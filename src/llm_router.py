"""Shared, provider-agnostic LLM call layer. Every LLM call site in the
pipeline (entity_extraction.py, entity_resolution.py, narrator.py,
v2/relevance_gate.py) routes through here instead of owning its own
Anthropic/Google client.

Two entrypoints:
  - call_tool(): structured tool/function-calling, returns a plain dict
    (the tool's input arguments), or {} if every model in the chain failed.
  - call_text(): plain text completion, returns a string, or "" if every
    model in the chain failed.

Both take a `task` name (a key into config.LLM_TASK_MODELS) and walk that
task's ordered (provider, model) fallback chain, trying each in turn until
one succeeds. This is what makes an account-wide outage on one provider
(e.g. the Anthropic usage-cap lockout seen 2026-08) degrade a run instead
of failing every call outright -- the chain's last resort is always a
different vendor, not just a different model from the same one.

Tool schemas are written once, in a single JSON-schema-shaped dict (the
same shape Anthropic's `input_schema` already uses), and translated to
Gemini's `types.Schema` format internally via _to_gemini_schema -- callers
never need to know which provider actually served a given call.

Cost accounting is provider-aware on purpose: Gemini's "thinking" models
(not gemini-3.5-flash-lite, which has none) bill thinking tokens as output
but report them in a *separate* usage field (`thoughts_token_count`) from
`candidates_token_count`. A cost calc that only reads candidates_token_count
silently undercounts -- confirmed empirically this build (see chat: a
trivial "Say OK." prompt to gemini-3.6-flash used 68 thinking tokens, zero
of which showed up in candidates_token_count). _gemini_output_tokens below
sums both defensively so this can't recur if a future task chain ever
points at a thinking-capable Gemini model.
"""

import sys

from anthropic import Anthropic
from dotenv import load_dotenv
from google import genai
from google.genai import types

import config
import cost_tracker

load_dotenv()

_anthropic_client: Anthropic | None = None
_gemini_client: genai.Client | None = None


def _get_anthropic_client() -> Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic()
    return _anthropic_client


def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client()
    return _gemini_client


def _cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = config.LLM_PRICING.get(model)
    if rates is None:
        return 0.0
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000


def _gemini_output_tokens(usage) -> int:
    """candidates_token_count plus any (separately-reported) thinking
    tokens -- see module docstring. Both default to 0/None on models
    without thinking output, so this is a safe no-op there."""
    candidates = getattr(usage, "candidates_token_count", 0) or 0
    thoughts = getattr(usage, "thoughts_token_count", 0) or 0
    return candidates + thoughts


def _to_gemini_schema(schema: dict) -> types.Schema:
    """Translates one canonical JSON-schema-shaped dict (Anthropic's
    input_schema format) into Gemini's types.Schema, recursively. Handles
    the one real divergence seen in this codebase's existing schemas:
    JSON-schema's `"type": ["string", "null"]` union form (entity_resolution.py's
    matched_canonical_id) becomes `type="STRING", nullable=True`."""
    kwargs: dict = {}

    json_type = schema.get("type")
    if isinstance(json_type, list):
        non_null = [t for t in json_type if t != "null"]
        if non_null:
            kwargs["type"] = non_null[0].upper()
        if "null" in json_type:
            kwargs["nullable"] = True
    elif json_type:
        kwargs["type"] = json_type.upper()

    if "description" in schema:
        kwargs["description"] = schema["description"]
    if "enum" in schema:
        kwargs["enum"] = schema["enum"]
    if "required" in schema:
        kwargs["required"] = schema["required"]
    if "properties" in schema:
        kwargs["properties"] = {k: _to_gemini_schema(v) for k, v in schema["properties"].items()}
    if "items" in schema:
        kwargs["items"] = _to_gemini_schema(schema["items"])

    return types.Schema(**kwargs)


def _call_tool_anthropic(model, system_prompt, user_content, tool_name, tool_description, input_schema, max_tokens):
    response = _get_anthropic_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        tools=[{"name": tool_name, "description": tool_description, "input_schema": input_schema}],
        tool_choice={"type": "tool", "name": tool_name},
        messages=[{"role": "user", "content": user_content}],
    )
    result = {}
    for block in response.content:
        if block.type == "tool_use" and block.name == tool_name:
            result = dict(block.input)
    return result, response.usage.input_tokens, response.usage.output_tokens


def _call_tool_gemini(model, system_prompt, user_content, tool_name, tool_description, input_schema, max_tokens):
    tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=tool_name, description=tool_description, parameters=_to_gemini_schema(input_schema)
            )
        ]
    )
    response = _get_gemini_client().models.generate_content(
        model=model,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
            tools=[tool],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="ANY", allowed_function_names=[tool_name])
            ),
        ),
    )
    result = {}
    candidate = response.candidates[0] if response.candidates else None
    if candidate and candidate.content and candidate.content.parts:
        for part in candidate.content.parts:
            if part.function_call and part.function_call.name == tool_name:
                result = dict(part.function_call.args)
    usage = response.usage_metadata
    return result, usage.prompt_token_count, _gemini_output_tokens(usage)


def _call_text_anthropic(model, system_prompt, user_content, max_tokens):
    response = _get_anthropic_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return text, response.usage.input_tokens, response.usage.output_tokens


def _call_text_gemini(model, system_prompt, user_content, max_tokens):
    response = _get_gemini_client().models.generate_content(
        model=model,
        contents=user_content,
        config=types.GenerateContentConfig(system_instruction=system_prompt, max_output_tokens=max_tokens),
    )
    text = (response.text or "").strip()
    usage = response.usage_metadata
    return text, usage.prompt_token_count, _gemini_output_tokens(usage)


def _walk_chain(chain: list[tuple[str, str]], task: str, attempt_fn, empty_result):
    """Shared fallback-chain logic for call_tool/call_text. `chain` is an
    ordered list of (provider, model) -- passed in explicitly (not looked
    up from config here) so this is unit-testable with a fake chain, no
    config/network dependency. `attempt_fn(provider, model)` must return
    (result, input_tokens, output_tokens) or raise. Records cost/fallback
    state via cost_tracker on every successful attempt."""
    for position, (provider, model) in enumerate(chain):
        fell_back = position > 0
        try:
            result, input_tokens, output_tokens = attempt_fn(provider, model)
        except Exception as e:
            print(f"[llm_router] {task}: {provider}/{model} failed ({e}); trying next in chain", file=sys.stderr)
            continue

        cost_tracker.record_llm_call(
            input_tokens, output_tokens, _cost(model, input_tokens, output_tokens), provider, model, fell_back
        )
        if fell_back:
            print(f"[llm_router] {task}: served by fallback {provider}/{model}", file=sys.stderr)
        return result

    print(f"[llm_router] {task}: every model in the chain failed", file=sys.stderr)
    return empty_result


def call_tool(
    task: str,
    system_prompt: str,
    user_content: str,
    tool_name: str,
    tool_description: str,
    input_schema: dict,
    max_tokens: int = 1024,
) -> dict:
    def attempt(provider, model):
        if provider == config.PROVIDER_ANTHROPIC:
            return _call_tool_anthropic(
                model, system_prompt, user_content, tool_name, tool_description, input_schema, max_tokens
            )
        if provider == config.PROVIDER_GOOGLE:
            return _call_tool_gemini(
                model, system_prompt, user_content, tool_name, tool_description, input_schema, max_tokens
            )
        raise ValueError(f"unknown provider {provider!r}")

    return _walk_chain(config.LLM_TASK_MODELS[task], task, attempt, empty_result={})


def call_text(task: str, system_prompt: str, user_content: str, max_tokens: int = 1024) -> str:
    def attempt(provider, model):
        if provider == config.PROVIDER_ANTHROPIC:
            return _call_text_anthropic(model, system_prompt, user_content, max_tokens)
        if provider == config.PROVIDER_GOOGLE:
            return _call_text_gemini(model, system_prompt, user_content, max_tokens)
        raise ValueError(f"unknown provider {provider!r}")

    return _walk_chain(config.LLM_TASK_MODELS[task], task, attempt, empty_result="")

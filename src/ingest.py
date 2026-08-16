"""Parses data/{servicenow,jira,gitrepo,confluence}.txt into chunks and
loads them into local persistent ChromaDB collections.

Idempotent: wipes and rebuilds all four collections on every run, since the
source files are a static test fixture rather than a live feed.
"""

import json
import re
from pathlib import Path

import chromadb

import config
from embeddings import get_embedding_function

DATA_DIR = Path(__file__).parent.parent / "data"

RECORD_START_KEY = {
    "servicenow": "INCIDENT",
    "jira": "ISSUE",
    "gitrepo": "PULL REQUEST",
    "confluence": "PAGE",
    "slack": "THREAD",
}
DOC_TYPE = {
    "servicenow": "incident",
    "jira": "issue",
    "gitrepo": "pull_request",
    "confluence": "wiki_page",
    "slack": "slack_thread",
}
PEOPLE_FIELDS = ["ASSIGNED TO", "ASSIGNEE", "AUTHOR", "REVIEWER", "PARTICIPANTS"]
RELATED_FIELDS = [
    "RELATED WORK",
    "RELATED INCIDENT",
    "LINKED PULL REQUEST",
    "LINKED TICKET",
    "RELATED",
]
ID_PATTERN = re.compile(r"\bINC\d+\b|\bPROJ-\d+\b|\bPR-\d+\b")
SECTION_PATTERN = re.compile(r"^SECTION\s+\d+\s*—.*$", re.MULTILINE)
HEADER_LINE = re.compile(r"^([A-Z][A-Z /]*[A-Z]):\s?(.*)$")


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def split_records(raw_text: str) -> list[str]:
    """Records in these exports are separated by a line of only '=' chars."""
    blocks = re.split(r"^=+$", raw_text, flags=re.MULTILINE)
    return [b.strip("\n") for b in blocks if b.strip()]


def parse_header(block: str) -> tuple[dict, str]:
    """Split a record block into (header_fields, body_text) at the '---' rule."""
    lines = block.splitlines()
    header_lines = []
    body_start = len(lines)
    for i, line in enumerate(lines):
        if re.match(r"^-+$", line.strip()):
            body_start = i + 1
            break
        header_lines.append(line)

    fields: dict[str, str] = {}
    last_key = None
    for line in header_lines:
        m = HEADER_LINE.match(line)
        if m:
            key, value = m.group(1).strip(), m.group(2).strip()
            fields[key] = value
            last_key = key
        elif last_key and line.strip():
            fields[last_key] += " " + line.strip()

    body = "\n".join(lines[body_start:]).strip()
    return fields, body


def extract_related_ids(fields: dict) -> list[str]:
    ids = set()
    for key in RELATED_FIELDS:
        if key in fields:
            ids.update(ID_PATTERN.findall(fields[key]))
    return sorted(ids)


def extract_people(fields: dict) -> dict:
    people = {}
    for key in PEOPLE_FIELDS:
        if key in fields:
            people[key.lower().replace(" ", "_")] = fields[key]
    return people


def build_chunks_for_record(source_system: str, fields: dict, body: str) -> list[dict]:
    doc_id_key = RECORD_START_KEY[source_system]
    doc_id_raw = fields[doc_id_key]

    if source_system == "confluence":
        doc_id = slugify(doc_id_raw)
        title = doc_id_raw
        status = ""
    elif source_system == "slack":
        # doc_id_raw is a channel name (e.g. "#eng-platform"), which repeats
        # across many threads -- channel + date is the actual unique key in
        # this export (verified: no two threads share both).
        title = fields.get("TOPIC", doc_id_raw)
        doc_id = slugify(f"{doc_id_raw}-{fields.get('DATE', '')}")
        status = ""
    else:
        doc_id = doc_id_raw
        title = fields.get("TITLE", doc_id_raw)
        status = fields.get("STATUS", "")

    # Deliberately lean: just doc_type/id/title, not the full header block.
    # An earlier attempt embedded the full header (STATUS, PRIORITY,
    # ASSIGNED TO, dates, ...) to fix a narrator gap (see build_phase_1.md
    # addendum) but that made every document's embedding more similar to
    # every other one via shared boilerplate fields, wrecking the
    # calibrated MAX_SEARCH_DISTANCE separation between true and false
    # matches. STATUS and friends are still available via metadata
    # (raw_fields, status) for anything that needs them without touching
    # what gets embedded.
    header_summary = f"{DOC_TYPE[source_system].upper()}: {doc_id} — {title}"
    base_metadata = {
        "source_system": source_system,
        "doc_id": doc_id,
        "doc_type": DOC_TYPE[source_system],
        "title": title,
        "status": status,
        "people": json.dumps(extract_people(fields)),
        "explicit_related_ids": json.dumps(extract_related_ids(fields)),
        "raw_fields": json.dumps(fields),
    }

    section_matches = list(SECTION_PATTERN.finditer(body))
    if len(section_matches) >= 2:
        chunks = []
        for idx, m in enumerate(section_matches):
            start = m.start()
            end = (
                section_matches[idx + 1].start()
                if idx + 1 < len(section_matches)
                else len(body)
            )
            section_text = body[start:end].strip()
            chunks.append(
                {
                    **base_metadata,
                    "chunk_id": f"{source_system}:{doc_id}:{idx}",
                    "chunk_index": idx,
                    "text": f"{header_summary}\n\n{section_text}",
                }
            )
        return chunks

    return [
        {
            **base_metadata,
            "chunk_id": f"{source_system}:{doc_id}:0",
            "chunk_index": 0,
            "text": f"{header_summary}\n\n{body}",
        }
    ]


def load_source_file(source_system: str) -> list[dict]:
    path = DATA_DIR / f"{source_system}.txt"
    raw_text = path.read_text()
    start_key = RECORD_START_KEY[source_system]

    chunks = []
    for block in split_records(raw_text):
        if not block.lstrip().startswith(f"{start_key}:"):
            continue  # file preamble / export-scope banner, not a record
        fields, body = parse_header(block)
        chunks.extend(build_chunks_for_record(source_system, fields, body))
    return chunks


def main():
    client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    embedding_function = get_embedding_function()

    for source_system in config.SOURCE_SYSTEMS:
        try:
            client.delete_collection(source_system)
        except Exception:
            pass
        collection = client.create_collection(
            name=source_system,
            embedding_function=embedding_function,
        )

        chunks = load_source_file(source_system)
        collection.add(
            ids=[c["chunk_id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[
                {k: v for k, v in c.items() if k not in ("text", "chunk_id")}
                for c in chunks
            ],
        )
        print(f"{source_system}: loaded {len(chunks)} chunks into collection '{source_system}'")


if __name__ == "__main__":
    main()

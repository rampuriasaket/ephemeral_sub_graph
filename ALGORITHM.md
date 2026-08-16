# How ESG works

This describes the traversal strategy implemented in `src/v2/`. It's written for
someone trying to understand the *approach*, not as a spec for modifying the code —
for that, read the code itself, starting at `src/v2/discovery_loop_v2.py`.

## The core idea

Given a question, ESG builds a small graph connecting exactly the documents relevant
to answering it, by starting from the question and repeatedly asking "what does this
lead to?" — following entity names and document content outward, one step at a time,
until it runs out of genuinely new leads or hits a budget. The graph is built fresh
for that one question and discarded once answered. Nothing is kept between questions.

## The traversal loop

**1. Seed.** Extract entities directly from the question's text (e.g. a service name,
a person, a ticket ID) and run one broad search across every connected system on the
raw question text. Whatever that broad search finds is accepted immediately — no
filtering — since this is the one deliberately generous step: without an anchor yet,
being too strict here would throw away real connections on vague questions.

**2. Work a shared queue.** Every discovery — entities and document chunks alike —
goes into one FIFO queue, popped in the order it was found. There's no priority
scoring and nothing is retried in a different order later; whatever comes out of the
queue first gets processed first.

**3. Popping an entity** (e.g. a service name or ticket ID) means searching for it by
name or exact ID across every connected system. A candidate has to actually contain
that entity (in its text, or in a structured "related-to" field) to survive this
first, free mechanical check — no LLM call yet.

**4. Popping a document chunk** means running a semantic search on that chunk's own
content across every system, to find other documents that are conceptually related
even if they share no explicit identifier or name.

**5. Every survivor of the mechanical check goes through two more gates, always in
this order:**
   - **Identity check.** Is this actually a new document, or one already in the
     graph (exact ID match), or a near-duplicate of one (high embedding similarity)?
     Matches here are merged in for free — no LLM call, no new node.
   - **Relevance gate.** For anything genuinely new, one batched LLM call judges
     whether it's really connected to the investigation — given the original
     question, the full chain of entities/documents that led here (not just the
     immediate parent, so a plausible-looking two-hop drift gets caught), and the
     candidate's own text. The gate has to give a one-sentence reason for every
     accept or reject; there's no silent default in either direction. One
     exception: a candidate whose only connection to the searched entity is a
     citation the *source document itself* declared in a structured "related-to"
     field (not free text) skips the gate and is accepted directly — the source
     has already asserted the relationship, so there's nothing left to judge.

**6. Accepting** a document means: add it to the graph, extract its entities (this
happens exactly once, right when it's accepted — never again if it's revisited
later), push any new entities onto the queue, and push the document itself onto the
queue so its own content becomes a future search.

**7. Stop** when any of these happens:
   - the queue is empty (nothing left to follow)
   - 20 entity-searches or 20 document-searches have been processed (each gets one
     one-time 25% extension — to 25 — if there's a real backlog still waiting when
     the cap hits; that extension can only fire once per run)
   - both search budgets (15 calls per system, tracked separately for entity
     searches vs. document searches) are exhausted at the same time

Once stopped, the accumulated graph is handed to a narrator LLM call that composes
the final answer, grounded only in what's actually in the graph — nothing it wasn't
given.

## Why a few things are built the way they are

**Two independent budgets, not one shared one.** Entity-driven and document-driven
search are tracked and capped separately, so a question that needs a lot of one kind
of search can't silently starve the other.

**The relevance gate sees the whole chain, not just the last hop.** Judging a
candidate only against its immediate parent lets a chain of individually-plausible
hops drift somewhere irrelevant two or three steps later, each step looking
reasonable in isolation. Seeing the full path back to the question catches that.

**Seed search stays deliberately ungated.** An earlier version routed seed results
through the same relevance gate as everything else. On vague, broad questions with no
concrete entity to anchor on, that made the gate reject almost everything, producing
an empty answer that a much simpler baseline still handled fine. The seed step is the
one place ESG trades some precision for making sure it doesn't come back empty-handed
on exactly the questions where a sharp anchor doesn't exist yet.

**Nothing is ever removed once accepted.** A document that makes it into the graph
stays there for the rest of the run. The relevance gate's job is to be right on the
way in, not to prune mistakes out afterward.

## What it costs

The tradeoff for this thoroughness is cost and latency: ESG runs many more search and
LLM calls than a single-shot retrieval baseline, translating to roughly 30x the
per-question cost and about 17–18x the wall-clock time, averaged across the evaluation
set (see `results/run_1/output_b_paper_table.md` for measured figures). The payoff, measured
against a 35-question evaluation set, is materially higher recall — particularly on
questions where the connection between documents has no shared identifier or name to
chase, which a cheaper baseline structurally cannot reach no matter how many
follow-up hops it's given.

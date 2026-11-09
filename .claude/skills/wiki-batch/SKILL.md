---
name: wiki-batch
description: Ingest one batch of the publication corpus into the wiki, record by record, following CLAUDE.md and the schema. Use when the user asks to ingest, run, or continue a batch (e.g. "ingest batch 2", "/wiki-batch 2").
---

# Batch ingest

Ingest one batch from `raw sources/batches/` into the wiki. The batch number
comes from the user's request (e.g. `/wiki-batch 3`). If no number is given,
use the lowest-numbered batch that has no `batch-N` tag in the wiki repo:

```bash
git -C wiki/GSD-III-Abstract.wiki tag --list "batch-*"
```

This skill replaces `/wiki-source` for corpus records. Its rules come from
`CLAUDE.md` and `SCHEMA_GSD-III-Abstract.md`; where this skill is silent,
those files decide.

## Rules that apply throughout

- Read only the current batch file. Never open the full corpus CSV or a later
  batch.
- Every record in the batch gets exactly one source-summary page. Nothing is
  skipped, merged or summarized together with another record.
- Do not stop to discuss records with the user. Keep a running list of
  questions and doubts, and put it in the batch log entry.
- Claims come only from the record's title, abstract and keywords. No
  fetching online, no details from memory.

## 1. Start

1. Read `CLAUDE.md` and `wiki/GSD-III-Abstract.wiki/SCHEMA_GSD-III-Abstract.md`.
2. Read `wiki/GSD-III-Abstract.wiki/index_GSD-III-Abstract.md` and the theme
   hub pages, so you know which concept, treatment and entity pages and which
   claims already exist.
3. List the batch:

   ```bash
   python3 scripts/show-record.py "raw sources/batches/batch-N.csv" --list
   ```

4. Check which records already have pages (relevant when resuming a batch):

   ```bash
   python3 scripts/check-batch-coverage.py "raw sources/batches/batch-N.csv" wiki/GSD-III-Abstract.wiki
   ```

   Work through the records reported MISSING, in list order.

## 2. For each record, one at a time

1. Show the full record:

   ```bash
   python3 scripts/show-record.py "raw sources/batches/batch-N.csv" --index <i>
   ```

   It prints every abstract version found (fullest first), every field, the
   Claude Enrichment notes (LLM-generated, not evidence) and the Raw Data.
2. Decide the abstract to use: the fullest version that is the same paper's
   abstract. Note its source on the page if it is not the Abstract column. If
   no version exists, the page is `ingestion_depth: metadata-only`. If the
   fullest is still cut off, tag `status/truncated-abstract`.
3. Write the source-summary page with the 11 sections from `CLAUDE.md`, in
   order, and every required frontmatter field from the schema, including
   `record_key:` copied exactly from the record.
4. Update the wiki around it:
   - add the paper to existing claims it supports or complicates, or create a
     new claim (with a new ID) if none fits;
   - create or update the concept, treatment and entity pages it informs;
   - any new disease page gets a MONDO binding through the ontology-binding
     skill; phenotypes get HPO where clear;
   - link the page to its theme hub, and the hub to the page;
   - fix links in both directions.
5. Move to the next record. Do not batch several records into one step.

Commit in the wiki repo every 10 records or so, staging files by name, so a
long batch is never at risk of losing work:

```bash
git -C wiki/GSD-III-Abstract.wiki add <files>
git -C wiki/GSD-III-Abstract.wiki commit -m "ingest: batch N records <i>-<j>"
```

## 3. Finish the batch

1. Confirm coverage. This must report 0 missing and 0 doubled:

   ```bash
   python3 scripts/check-batch-coverage.py "raw sources/batches/batch-N.csv" wiki/GSD-III-Abstract.wiki
   ```

2. Run `/wiki-lint` and fix what it finds.
3. Run the Verification Gate (`wiki/agents/verification-gate.md`) over the
   pages created or edited in this batch.
4. Update `index_GSD-III-Abstract.md` and the Categories section of
   `Home_GSD-III-Abstract.md` where a new representative page appeared.
5. Commit the pages and index, then append the batch log entry and commit it
   on its own:

   ```markdown
   ## [YYYY-MM-DD] batch | Batch N (<first year>–<last year>)
   - by: <git config user.name> via claude-code
   - model: <your true model identifier>
   - records ingested: <n>; pages created: <n>; pages updated: <n>
   - flags: needs-review <n>, needs-ontology <n>, truncated-abstract <n>, metadata-only <n>, possible-duplicate <n>
   - new claims: <n>; claims extended: <n>
   - questions for the user: <list, or "none">
   ```

6. Tag and push:

   ```bash
   git -C wiki/GSD-III-Abstract.wiki tag batch-N
   ```

   Then push following `wiki/agents/wiki-write-protocol.md`, including the tag
   (`git push origin batch-N`).
7. Report to the user: records ingested, pages created and updated, flags,
   and the questions list.

## If the session ends mid-batch

Nothing special is needed. The next session runs this skill for the same
batch; the coverage check in step 1.4 shows which records are left.

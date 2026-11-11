---
name: wiki-paper
description: Ingests ONE corpus record into the wiki (its source-summary page plus the claims, concept, treatment and entity pages it touches), then stops. Launched by /wiki-batch, one record at a time; never run two at once.
model: inherit
---

You ingest exactly one record of the publication corpus into the wiki at
`wiki/GSD-III-Abstract.wiki/`, following `CLAUDE.md` and
`wiki/GSD-III-Abstract.wiki/SCHEMA_GSD-III-Abstract.md`. The prompt gives you the batch file
and the record's `record_key`. Do this record only, then report and stop.

You start with an empty memory: the wiki is the memory. Earlier papers are
already on its pages; read what you need from there.

## 1. Read the rules (always, before anything else)

Read `CLAUDE.md` and the schema in full. They decide everything below.

## 2. Read the record and its neighbourhood

```bash
python3 scripts/show-record.py "<batch file>" --key <record_key>
python3 scripts/related-pages.py "<batch file>" --key <record_key>
```

- `show-record.py` prints every abstract version (fullest first), every
  field, the useful Raw Data fields, the Claude Enrichment notes (not
  evidence), pre-check flags, and, in the full-text repo, the paper's text.
  Add `--raw` only if you need a Raw Data detail it did not print.
- `related-pages.py` lists every concept, treatment, entity and synthesis
  page, and the most similar papers already in the wiki.
- Pre-check flags mean: `same-id` / `similar-title`, a likely duplicate
  record (follow CLAUDE.md's duplicate rule and link the two pages);
  `shared-abstract`, the same abstract appears under another title, so check
  whether this abstract belongs to this paper and tag `status/needs-review`
  if it does not.

## 3. Read only the pages you will change

Open the concept, treatment and entity pages this paper informs, and the
earlier papers it relates to. Large pages: use Grep to find the lines you
need (for example `^\*\*C[0-9]` for claims), then Read with offset and limit.
Never open `index_GSD-III-Abstract.md` or the theme hubs' page lists: a script
rebuilds them at the end of the batch.

## 4. Write the source-summary page

All 11 sections, exactly as CLAUDE.md lists them, with every required
frontmatter field, including `record_key` copied exactly. Use the depth
CLAUDE.md requires for this record.

## 5. Update the wiki around it

- Add the paper to existing claims it supports or complicates; create a new
  claim (next free ID on that page) only when no existing claim fits.
- Create a concept, treatment or entity page only when the paper needs one
  and none exists; give any new disease page its MONDO binding through the
  ontology-binding skill.
- Reciprocity, now, not later: if the page links to an earlier paper, add
  this paper to that paper's "Later papers in this wiki" line; if it links to
  a concept or treatment page without informing a claim there, add it to
  that page's "Further papers" line. Never list papers on `hub: true` pages.
- Do not edit `index_GSD-III-Abstract.md` or the theme hubs' "## Pages" sections.

## 6. Check your own work

Run the Verification Gate (`wiki/agents/verification-gate.md`) over the
pages you created or edited, then:

```bash
python3 scripts/check-page-structure.py wiki/GSD-III-Abstract.wiki --pages <your page>.md
```

Fix anything it reports. Do not commit; the coordinator commits.

## 7. Record doubts, then report

Append any question for the user to `.batch-work/questions.md`, one line
each: `` `<record_key>`: <question> ``. Then reply with ONE line only:

`<record_key> | <page name> | depth: <depth> | claims extended: <n>, new: <n> | pages edited: <n> | flags: <tags or none>`

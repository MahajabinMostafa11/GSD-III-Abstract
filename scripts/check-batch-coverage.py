#!/usr/bin/env python3
"""Check that every record in a batch has exactly one source-summary page.

Reads `record_key:` from the frontmatter of every page in the wiki and
compares it with the batch file.

Usage:
    python3 scripts/check-batch-coverage.py "raw sources/batches/batch-1.csv" wiki/GSD-III-Abstract.wiki

Exit code 0 only when every record has exactly one page.

Requires: pip3 install pandas
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

KEY_LINE = re.compile(r'^record_key:\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)


def page_keys(wiki_dir):
    keys = defaultdict(list)
    for page in Path(wiki_dir).glob("*.md"):
        text = page.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            continue
        frontmatter = text.split("---", 2)[1] if text.count("---") >= 2 else ""
        for key in KEY_LINE.findall(frontmatter):
            keys[key.strip()].append(page.name)
    return keys


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    batch = pd.read_csv(sys.argv[1], dtype=str, keep_default_na=False)
    keys = page_keys(sys.argv[2])

    missing, doubled = [], []
    for row in batch.to_dict("records"):
        pages = keys.get(row["record_key"], [])
        if not pages:
            missing.append(row)
        elif len(pages) > 1:
            doubled.append((row, pages))

    print(f"Batch: {sys.argv[1]}")
    print(f"Records: {len(batch)}   with a page: {len(batch) - len(missing)}   "
          f"missing: {len(missing)}   more than one page: {len(doubled)}")
    for row in missing:
        print(f"  MISSING  {row['record_key']}  {row.get('Publication Year', '')}  {row.get('Title', '')[:80]}")
    for row, pages in doubled:
        print(f"  DOUBLED  {row['record_key']}  -> {', '.join(pages)}")
    sys.exit(0 if not missing and not doubled else 1)


if __name__ == "__main__":
    main()

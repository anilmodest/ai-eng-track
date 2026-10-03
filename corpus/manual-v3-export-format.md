---
product: Kestrel Data Runner
version: v3
section: Data
---

# Export format (Kestrel v3)

An export writes the result of a run to a file.

## Formats

CSV or NDJSON, chosen with `KESTREL_EXPORT_FORMAT`, which defaults to `csv`. The CSV separator is a comma and cannot be changed.

## Encoding

UTF-8 **without a byte-order mark**. Spreadsheet software that relied on the mark to detect the encoding may now show accented characters incorrectly on first open.

## Quoting

**Every** field is quoted, whether or not it contains a separator, so a file can be compared line by line between runs.

## Empty values

An empty string is written as `""` and a missing value as nothing at all, so the two can be told apart.

## File naming

`<pipeline>-<YYYYMMDD>-<run-id>.csv` or `.ndjson` in the export directory. The run id in the name means a second run on the same day no longer overwrites the first.

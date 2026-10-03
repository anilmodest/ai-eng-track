---
product: Kestrel Data Runner
version: v2
section: Data
---

# Export format (Kestrel v2)

An export writes the result of a run to a file.

## Formats

CSV only. The separator is a comma and cannot be changed.

## Encoding

UTF-8 **with a byte-order mark**, so that the file opens correctly in spreadsheet software without extra steps.

## Quoting

A field is quoted only when it contains a comma, a quotation mark or a newline.

## Empty values

An empty field is written as nothing at all between two separators. There is no way to tell an empty string from a missing value.

## File naming

`<pipeline>-<YYYYMMDD>.csv` in the export directory.

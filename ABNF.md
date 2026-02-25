# AICL v1.0 ABNF (Draft)

This ABNF describes the textual surface form of a single AICL message.
It is intentionally conservative and ASCII-first.

## Grammar

```abnf
message        = "MSG{" LF fields LF "}"
fields         = field *(LF field)
field          = key ":" value

key            = "A" / "I" / "O" / "T" / "G" / "C" / "K" / "U" / "P" /
                 "R" / "Q" / "D" / "V" / "M" / "H" / "X" / "S"

value          = scalar / list / object
scalar         = 1*(safechar)
safechar       = ALPHA / DIGIT / "_" / "-" / "." / ":" / "/" / "<" / ">" /
                 "=" / "+" / "?" / "!" / "," / ";" / SP / DQUOTE / "'" / "(" / ")"

list           = "[" [list-item *("," list-item)] "]"
list-item      = value

object         = "{" [pair *("," pair)] "}"
pair           = obj-key "=" obj-val
obj-key        = 1*(ALPHA / DIGIT / "_" / "-" / ".")
obj-val        = 1*(safechar / "[" / "]" / "{" / "}")

LF             = %x0A
SP             = %x20
DQUOTE         = %x22
ALPHA          = %x41-5A / %x61-7A
DIGIT          = %x30-39
```

## Canonical Field Order

Implementations should emit fields in this order:

`A I O T G C K U P R Q D V M H X S`

## Semantic Rules Outside ABNF

- `I`, `O`, `S` are required.
- `S.conf` must be in `0.00..1.00`.
- `S.trace` must be unique per workflow.
- `I` must be one of the standard intents.
- Unknown fields should be ignored unless strict mode is enabled.


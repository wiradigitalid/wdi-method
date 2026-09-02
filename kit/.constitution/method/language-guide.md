---
status: Accepted
---

# Language Guide

**Loaded when:** naming anything — a code identifier, a database field, a file, a folder.

Which language a name is written in, and nothing else. Case style → `../project/codebase-conventions-guide.md`;
legal characters → `structure-guide.md`; the right domain word → `.control/product-glossary.md`.

## Code MUST be English

Identifiers, code files and folders, database schema (tables, columns, indexes, constraints, enum
values, migrations), and machine-facing keys (API routes and fields, config keys, environment
variables, event names, CSS classes, design tokens). An identifier sits between English keywords and
English error messages, and a second language there is where misreadings happen.

Prose **inside** code — comments, commit messages, log messages — is not a name and is not governed
here.

**One exception:** an Indonesian administrative or legal thing — `kelurahan`, `npwp`. All three MUST
hold: it already has an entry in `.control/product-glossary.md`; only the domain noun is Indonesian
(`kelurahanCode`, MUST NOT be `kodeKelurahan`); one ASCII spelling in schema, API, and code alike. An
English word being longer or less familiar does not qualify.

## Visitor-facing URL paths MUST be English

The path a person types or copies is a name. One exception: `/bisnis` and `/{code}/bisnis` — that
surface is named in Indonesian in the product, and `/business` would be a second name for the same
thing.

## Two settings, and everything else is not a choice

The product picks two things, both in `.control/registry/index.yaml` under `policy:`, and both
defaulting to English:

| Setting | Governs |
|---|---|
| `doc_language` | The **prose** of working documents in `.what/` · `.how/` · `.control/` |
| `doc_filename_language` | The **slug** part of a document filename |

**Both are free text, not a list of codes.** `English`, `Bahasa Indonesia`, `id`, `Indonesia` — write
whatever names the language, because what reads the value is a **model**, and a model does not need a
lookup table. Fencing it into two codes would only make the owner translate their intent into the
installer's vocabulary first, and nothing is bought with that. The one value refused is an empty one.

Nothing else about language is a setting, and a skill MUST NOT ask:

- **Method terminology** — `DEC` `SRS` `SDD` `UC` `FR` `AD`, the gate names, the values of `mode` and
  `risk_accepted`. One thing, one name, in every repo the method is installed in.
- **Machine-facing markers** — `[NEEDS CONFIRMATION]` `[MISSING]` `[ASSUMED]` `[PARTIAL]`, and the
  `yes`/`no` in a `critical` column. They are matched by scripts, which makes them keys rather than
  prose, and the rule above on registry values already covers keys.
- **Code identifiers, database columns, config keys** — §Code MUST be English, above.

**A corpus written before these settings existed MUST NOT be migrated for them.** The readers accept
both languages — `validate.py` matches `yes|ya`, and `high-risk-named`'s keyword set is the union of both — so an
existing document keeps working and a new one is written in the chosen language. Rewriting a hundred
documents so a regex looks tidier is a cost with no buyer.

## Document filenames — the slug follows the setting

Three parts are **not** free, because the method reads them: layer and slot folder names, document code
prefixes (`DEC-`, `FR-`), and a `YYYY-MM-DD` prefix. Those are always English and always as written.
The slug after the code follows `doc_filename_language`.

Files under `.constitution/` MUST be English whatever the settings say — they are agent instructions,
and they travel to every repo through the `wdi-method` package.

## A wrong name MUST NOT be fixed inside an unrelated change

A rename reaches the schema, the API, and every caller. It gets a change of its own, or a ratified
row in `../project/codebase-brownfield-guide.md`. A **new** name MUST NOT copy a wrong neighbour.
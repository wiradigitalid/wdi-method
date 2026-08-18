---
status: Accepted
---

# Language Guide

**Loaded when:** naming anything — a code identifier, a database field, a file, a folder.

Which language a name is written in, and nothing else. Case style → `codebase/conventions-guide.md`;
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

## Document filenames MAY be Indonesian

Three parts are not free, because the method reads them: layer and slot folder names, document code
prefixes (`DEC-`, `FR-`), and a `YYYY-MM-DD` prefix. Files under `.constitution/` MUST be English —
they are agent instructions.

## A wrong name MUST NOT be fixed inside an unrelated change

A rename reaches the schema, the API, and every caller. It gets a change of its own, or a ratified
row in `codebase/brownfield-guide.md`. A **new** name MUST NOT copy a wrong neighbour.
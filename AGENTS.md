# Agent Rules — wdi-method

Rules for an agent working **on this package**. For an agent working on a product repo that has the
method installed, the rules are in that repo's own `AGENTS.md`.

Keywords MUST / MUST NOT / SHOULD / MAY are normative.

## Versioning — the one hard boundary

| Part | May an agent release it? |
|---|---|
| `npm version patch` | **Yes.** Do it as part of the change, and say so in the commit |
| `npm version minor` | **No.** Propose it; the maintainer releases it |
| `npm version major` | **No.** Same |

An agent MUST NOT run `npm version minor` or `npm version major`, and MUST NOT edit `version` in
`package.json` by hand to achieve the same thing.

The reason: this package **overwrites files** in repos that already hold months of work, and the version
number is the only signal a reader has for how carefully to read the diff. A minor released by whoever
happened to be working takes that signal away. `CONTRIBUTING.md` carries the same rule for humans.

An agent MUST NOT run `npm publish`. Publishing is irreversible after 72 hours and happens under the
maintainer's account.

## Language

Everything in this repository is **English** — the installer's interface included. The interface comes
from us, which is the same reason `.constitution/` and the fifteen wrappers are English.

What MAY be another language is the **working documents of a product**, and that is decided per repo by
`policy.doc_language`. This package MUST NOT assume an answer: a sentence like *"prose in this repo is
X"* inside `kit-overlay/` ships that assumption to every consumer.

## Where a change belongs

| Changing | Edit it | Reaches consumers via |
|---|---|---|
| A guide, template, script, or skill wrapper | a **product repo**, then `promote` | `kit/` |
| `bin/` `lib/` `tests/` `kit-overlay/` README | here, directly | the published package |
| `kit/.constitution/project/README.md` | here — `promote` skips that folder | `update`, seeded once |

A generic rule MUST NOT be authored here from imagination. Write it where it will be run, run it, then
promote it. `CONTRIBUTING.md` explains why.

## Before any commit that touches the kit

```bash
npm test
git grep -ilE "<client>|<product>" -- kit kit-overlay scaffold bin lib README.md
```

The second command MUST return nothing. This repository is public.

## Two things update MUST never do

Both were real defects, and both are now covered by tests:

- **Resurrect a folder a product retired.** On update, absence is a decision. `.work/` and
  `_bmad-output/prior-knowledge/` are seeded on first install only.
- **Overwrite a value the product already chose** — an initiative slug, a language, anything in
  `.constitution/project/`. A value only changes when somebody actually answers, and the run says which
  values it kept.

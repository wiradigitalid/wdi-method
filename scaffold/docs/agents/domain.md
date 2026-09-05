# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

**This repo does not use `CONTEXT.md`, `CONTEXT-MAP.md`, or `docs/adr/`, and none of them MUST be
created.** WDI Method already owns every home they would occupy, and a second home for the same fact is
drift rather than tidiness. `.constitution/method/constitution.md` Article 3 states it outright: this
method has no `docs/` layer for corpus or rules, and `wdi-reconcile` reports a root `CONTEXT.md` or a
`docs/adr/` as a finding against that article.

This file is seeded by `wdi-method` so the answer is right from the first install. `/setup-matt-pocock-skills`
would otherwise write its own default here — one that points at exactly the two paths above — and every
repo that ran it has had to hand-correct this file afterwards.

## Where each thing actually lives

| Looking for | Read |
|---|---|
| What a domain term means | `.control/product-glossary.md` |
| What is promised — a capability, an `FR`, a use case, a business rule | `.what/` |
| How it is built — the spine, C4, an inventory, an SDD, a contract | `.how/` |
| Why it is like this — a decision worth remembering | `.control/decisions/`, indexed by the generated decision table under `.control/generated/` |
| An architectural invariant | an `AD-N` in the architecture spine, under `.how/_platform/` |
| Which contexts exist and what each owns | `.control/registry/components.yaml` |
| Where code lives | `.control/structure-codebase.md` |
| Where documents live | `.control/structure-document.md` |

`AGENTS.md` § *The thing in your hand → its folder* is the short version of this table and is the
authority. Where this file and `AGENTS.md` disagree, `AGENTS.md` wins.

## A decision is a `DEC-`, never an ADR

`decision-guide.md` owns the shape, the one test that decides whether a decision is recorded at all, and
the `draft → accepted → applied` ladder. An ADR file under `docs/adr/` MUST NOT be written in its place:
the numbering is global and lives in `.control/registry/decisions.yaml`, and a decision recorded outside
it is invisible to `refs-resolve`, to the RTM, and to the generated decision table.

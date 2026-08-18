---
status: Accepted
---

# Constitution — {product}

Rewrite Articles 2 and 5 for the product this repo is. Article 1 cites
`.control/registry/index.yaml` — replace `{product}` there at G1, not here.
Articles 3, 4, 6, and 7 are the method and travel unchanged.

An agent working here MUST be able to act on the contents of this repo alone.

## Article 1 — Scope

This repo covers the product named at `product.name` in
`.control/registry/index.yaml`. One product, one repo. A second product MUST
get a repo of its own.

`product.client` in the same file names the client if there is one, and stays
empty if there is not. The product brief at G1 uses `product.name` as its
title. Neither this file nor the brief is a second source of the name.

An agent working here MUST NOT demand that sibling organisation repositories
be open in the same session.

## Article 2 — Content boundary, `.work/`, and cross-repo references

All three are governed by [`repo-guide.md`](repo-guide.md). Its rules MUST NOT be
repeated here — one rule, one place.

What is particular to this repo, and therefore lives here:

- Name any extra boundary this product has (a public-repo rule, a ban on `3p.md`,
  a `.work/` resting state). If there is none, delete this bullet list and the
  sentence above it.
- `3p.md` MUST NOT be created in a product repo. Operational engagement memory
  lives outside.

## Article 3 — Layers

The repo layout is governed by `corpus-guide.md` and mapped by
`.control/structure-document.md`. What MUST be known before opening either:

| Path | Role |
|---|---|
| `.constitution/` | Rules — how we work. `method/` holds the non-binding explanation of them |
| `.control/` | Control — what currently holds and what has been decided |
| `.what/` | What is promised |
| `.how/` | How it is built |
| `_bmad-output/` | Run workspace; committed, not curated |
| `.work/` | Scratch; committed, emptied when a task closes |
| *(application roots)* | Application code — name them in this row |

The method does not use a `docs/` layer for corpus or rules. A leftover `docs/`
folder is inventory to sort, not a second home.

## Article 4 — Lifecycle

Every `.constitution/` file MUST carry a `status:` frontmatter, and it MUST be one of five:

| Status | Means |
|---|---|
| `Accepted` | **Binds.** It MAY be cited as the reason to reject a change |
| `Reference` | **Explains, does not bind.** It MUST NOT be cited as the reason to reject a change, and MUST NOT be installed as `doc_standards` or `persistent_facts` |
| `Draft` | Not settled. Its contents MAY be read as guidance but MUST NOT be used to reject a change |
| `Superseded` | Replaced. It MUST name its replacement |
| `Cancelled` | Withdrawn without a replacement, and kept so nobody rewrites it |

**One exception, by construction:** a file in `document/templates/` MUST NOT carry a `status:` of its own.
A template's frontmatter is the *artifact's* frontmatter — it is copied into what the template produces —
so a status there would land in the artifact and mean something else entirely.

A missing header anywhere else is a **finding**, not an implicit anything.

`Reference` exists so that the *explanation* of a rule can live beside the rule without competing with it —
`method/` holds four such files. Where a `Reference` file and an `Accepted` one disagree, the `Accepted`
one wins, and the disagreement MUST be reported as a defect rather than resolved by preferring whichever was
opened first. A rule MUST NOT be born in a `Reference` file; when one is noticed there, it is stated as a
finding and written in the guide that owns it.

## Article 5 — The method arrives from WDI Method

This is the **consumer** article. Use it in every product repo.

`.constitution/` guides and templates (except this file's Articles 1, 2, and 5,
`codebase/*-guide.md`, and any extra file this repo added), the `wdi-*` skills,
and `_bmad/custom/*.toml` arrive from the public WDI Method package via
`npx wdi-method install` / `update`.

- A method file MUST NOT be invented or patched here to improve the method. If a
  rule is wrong, it is fixed in the WDI Method package, then brought here with
  `update`.
- `wdi-method update` MUST overwrite method files and MUST NOT touch `.what/`,
  `.how/`, `.control/` product state, this file's Articles 1–2 and 5,
  `codebase/*-guide.md` once `Accepted`, extra constitution files this repo
  added, or `_bmad/custom/*.user.toml`.
- A rule particular to this repo MUST be written out in full in this file or a
  sibling, and MUST NOT be replaced by a pointer into another repository.

A prefix in `.claude/skills/` names the **method**, not the owner: `bmad-*` is
BMad's, `wdi-*` is this method's.

## Article 6 — Decisions

A decision worth remembering is a `DEC-NNN`. Its shape, the one test that decides whether it is
recorded at all, global numbering, the `draft → accepted → applied` status ladder, and supersession
are governed by [`document/decision-guide.md`](document/decision-guide.md). Decisions live in
`.control/decisions/` and are registered in `.control/registry/decisions.yaml`.

Recording a decision is **not mandatory**, and one case is: a decision that contradicts or changes an
`AD-N`. The guide owns both halves and they MUST NOT be restated here.

The name ADR is retired, along with `layer:` and `component:` on a decision. `ADR-NNN` appearing in a
document frozen before that date is a retired alias for `DEC-NNN`, and those documents MUST NOT be
rewritten for the prefix. A course correction is a `DEC-` of `type: course-correction`.

## Article 7 — Non-technical facts

A non-technical fact that constrains what may be built, used, or promised — a domain now held, a
third-party account now active, the legal entity a screen must name, a date that locks scope — MUST
be recorded in `.control/project-non-technical-log.md`, and MUST NOT be scattered into a `DEC-`, a
PRD, or a code comment as though it were an engineering constraint.

That file states its own entry shape, its closed category list, and which facts belong to another
home instead. It MUST be written through the skill `wdi-log` intent `fact`, never by hand.

Two boundaries hold over it and MUST NOT be relaxed there:

- The content boundary in [`repo-guide.md`](repo-guide.md). This file is not an exemption from it;
  a commercial fact does not become admissible by being called non-technical.
- Article 2's ban on `3p.md`. Operational engagement memory stays outside this repo, and the log
  MUST NOT grow into a substitute for it.

It is control, not chronology. What happened on a given day is recovered from git by `wdi-report`;
what is recorded here is what still holds.

---
status: Accepted
---

# Constitution — {product}

Articles 1, 2, and 5. They are **yours**: seeded once at install, never overwritten by `update`, and
never carried into the package by `promote`. Rewrite Articles 2 and 5 for the product this repo is;
Article 1 needs no edit — it cites `product.name` in `.control/registry/index.yaml`.

The method's own articles — 3 Layers, 4 Lifecycle, 6 Decisions, 7 Non-technical facts — live in
[`../method/constitution.md`](../method/constitution.md) and are replaced on every update. The
numbering is shared across the two files and has gaps in each.

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

All three are governed by [`../method/repo-guide.md`](../method/repo-guide.md). Its rules MUST NOT be
repeated here — one rule, one place.

What is particular to this repo, and therefore lives here:

- Name any extra boundary this product has (a public-repo rule, a ban on `3p.md`,
  a `.work/` resting state). If there is none, delete this bullet list and the
  sentence above it.
- `3p.md` MUST NOT be created in a product repo. Operational engagement memory
  lives outside.

## Article 5 — The method arrives from WDI Method

This is the **consumer** article. Use it in every product repo.

Everything in `.constitution/method/`, the `wdi-*` skills, and
`_bmad/custom/*.toml` arrive from the public WDI Method package via
`npx wdi-method install` / `update`. Everything in `.constitution/project/` —
this file, `codebase-*-guide.md`, and any rule this repo adds — is **ours**: it is
seeded once and never written again.

- A method file MUST NOT be invented or patched here to improve the method. If a
  rule is wrong, it is fixed in the WDI Method package, then brought here with
  `update`.
- `wdi-method update` MUST overwrite everything in `.constitution/method/` and
  MUST NOT touch `.what/`, `.how/`, `.control/` product state, anything in
  `.constitution/project/` — at **any** `status:`, `Draft` included, which is when
  a codebase guide is actually written — or `_bmad/custom/*.user.toml`.
- A rule particular to this repo MUST be written out in full in this file or a
  sibling, and MUST NOT be replaced by a pointer into another repository.

A prefix in `.claude/skills/` names the **method**, not the owner: `bmad-*` is
BMad's, `wdi-*` is this method's.

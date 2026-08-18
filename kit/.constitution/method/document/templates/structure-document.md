---
type: structure
scope: document
verified: '{YYYY-MM-DD}'      # the day the tree was actually read
commit: '{sha}'               # the commit it was read at — staleness is measured against this
---

# Document Structure

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     This file is DESCRIPTIVE. It states which parts of the corpus actually carry content today.
     The layers themselves, the placement test, the naming scheme, and slot numbering all belong to
     corpus-guide.md and MUST NOT be restated here.

     Written and refreshed only by `wdi-init` intent `structure`, never by hand. Rules for both maps live in
     .constitution/method/structure-guide.md.

     Same shape as the codebase map: annotated trees, folders complete, ★ inline on the documents
     that earn it. What differs is the split — the codebase map splits by deployability, this one
     splits by LAYER, because that is the axis a reader is lost on.

     The five roots are fixed, so the top-level tree is not a discovery. Which sub-folders carry
     content, which Product Component folders exist, and which slots have been split out of a kernel
     ARE, and that is what this map is for. -->

## Verified

<!-- One line: date, commit SHA, and how the tree was read. If the commit is no longer an ancestor
     of HEAD, this map is stale and MUST be refreshed before a gate reads it. -->

## Top level

<!-- The five roots, one line each, with the state of each: populated, or still empty. Mark an empty
     root as empty rather than dropping it — a dropped root reads as a root that does not exist. -->

```text
.constitution/                # how we work — {state}
.control/                     # what currently holds — {state}
.what/                        # what was promised — {state}
.how/                         # how it is built — {state}
_bmad-output/                 # work in progress, not curated — {state}
```

## Per layer

<!-- One subsection per root that carries content. Annotated tree: sub-folders complete, ★ on the
     single-copy documents a reader must find first. Per-Product-Component folders are NOT expanded
     here — the table below owns them, and expanding both means maintaining both. -->

### {layer}

```text
{layer}/
├── {folder}/                 # what belongs here
│   └── {file}                # ★ why this one is key
└── {folder}/                 # {state}
```

## Product Components

<!-- One row per PC that actually exists. Both sides are expected: a PC with an SRS and no SDD, or
     the reverse, is drift and MUST be listed under Findings rather than normalised here. List only
     the slots that have been split out of a kernel; empty slots stay unlisted. -->

| Product Component | `.what/<pc>/` | `.how/<pc>/` | Slots split out |
| --- | --- | --- | --- |

## Registries and generated

<!-- Which registry files carry entries and which are still empty skeletons, and which generated
     tables have been produced. Generated output is never written by hand; naming it here is what
     makes a hand edit visible. -->

| File | State |
| --- | --- |

## Findings

<!-- Drift this map surfaced while being derived: a PC on one side only, a supplement with no
     citation, a folder outside the five roots, a document whose home contradicts corpus-guide.md.
     Findings are reported, never fixed here — fixing them is `wdi-reconcile` work, or the owning
     skill's.
     Cut the section only when it is genuinely empty. -->

---

<!-- Keep this legend last, and keep it one line. -->

★ = key document: single-copy, referenced from elsewhere, or the first thing a reader must find.

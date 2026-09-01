---
status: Accepted
---

# BMad Skill Register

**Loaded when:** deciding which BMad skill a piece of work needs, or checking what one writes

This used to be the full catalogue of all 59 installed BMad skills. **That catalogue is retired.** It was a
copy of somebody else's inventory, it went stale on every BMad update, and nothing in this method read more
than a dozen of its rows. What binds is the division of labour below; for anything about a BMad skill this
method does not invoke, ask `bmad-help`, which reads BMad's own documentation.

## Who writes what

| Artifact | Written by | Wrapped in |
|---|---|---|
| Product brief | `bmad-product-brief` | `wdi-problem` |
| PRD | `bmad-prd` | `wdi-product` |
| UX — `EXPERIENCE.md` + `DESIGN.md` | `bmad-ux` | `wdi-ux` |
| Architecture spine + the C4 set | `bmad-architecture` | `wdi-blueprint` intent `platform` |
| **UC catalogue · actors · entities · business rules** | **nothing in BMad** | `wdi-blueprint` writes it itself |
| **SRS and all of `.what/<pc>/`** | **nothing in BMad** | `wdi-component` writes it itself |
| **SDD and all of `.how/<pc>/`** | **nothing in BMad** | `wdi-component` writes it itself |
| Document review | `bmad-review` | `wdi-review` |
| Course correction | `bmad-correct-course` | `wdi-decision` |

**Everything below G5 left this table.** `SPEC.md`, the tickets, the code, and the code panel are produced
by `to-spec`, `to-tickets`, `implement`, `tdd`, and `code-review` — engines that are not BMad's, and that
three of the five carry `disable-model-invocation: true` for, so **the owner runs them and no skill can**.
`wdi-build` owns that pipeline; `bmad-guide.md` owns the reasoning.

**The three bold rows are why this method exists.** BMad stops at the promise and starts again at the
mechanism, and every behaviour in between had no author. Three consequences attach to those artifacts and
MUST be handled deliberately rather than discovered: no `doc_standards` fires a review, no memlog is born on
its own, and no template enforces itself.

## No BMad skill is invoked directly

Every one above has a wrapper, and the wrapper is what checks position, verifies the result against the
guide, and lands the memlog. Routing past it produces an artifact nothing verifies.

**One exception, and it is narrow:** on the Fast Path the owner runs `/implement` directly, with no wrapper.
A Fast Path that turns out to touch an `FR` MUST stop and become a spec `S`, which puts it back inside
`wdi-build`.

## What is available but writes nothing

| Skill | Use |
|---|---|
| `bmad-advanced-elicitation` · `bmad-party-mode` | Thinking aids. They produce no artifact and MUST NOT be treated as authors |
| `bmad-deep-recon` | Research, before a brief rests on outside data. Its output stays in `_bmad-output/` permanently and MUST NOT be folded into the brief |
| `bmad-help` | Questions about BMad itself. It MUST NOT be used to answer "where am I" — that is `wdi-help` |

## What is NOT USED, and MUST NOT be

| Skill | Why |
|---|---|
| `bmad-spec` · `bmad-build` · `bmad-build-auto` · `bmad-code-review` · `bmad-retrospective` | **Retired.** The engine layer below G5 is no longer BMad's. Their `_bmad/custom/*.toml` overrides are withdrawn and `update` removes any still installed |
| `bmad-create-epics-and-stories` · `bmad-sprint-planning` · `bmad-sprint-status` | They belong to the sprint route, which keeps status in a hand-edited file. This method reads status from the ticket itself — `bmad-guide.md` owns the reasoning |
| `bmad-create-story` · `bmad-dev-story` · `bmad-quick-dev` · `bmad-dev-auto` | Deprecated in BMad itself, and their replacements are retired too |
| `bmad-editorial-review*` · `bmad-review-*` | Shims onto `bmad-review` lenses. Ask for the lens, not the shim |
| `bmad-document-project` · `bmad-generate-project-context` | Forward to `bmad-project-context`. This repo's agent instructions are maintained by hand |
| Any skill named as a **gate condition** | A gate is passed by its checklist and its validators, never by a skill having run |

## The class that decides where output lands

`bmad-guide.md` owns the class definitions; what matters here is that **class B** exists because some skills
write several things at once that belong to different layers. `bmad-ux` is the case: `EXPERIENCE.md` is a
promise and `DESIGN.md` is a build detail, and no configuration can send them to two places. Its output
lands in a neutral folder first, and `wdi-ux` places it.

Which skill lands which output is the ownership table in `corpus-guide.md`, and it MUST NOT be duplicated
here.

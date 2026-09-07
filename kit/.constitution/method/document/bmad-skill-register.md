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
by `to-spec`, `to-tickets`, `implement`, `tdd`, and `code-review` — engines that are not BMad's. Three of
the five ship with `disable-model-invocation: true`; `wdi-method` strips it from the copies installed in
this repo and writes a guard line naming who may drive them, so **`wdi-build` and `wdi-autopilot` invoke
them directly** and an unattended iteration needs nobody. `wdi-build` owns that pipeline;
`bmad-guide.md` owns the reasoning.

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
| `bmad-qa-generate-e2e-tests` | Tests for a feature that **already exists**. `tdd` is test-first for work being built, so this has no replacement here and is NOT retired — but what it writes is a test, never a contract, and it MUST NOT be read as one |
| `bmad-checkpoint-preview` | A human reading aid over a change, the same class as `bmad-advanced-elicitation`. It MUST NOT be counted as the Step 3 panel: that one is a separate dispatch by a different agent |
| `bmad-help` | Questions about BMad itself. It MUST NOT be used to answer "where am I" — that is `wdi-help` |

## What is NOT USED, and MUST NOT be

**The criterion, and it binds every row below.** A BMad skill is retired only where this method has a
**named replacement** for what it produces. Without one it is not retired — it goes in the table above
instead, as something that may be used but MUST NOT author. Banning a capability with nothing in its
place is how a method gets worked around rather than followed.

### Retired at G5 — enforced by install and update

**This is enforced, not only stated.** `install` and `update` set `disable-model-invocation: true` on
every wrapper below and add a `Skill(<name>)` deny rule to `.claude/settings.json`, both re-applied on
every run because BMad's installer rewrites its own wrappers. A person typing `/bmad-build` still gets
it: the method retires a default, it does not confiscate a tool. The list lives in
`bin/wdi-method.js` as `BMAD_RETIRED_G5`, and a test fails when this table and that array disagree.

| Skill | Replaced by | Why |
|---|---|---|
| `bmad-spec` | `to-spec` | **Retired.** The contract below G5 is no longer BMad's. Its `_bmad/custom/*.toml` override is withdrawn and `update` removes any still installed |
| `bmad-build` · `bmad-build-auto` | `implement` · `wdi-autopilot` | **Retired.** `bmad-build` describes itself as implementing "any user intent, requirement, story, bug fix or change request" — the most inviting description in the repo's skill index, for the one thing this method owns most tightly. `bmad-build-auto` is an unattended loop, which is `wdi-autopilot`'s |
| `bmad-code-review` | `code-review` | **Retired.** The panel at Step 3 is a separate dispatch by a different agent; BMad's own review layers are the builder reviewing itself |
| `bmad-retrospective` | — | **Retired** with `RTR-` and `V19`. A frozen `RTR-` file stays where it is |
| `bmad-agent-dev` | `implement` | **Retired.** "Senior software engineer for story execution and code implementation" is `implement`'s sentence |
| `bmad-create-epics-and-stories` | `to-tickets` | **Retired**, and not merely by preference: the `epics` level between a spec and its tickets is **repealed in code** — `validate.py` reads a flat `tickets:` list. A skill whose only output is a shape nothing reads |
| `bmad-create-story` · `bmad-dev-story` · `bmad-dev-auto` · `bmad-quick-dev` | `implement` | **Retired.** BMad deprecated all four in favour of `bmad-build`, which is itself retired here. An alias to a retired skill is retired |
| `bmad-sprint-planning` · `bmad-sprint-status` | the ticket itself | **Retired.** The sprint route keeps status in a hand-edited file; this method reads status from the ticket — `bmad-guide.md` owns the reasoning |

### Not used for other reasons — not enforced, and not G5's

These are outside the enforced list above: nothing locks them, because nothing here replaces them and
none of them competes for G5's work.

| Skill | Why |
|---|---|
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

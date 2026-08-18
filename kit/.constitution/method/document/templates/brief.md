# Product Brief Template

A flexible starting structure for the executive product brief. Adapt aggressively to the product, the purpose, and the domain. Drop sections that do not earn their place, add sections the product needs, reorder freely. The brief serves the product's story, not the template's shape.

## Default Structure

```markdown
# Product Brief: {Product Name}

## Executive Summary

[2-3 paragraph narrative: what this is, what problem it solves, why it matters, why now. Compelling enough to stand alone — if someone reads only this section, they should understand the vision.]

## The Problem

[What pain exists, who feels it, how they cope today, the cost of the status quo. Be specific: real scenarios, real frustrations, real consequences.]

## The Solution

[What is being built, how it solves the problem. Focus on the experience and the outcome, not the implementation.]

## What Makes This Different

[Key differentiators. Why this approach over alternatives, what is the unfair advantage. Be honest. If the moat is execution speed, say so. Do not fabricate technical moats.]

## Who This Serves

[Primary users — vivid but brief. Who they are, what they need, what success looks like for them. Secondary users if relevant.]

| Role | Need | Tier |
|---|---|---|
| {role} | {what they need from this product} | **primary** |
| {role} | {…} | secondary |
| {role} | {…} | secondary |

[Exactly one row MUST be `primary`. Every user and stakeholder who touches the product belongs in this table — including the ones who never open it, but pay for it, approve it, or are accountable for it. Shared goals that cut across roles go in a line under the table.]

## Goals

[What the product is trying to achieve, one line each. Number them `BG-1`, `BG-2`, … — `BG` is the first link of the traceability chain `BG → CAP → FR/NFR → UC → DEC → Story → Test`, so these IDs are cited downstream and MUST stay stable once written.]

- **BG-1** — core value: [the goal that justifies the product existing at all]
- **BG-2**: [...]

[MUST NOT be numbered `G1`, `G2` — `G1`–`G5` already name the five gates.]

## Success Criteria

[How we know this is working. Mix of user success signals and business objectives. Measurable.]

## Scope

[Boundary document, not a feature list. Keep both lists tight.]

### Scope In

[What is in for the first version.]

### Scope Out

[What is explicitly out, written as items. MUST NOT be left to be inferred from absence — the value of this list is that it names what someone will otherwise assume is coming. Per-release MVP scope belongs in the PRD; this is the product boundary.]

## Constraints

[What is fixed before design starts and cannot be traded away: platform scope, integration boundary, regulatory limit, milestone boundary, a timeline that is genuinely immovable. One line each, and each MUST say what it forbids.]

[Technical constraints that only shape implementation belong in `addendum.md`, not here. A constraint that emerges from a design decision becomes `AD-N` in the architecture spine — MUST NOT be appended to this list later.]

## Assumptions

[What is believed true but not verified, and that the brief would be wrong without. State each so it could be proven false.]

[An assumption that starts to wobble MUST be promoted to a row in `.control/registry/risks.yaml` with an owner. An assumption nobody would act differently about is not worth listing.]

## Prerequisites

[What MUST exist or be granted before work can start: access, accounts, data, an upstream system, a decision someone else owns.]

[Any prerequisite not yet satisfied MUST have a matching row in `.control/questions/external.md` naming who is being waited on and by when.]

## Vision

[Where this goes if it succeeds. What it becomes in 2-3 years. Inspiring but grounded.]
```

---

## Project overrides — WDI

- **Home.** `.what/_product-brief/brief.md`, with `addendum.md` beside it. Set through
  `run_folder_pattern = "_product-brief"`; both filenames are fixed by the skill and MUST NOT be
  expected to change.
- **Singleton.** One brief per product, spanning every release. A second product MUST get its own
  repository rather than a second brief.
- **Decision Summary.** MUST name exactly one problem, one **primary** user, and one measure of
  success. Secondary users and stakeholders are listed, not ranked away. If the primary cannot be
  chosen, the discovery is not finished.
- **Six sections above the BMad default.** `Who This Serves` carries a full stakeholder table;
  `Scope` is split into In and Out; and `Goals`, `Constraints`, `Assumptions`, and `Prerequisites`
  are added. The last three have no home anywhere else in the corpus.
- **No Product Component list.** The slicing is born at the tail of G2 through `wdi-init` intent
  `component`, which reads
  the brief and every PRD once a domain model exists. A list guessed at G1 is a guess made before
  there is anything to guess from.
- **Raw material stays out.** Research, brainstorming, and pressure-test output live in
  `_bmad-output/` and stay there. It MUST NOT be folded in, and MUST NOT be promoted into `.what/` —
  a `DEC-` or the PRD cites it by path instead.
- **Dying cheap is a pass.** A brief that concludes the idea is not worth building is a valid G1
  outcome, and the most profitable one.
- **Memlog.** Written to `.control/memlog/brief.md` via `--path`.

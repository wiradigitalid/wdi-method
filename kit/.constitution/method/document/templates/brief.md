# Product Brief Template

A flexible starting structure for the executive product brief. Adapt aggressively to the product, the purpose, and the domain. Drop sections that do not earn their place, add sections the product needs, reorder freely. The brief serves the product's story, not the template's shape.

**The brief states the current design. It is not a history of itself.** A section MUST NOT carry a
correction block, a "previously" note, or a record of who changed what — that belongs in
`.control/decisions/` or is not worth keeping. See `corpus-guide.md` § The corpus is written in the
present tense.

**A derived fact has exactly one home, and it is never this document.** `Goals` cites
`goals.yaml`; it does not restate what a goal says. `Assumptions` and `Prerequisites` are not
sections here at all — they live in `.control/questions/`, and this brief is never their second copy.
See `corpus-guide.md` § A derived fact has exactly one home.

## Default Structure

```markdown
# Product Brief: {Product Name}

> **This is the working brief.** It points at the registry instead of repeating it, so `Goals` is one
> line and there is no Assumptions or Prerequisites section here.
>
> **To read or hand over one complete, self-contained document, run `/wdi-report render brief`.**
> It writes `.what-rendered/_product-brief/brief.md` with the goals, the open assumptions, and the open
> prerequisites filled in from their own homes. That file is regenerated, never hand-edited.

## Why

[2-3 paragraphs: what this is, what problem it solves, why it matters, why now, and where it goes if
it succeeds. One narrative — do not split "what this is" from "where this goes" into two sections.
Compelling enough to stand alone: if someone reads only this section, they understand the vision.]

## The Problem

[What pain exists, who feels it, how they cope today, the cost of the status quo. Be specific: real
scenarios, real frustrations, real consequences.]

## The Solution *(optional — one paragraph, no more)*

[What kind of thing is being built — the bet, not the feature list. "A self-serve app, not a managed
service"; "an API, not a dashboard." One paragraph. The moment this needs a second paragraph it has
started designing, and design is G2's job, not G1's.]

## What Makes This Different *(optional)*

[Key differentiators. Why this approach over alternatives, what is the unfair advantage. Be honest. If
the moat is execution speed, say so. Do not fabricate technical moats.]

## Who This Serves

[Primary users — vivid but brief. Who they are, what they need, what success looks like for them. Secondary users if relevant.]

| Role | Need | Tier |
|---|---|---|
| {role} | {what they need from this product} | **primary** |
| {role} | {…} | secondary |
| {role} | {…} | secondary |

[Exactly one row MUST be `primary`. Every user and stakeholder who touches the product belongs in this table — including the ones who never open it, but pay for it, approve it, or are accountable for it. Shared goals that cut across roles go in a line under the table.]

## Goals

Goals — see `.control/registry/goals.yaml` → `goals:`.

[This section is a POINTER, not a list. `BG-N` and its statement live in the registry — that is what
lets `wdi-product` cite `BG-N` without a second copy drifting from this one. If a goal needs a reason
beyond its statement, that reason is a `why:` field on the goal's own row in the registry, not a
paragraph here. `BG` is the first link of the traceability chain `BG → CAP → FR/NFR → UC → DEC →
Ticket → Test`.]

[MUST NOT be numbered `G1`, `G2` — `G1`–`G5` already name the five gates.]

## Success Criteria

[Exactly ONE measurable figure that proves this worked. Not a mission statement, not a mix of signals
— one number, with a timeframe. "40% of visitors who start checkout finish it, within three months of
launch." A criterion nobody could check without opening the code is not a criterion.]

## Scope

[Boundary document, not a feature list. Keep both lists tight. This is the PRODUCT boundary — what
belongs in this product at all, ever. Per-release MVP scope belongs in the PRD's own Scope section,
not here.]

### Scope In

[What belongs to this product's boundary — not "what ships first," which is the PRD's call.]

### Scope Out

[What is explicitly out, written as items. MUST NOT be left to be inferred from absence — the value of this list is that it names what someone will otherwise assume is coming. Per-release MVP scope belongs in the PRD; this is the product boundary.]

## Constraints

[What is fixed before design starts and cannot be traded away: platform scope, integration boundary, regulatory limit, milestone boundary, a timeline that is genuinely immovable. One line each, and each MUST say what it forbids.]

[Technical constraints that only shape implementation belong in `addendum.md`, not here. A constraint that emerges from a design decision becomes `AD-N` in the architecture spine — MUST NOT be appended to this list later.]
```

---

## Project overrides — WDI

- **Home.** `.what/_product-brief/brief.md`, with `addendum.md` beside it. Set through
  `run_folder_pattern = "_product-brief"`; both filenames are fixed by the skill and MUST NOT be
  expected to change.
- **Singleton.** One brief per product, spanning every release. A second product MUST get its own
  repository rather than a second brief.
- **Why replaces Executive Summary and Vision.** BMad's default carries both as separate sections with
  near-identical instructions — one narrative, told once, is what a reader actually gets.
- **Success Criteria MUST name exactly one measurable figure**, checked at G1 — this is the ★ question
  the gate asks and the section the brief is most often thin on.
- **Who This Serves.** MUST name exactly one **primary** user. Secondary users and stakeholders are
  listed, not ranked away. If the primary cannot be chosen, the discovery is not finished.
- **Goals is a pointer, not a list.** `BG-N` and its statement are authored straight into
  `.control/registry/goals.yaml` by `wdi-problem` when it lands the brief — landing the
  registry row is part of producing the brief, not a follow-up. This section MUST NOT restate a
  goal's text; a stated reason beyond the statement belongs in that row's `why:` field.
- **No Assumptions or Prerequisites section.** Both moved out entirely: an assumption goes through
  `wdi-question` into `.control/questions/assumptions.md`, a prerequisite into
  `.control/questions/external.md`. The brief cites neither by restating it — the generated deliverable
  (`.what-rendered/_product-brief/brief.md`) is where a reader sees them assembled with everything else.
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

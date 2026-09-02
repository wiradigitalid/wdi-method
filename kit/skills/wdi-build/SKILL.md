---
name: wdi-build
description: Use at G5 Release — one spec from open to closed in one supervised run. Opens the spec, hands the owner to-spec and to-tickets, ships every ticket to a green PR through a five-step pipeline, then closes the spec. One invocation, not four.
---

# WDI Build

One unit of work, one invocation. A spec used to need four calls — open it, produce the contract, ship each
ticket, close it — and three of those were bookkeeping. They are all in here now, because a unit of work that
needs four invocations gets three of them skipped.

**The engine layer below this gate is not BMad's.** `to-spec`, `to-tickets`, and `implement` produce the
contract, the tickets, and the code; `tdd` and `code-review` do the work inside them. `bmad-spec`,
`bmad-build`, `bmad-build-auto`, and `bmad-code-review` are **retired** and MUST NOT be invoked.

**Three of those engines are human-invoked.** `to-spec`, `to-tickets`, and `implement` carry
`disable-model-invocation: true`, so this skill CANNOT invoke them and MUST NOT claim to. It states the command
for the owner to run, waits, then verifies the result and lands it. That is not a workaround: the points where
those engines need a human are the gates, and owner time is what a gate is for.

**No orchestration tool is required, and this skill MUST NOT name one.** How the work is carried out is the
session's own arrangement: an orchestration skill, this CLI's native subagent tooling, or the coordinator doing
a step itself. Which CLI, which model, and which effort staff a step come from the local Agent Rules, and MUST
NOT be restated here. Every rule below holds whatever the mechanism — they are about the artifact and who
judges it, not about how an agent is launched.

Two roles exist regardless. The **coordinator** — this session — holds every judge call, the registries, and
every remote git action. The **builder** of a step holds the spec and the code.

When the coordinator is also the builder, the separation the pipeline rests on is absent. That MUST be reported
as absent rather than worked around: a step judged by whoever wrote it is a self-report. One consequence is
hard — see Step 3: at `risk_accepted: low` the panel requires reviewers who are not the builder, and a session
that cannot provide them is **blocked**, not excused.

## Precondition, and the one that is easy to miss

| Check | When it fails |
|---|---|
| Every component this spec touches has passed G4, **or** sits at `mode: catalog` | Route to `wdi-component`. `spec-after-g4` checks it, and `catalog` skipping G4 is by design, not an exception |
| An isolated worktree | Isolate first. MUST NOT run in a shared checkout |
| Every `prd` slug names a real `.what/_prd/<initiative>/` folder | A spec without a promise covering it is a spec nobody agreed to (`spec-names-release-prd`) |

The repo commits straight to `main` and opens a PR only when asked. **Invoking this skill is that ask**, for
this spec only; it MUST NOT be read as standing permission for the next change.

## Phase 1 — Open the spec

Record it in `.control/registry/specs.yaml`. The frame opens here; the `tickets` rows land in Phase 2, because
that is where they are born.

| Field | Rule |
|---|---|
| `id` | `SPEC-<N>`, monotonic, never reused. A `W<N>` id in a frozen record is a **retired alias** and MUST NOT be rewritten |
| `release` | MUST be stated. The release↔spec cadence is situational and MUST NOT be inferred from numbering (`spec-names-release-prd`) |
| `prd` | MUST be stated: which initiative PRDs this spec delivers against. MUST NOT be derived from `release` |
| `fr` | The `FR` this spec satisfies. Ideally one — an `FR` is human-testable from birth |
| `size` | `S` · `M` · `L`. MAY be raised mid-flight; MUST NOT be lowered |
| `depends_on` | At **spec** level. A spec declaring none runs in parallel with its neighbours |
| `spec_folder` | One per spec, not one per spec × component |
| `tickets` | Flat, one row per ticket: `id` · `component` · `satisfies: [UC]` · `blocked_by` · `touches` · test names |
| a ticket `id` | `<spec-id>-<NN>` — `SPEC-3-01`. The engine numbers its files from `01` per feature, which is unique only inside one spec; the RTM needs a key that is unique across the corpus |

**`tickets` is an index, not a store.** The ticket's prose lives where the tracker put it; the row carries only
what RTM and the validators read. And ticket **status** MUST NOT be copied here — it is read from the ticket
itself when `.control/generated/` regenerates (`ticket-status-one-home`). Two homes for one fact is how registries start lying.

`ticket-status-one-home` finds the file at `{spec_folder}/issues/<NN>-*.md`, from the number at the tail of the id, and reads its
status from either a `**Status:**` body line — what the engine writes, because a ticket file is a tracker
payload and trackers do not read YAML — or `status:` in frontmatter.

The `epics` nesting is **repealed**. A ticket names its `component` directly; an intermediate level that only
grouped rows bought nothing and cost a lookup.

Size does not choose which gates are active — that is `mode`'s job. It decides two things: session merging
(`S` merges G4 and G5 into one 20-minute session) and whether `SPEC.md` is written at all.

## Phase 2 — The contract, and the tickets

Two engines, and **the owner runs both.** State the command, wait, then verify and land.

| Size | What the owner runs | What lands |
|---|---|---|
| `M` · `L` | `/to-spec`, then `/to-tickets` | `SPEC.md` in `spec_folder` · ticket files · the `tickets` index rows |
| `S` | `/to-tickets` only | ticket files · the `tickets` index rows. **No `SPEC.md`** |

At `S` the tickets **are** the contract. `to-tickets` accepts a conversation directly, so a middle document
buys nothing there. From `M` up it is written first, because two things have to be settled **before** tickets
are cut and neither survives being decided afterwards: the **seams** the feature will be tested at — fewest
possible, highest possible, agreed with the owner — and the **testing decisions**, which say what a good test
is here and name the prior art.

### What you verify before landing anything

- **Nothing new.** `SPEC.md` is a **projection** of `.what/` + `.how/`. It MAY restate a promise in its own
  words — a machine contract is more useful self-contained — but **every restatement MUST refer to the live
  corpus document it came from.** A reference that does not resolve is not a wording problem: the gap is
  upstream. Route to `wdi-component` or `wdi-blueprint`, and do not let the contract invent it.
- **Every user story resolves to an id.** A user story with no `FR` or `UC` behind it is a **new promise**,
  and a new promise is `wdi-product`'s, never a spec's.
- **Every ticket names what it satisfies.** No `satisfies`, no landing: without it the chain
  `FR → UC → ticket → test` breaks and RTM cannot say which promise went green. This is the one field
  `to-tickets` does not ask for on its own, so it is the one most likely to be missing.
- **Every ticket is vertical.** A slice of one layer is not a ticket. The exception is a wide refactor,
  sequenced expand → migrate in batches → contract; `delivery-flow-guide.md` owns that rule.
- **Ticket files land under `spec_folder`.** Their **shape** is the engine's — one file per ticket, numbered
  in dependency order, blocking edges declared — and only the root is ours, because `to-tickets` states its
  own location is tracker-specific and configured. A ticket at the repo root, or under `docs/` or
  `.scratch/`, is drift: Article 3 names every layer this method has and those are not among them.

`SPEC.md` and ticket files **are not read by humans.** Both are machine contracts, and no review burden MAY be
moved onto them. `wdi-review` MAY still be dispatched over the contract; its trace lands on the spec in
`specs.yaml` — and where there is no `SPEC.md`, one trace covers the **ticket set as one artifact**, never one
review per ticket.

## Phase 3 — Ship each ticket

Work the **frontier**: the tickets whose blockers are all closed. A ticket whose `blocked_by` is not yet
satisfied MUST NOT be started, however ready it looks.

| # | Step | Engine | Exit condition |
|---|---|---|---|
| 1 | Encode | `/tdd` | **Failing tests exist that encode this ticket's acceptance criteria** |
| 2 | Build | `/implement` — the owner runs it; it uses `/tdd` at the agreed seams | Those tests green, typecheck clean, full suite green once |
| 3 | Panel | `code-review`, as a **separate** dispatch | Panel adjudicated, zero unresolved must-fix |
| 4 | Publish | — | Branch pushed, PR open, ticket-closing checklist answered |
| 5 | CI | — | All checks conclude green on the pushed head SHA |

**Step 1 is the change that matters most.** It used to be a plan, judged from a frontmatter field a builder
wrote about itself. Now it is a **failing test suite** — the acceptance criteria, encoded, and demonstrably
red. That is evidence rather than a claim, and it is what `ticket-has-test` and G5's ★2 have always been asking for:
*acceptance criteria proven by a test, not by an agent's statement.* Under TDD the test exists **before** the
code, so the proof is not retrofitted.

### Engine rules

- **MUST judge Steps 1 and 2 from the test suite**, not from a report and not from a status field. Red at the
  right assertions closes Step 1; green with a clean typecheck closes Step 2. A builder's chat report MUST NOT
  settle either.
- Ticket **status** is read from the ticket itself. It MUST NOT be copied into `specs.yaml` (`ticket-status-one-home`).
- Every step MUST start from a **fresh context**, and a fix round MUST NOT go back to whoever produced the
  code. The ticket carries everything the next builder needs, and inherited context is how a step stops judging
  the artifact on its own merits. Where one session runs consecutive steps itself, it MUST re-read the artifact
  rather than trust what it remembers writing.
- A step handed to a separate agent MUST be launched so it cannot sit waiting for input nobody will give, and
  its start MUST be confirmed from observed activity — never from a readiness match alone.
- A step that fails because the agent could not spawn what it needed is a **capability** failure, not a ticket
  failure. MUST retry it somewhere that can, and MUST NOT record it against the ticket.
- MUST NOT reorder or drop a step. A step with nothing to do MUST be reported as such, not skipped silently.
- A ticket returned by the panel MUST have its acceptance criteria amended and its status reset before it is
  picked up again — see Step 3.

### What every builder brief MUST carry

Three rules this corpus adds, and `/implement` knows none of them. All three MUST reach whoever writes code in
this spec — in the dispatch when a step is dispatched, and in the session's own working instructions when it
is not.

- **Debugging is conditional, never a phase.** When a test or build fails and the cause is not known, the
  builder MUST run `wdi-systematic-debugging` before proposing any fix. A third failed fix attempt is the signal
  to escalate, not to try a fourth.
- **The corpus is not the builder's to change.** A builder MUST NOT edit `.what/`, `.how/`, or an `applied`
  `DEC-`. A deviation from the SDD or an `AD-N` is **reported**, and it becomes a `DEC-` through
  `wdi-decision` — never absorbed as a code patch.
- **Verification is run, not assumed.** The commands are this product's, and they live in
  `.constitution/project/codebase-stack-guide.md` — build, test, and whatever the front end needs, each with
  the directory it runs from. A skill MUST NOT carry one product's build line. A green registry workflow
  MUST NOT be reported as proof the code compiles; they answer different questions.

### Step 1 — encode the acceptance criteria as failing tests

- The tests MUST be written **at the seams the spec agreed** — existing seams preferred, highest possible,
  fewest possible. Inventing a new seam here, after the agreement, is a finding: it means Step 1 is redesigning
  what Phase 2 settled.
- Every acceptance criterion MUST have at least one test. A criterion no test can express is not an acceptance
  criterion — it goes back to the ticket, or to the owner as an intent gap.
- The tests MUST be **seen red, at the right assertions.** A test that passes before the code exists is testing
  nothing, and a suite that fails for the wrong reason — an import error, a missing fixture — has not encoded
  anything yet.
- A test MUST NOT assert a literal where the behaviour is what matters. The panel treats that as a test that
  cannot fail, and returns it.

### Step 2 — build

- The owner runs `/implement`, and it MUST be given the ticket and the three brief rules above.
- It commits to the current branch and **never pushes**. That is its own behaviour and it is what we want; the
  coordinator is the hand that pushes.
- **`/implement` calls `/code-review` itself, and that call does NOT satisfy Step 3.** It is the builder
  reviewing its own work — self-review by construction. Step 3 stands as a separate dispatch regardless of what
  ran inside Step 2.
- The full suite MUST be run green once at the end, not only the tests this ticket touched. A ticket that
  passes its own tests and breaks a neighbour's has not finished.
- Where the work turns out to need something the ticket does not authorise, it stops and reaches the owner with
  the question verbatim. The builder MUST NOT widen its own scope.

### Step 3 — panel, then judge

Panel composition follows `risk_accepted`: at `low` a two-reviewer panel is **required** on the code; at
`medium` and `high` it is available and SHOULD be used when the diff touches money, personal data, or a third
party. The local Agent Rules govern which CLIs and models staff the panel. **A reviewer MUST be a different
agent from the builder** — the builder's own review layers, `/implement`'s internal `/code-review` included,
are self-review by construction and never satisfy the panel. This is the one separation in the pipeline that
MUST NOT be collapsed: where the session cannot provide it and `risk_accepted` is `low`, the ticket is blocked
and the owner MUST be told, because the field they set is what makes the panel required.

`code-review` reviews along two axes — **Standards**, against this repo's documented conventions, and
**Spec**, against what the ticket asked for. Both MUST run. Reporting one axis as the panel is reporting half
a review.

- MUST adjudicate every contested finding by reading the cited lines. Votes MUST NOT settle a finding. A finding
  neither reviewer can locate in the diff is dismissed with that reason stated.

**MUST return to Step 2:**

- Breaks a ticket's acceptance criterion, or contradicts the contract, the SDD, an `AD-N`, or an `applied` `DEC-`
- Wrong behaviour, crash, or data loss reachable from the running app
- Corpus drift: an `LC` touched but not registered, a contract changed in code but not in `02-contracts/`, a
  screen added without its `01-ux/` entry
- An enum value rendered straight to the screen instead of read off its label map
- Payment or private data reaching a tracked file
- A weakened guard, or a test that cannot fail — including one asserting a literal instead of the behaviour it
  claims to cover

**MUST record as follow-up and MUST NOT return to Step 2:** style or naming with no behaviour delta · a
refactor outside this ticket's scope · a pre-existing defect this ticket did not touch · a speculative risk
with no reachable path.

A must-fix MUST return as a **ticket amendment**, never a chat instruction: amend what the ticket asks for,
note the finding that caused it, reset the ticket's status to `ready-for-agent`, then pick it up again. **What
a ticket `satisfies` is not amendable here** — that is the promise, and a must-fix rooted in the promise is an
intent gap that goes to the owner through `wdi-product`. Changing the `FR` a ticket serves in order to make the
code pass is how a corpus starts agreeing with whatever was built.

Cap: **2 return trips.** MUST re-run the whole panel after each fix round — a fix introduces defects. On hitting
the cap MUST escalate and MUST NOT open a PR carrying an unresolved must-fix.

### When the code turns out to be right and the document wrong

This is normal during G5 and it is **not drift**. Building a thing is how you find out what the thing is.

The builder still MUST NOT edit `.what/`, `.how/`, or an `applied` `DEC-` to make its own code fit — that is
the corpus learning to agree with whatever was built, and it is a different failure. What happens instead:

1. **Say it once.** Name what the code does, which promise it contradicts, and what that costs. One place,
   one time. An `AD-N` is the one contradiction that **stops** — `decision-guide.md` owns it.
2. **The owner decides.** If they adopt the code, that survey is spent.
3. **The owning skill edits**, in the present tense, as if the design had always said this — `wdi-product`
   for an `FR`, `wdi-component` for behaviour or design, `wdi-blueprint` for a cross-component rule.

What MUST NOT happen after step 2: raising the same conflict again in a later pass, opening an `OQ-` for it,
dispatching a review over it, or writing anywhere in the corpus that the change arrived late. The commit is
that record. `corpus-guide.md` § The corpus is written in the present tense is the binding rule.

### Step 4 — ticket-closing checklist, then push and PR

The checklist is **three items**, and it MUST be answered before the PR opens:

1. Something the next person needs to know? → **into the document that carries it**, and that is almost
   always where it ends. It reaches `wdi-decision` only when no design document has a home for it —
   `decision-guide.md` § A decision's first home. A ticket contradicting an `AD-N` **stops** rather than
   closing; that is the one case where recording is mandatory.
2. A trap for the next agent? → recorded where the next agent will read it.
3. Test names matching what `specs.yaml` records?

The five items that left this list moved to Phase 4, where the information actually exists.

- MUST run the repository's commit/push audit before `git push`: refuse the forbidden paths, run the guard test,
  fix content on failure. A failing guard is a finding about the content — MUST NOT weaken the guard or the test.
- MUST NOT push to `main`/`master`, MUST NOT force-push, MUST NOT merge.
- The coordinator MUST be the hand that pushes and opens the PR.

### Step 5 — watch CI, then judge

- MUST wait for every check to conclude, then confirm the checks belong to the **pushed head SHA**. A green
  report from a stale run is a false report.
- `korpus.yml` validates the corpus, not the code. Build and test evidence comes from Step 2's own runs.
- Classify each failure before acting: a defect from this change → Step 1 if the test was missing, Step 2 if
  the code was wrong, with `wdi-systematic-debugging` when
  the cause is unknown · infrastructure or flake → re-run **once**, and MUST NOT patch code to mask it; a second
  identical failure is a defect · a guard failure → fix the content.
- Cap: 2 return trips. On hitting the cap MUST report red honestly rather than keep pushing.

### Parallel tickets

Tickets with no blocking edge between them MAY run at once — that is what the frontier is — but four
conditions MUST hold: each concurrent builder in its own worktree; `parallel-tickets-blocked` green for every pair released together;
the first ticket that establishes a component's shape already closed, so later tickets inherit its code map;
and no shared registry write in flight.

**A wide refactor is the exception, and it inverts the rule.** Its batches MUST run in sequence, not in
parallel, because each keeps CI green only while the expand still stands. Where even a batch cannot stay green
alone, they share an integration branch and green is promised only at the final integrate-and-verify ticket.

The pattern that MUST be preferred: run the biggest blocker alone first, let its shape decisions land, then fan
out.

## Phase 4 — Close the spec

**Six steps.** Run in this order and stop at the first failure.

1. **Registry catch-up.** Every `LC` the spec's design named is registered in `components.yaml`, and every
   `touches` value resolves — `lc-registered`. This is the moment those questions have answers.
2. **Inventories refreshed from code.** Run `.constitution/method/scripts/inventory.py`. The plan-versus-reality
   difference is reported as a finding; it MUST NOT be patched into agreement by hand.
3. **Structure maps refreshed** through `wdi-init` intent `structure`, if a base folder was born or removed or a
   key file moved.
4. **Distillation.** Every applicable row of the ownership table in `corpus-guide.md` has been landed by its
   owner. Anything durable in the spec folder leaves it now, or dies with it — **the ticket files included.**
   Their prose is working output; what survives is the index in `specs.yaml` and whatever the checklist routed.
5. **RTM green.** Every traceability row for this spec is closed. New risks are in the risk register with an
   owner.
6. Mark the spec `status: closed` in `specs.yaml`.

The retrospective step is **repealed**, and `RTR-` with it. It was the only thing size `L` decided, and the
only thing `V19` checked.

- You MUST NOT close a spec with an open distillation row. The whole point of an ephemeral working layer is that
  durable truth leaves it first.
- You MUST NOT reopen a closed spec to add scope. Scope arriving late opens a new spec, or goes through
  `wdi-decision` if it invalidates what is already planned.
- A change invalidating more than 30% of a spec's tickets MUST go through `wdi-decision`, not a patch to
  `specs.yaml`.
- Fast Path work is recorded as `fastpath` with no gates. If an `FR` turns out to be touched, the work MUST stop
  and be raised to a spec `S`.

## Red Flags — STOP

- "One reviewer approved, good enough"
- Judging Step 1 or Step 2 from a report instead of from the test suite
- **Counting `/implement`'s own `/code-review` as the panel** — that is the builder reviewing itself
- Writing `SPEC.md` at size `S`, or skipping it at `M` and up
- Landing a ticket with no `satisfies` — the RTM chain breaks silently and nothing else notices
- Amending what a ticket `satisfies` to make a must-fix go away
- A ticket that slices one layer instead of cutting through all of them, outside a wide refactor
- Running a wide refactor's batches in parallel
- Claiming this skill invoked `to-spec`, `to-tickets`, or `implement` — it cannot; the owner runs them
- A builder editing `.what/`, `.how/`, or an `applied` `DEC-` to make its code fit
- Fixing a failing test without knowing why it failed
- Opening a PR with an unresolved must-fix, or before the ticket-closing checklist is answered
- Editing a guard, a test, or an assertion to turn something green
- Reporting green without checking the head SHA, or reading green `korpus.yml` as a passing build
- Leaving a dispatched step able to stall on a question nobody is there to answer
- Naming an orchestration tool as this skill's requirement, or restating a CLI/model mapping the Agent Rules own
- Closing the spec without the registry catch-up in Phase 4 — that is where five checklist items now live
- Letting the contract state something `.what/` and `.how/` do not, or restate it without a reference

**Each of these means: stop, return to the step or phase that owns it, or escalate to the owner.**

## Output

MUST follow the Agent Rules `Answer Closing` block, carrying these additions:

- **what was done** — spec, `FR` satisfied, every ticket with its branch and PR URL, what the code now does
- **what blocked it** — every step that looped, every dismissed finding and why, anything left red, and every
  Phase 4 item that did not pass
- **what comes next** — every finding recorded as follow-up, every entry in a contract's `deferred` list, every
  ticket-closing item routed to another skill, and the plan-versus-code inventory differences. A follow-up
  absent here is a lost finding.

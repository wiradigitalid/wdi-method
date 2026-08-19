---
name: wdi-build
description: Use at G5 Release — one wave from open to closed in one supervised run. Opens the wave, runs bmad-spec, ships every story to a green PR through a five-step pipeline, then closes the wave. One invocation, not four.
---

# WDI Build

One unit of work, one invocation. A wave used to need four calls — open it, run `bmad-spec`, ship each story,
close it — and three of those were bookkeeping. They are all in here now, because a unit of work that needs
four invocations gets three of them skipped.

**REQUIRED SUB-SKILL:** MUST dispatch, wait, and escalate through `orchestration`. Worker CLI/model/effort MUST
come from the Orca Agent Dispatch tables in the user's Agent Rules; this skill MUST NOT restate them.

The coordinator (this session) holds every judge call, the registries, and every remote git action. Dispatched
workers hold the spec and the code.

## Precondition, and the one that is easy to miss

| Check | When it fails |
|---|---|
| Every component this wave touches has passed G4, **or** sits at `mode: catalog` | Route to `wdi-component`. V22 checks it, and `catalog` skipping G4 is by design, not an exception |
| An isolated worktree | Isolate first. MUST NOT run in a shared checkout |
| Every `prd` slug names a real `.what/_prd/<initiative>/` folder | A wave without a promise covering it is a wave nobody agreed to (V17) |

The repo commits straight to `main` and opens a PR only when asked. **Invoking this skill is that ask**, for
this wave only; it MUST NOT be read as standing permission for the next change.

## Phase 1 — Open the wave

Record it in `.control/registry/waves.yaml`:

| Field | Rule |
|---|---|
| `id` | `W<N>`, monotonic, never reused |
| `release` | MUST be stated. The release↔wave cadence is situational and MUST NOT be inferred from numbering (V17) |
| `prd` | MUST be stated: which initiative PRDs this wave delivers against. MUST NOT be derived from `release` |
| `fr` | The `FR` this wave satisfies. Ideally one — an `FR` is human-testable from birth |
| `size` | `S` · `M` · `L`. MAY be raised mid-flight; MUST NOT be lowered |
| `depends_on` | At **wave** level. A wave declaring none runs in parallel with its neighbours |
| `spec_folder` | One per wave, not one per wave × component |
| `epics` → `stories` | With `satisfies: [UC]`, `depends_on`, `touches`, and test names |

Story **status** MUST NOT be copied into `waves.yaml`. It is read from story-file frontmatter when
`.control/generated/` regenerates (V18). Two homes for one fact is how registries start lying.

Size does not choose which gates are active — that is `mode`'s job. It governs session merging (`S` merges G4
and G5 into one 20-minute session) and whether the retrospective runs (`L`).

## Phase 2 — The SPEC

Dispatch `bmad-spec` for the wave, slug `w<N>-<slug>`. **One wave = one `SPEC` = one tracker Task**, with no
compound joins.

`SPEC.md` is a **projection** of `.what/` + `.how/` onto this wave and MUST NOT introduce anything new. When it
needs something that is not in either, the gap is upstream: route to `wdi-component` or `wdi-blueprint`, and do
not let the SPEC invent it.

`SPEC.md` and story files **are not read by humans.** Both are machine contracts, and no review burden MAY be
moved onto them. `wdi-review` MAY still be dispatched over the SPEC; its trace lands on the wave in
`waves.yaml`, because `bmad-spec` is the sole author of the file and overwrites hand edits.

## Phase 3 — Ship each story

Steps 1–2 run `bmad-build-auto` under **folder+id dispatch**: the coordinator supplies `spec_folder` and
`story_id`, and the worker resolves everything else from `{spec_folder}/stories.yaml` and `SPEC.md`.

| # | Step | Engine | Exit condition |
|---|---|---|---|
| 1 | Plan | `bmad-build-auto` + `Halt after planning.` | Spec frontmatter reads `status: ready-for-dev` |
| 2 | Build | `bmad-build-auto` given the spec path | Spec frontmatter reads `status: done` |
| 3 | Panel | `bmad-code-review` | Panel adjudicated, zero unresolved must-fix |
| 4 | Publish | — | Branch pushed, PR open, story-closing checklist answered |
| 5 | CI | — | All checks conclude green on the pushed head SHA |

### Engine rules

- MUST judge a step from the spec's frontmatter `status`. A worker's chat report MUST NOT settle it.
- Every step MUST go to a **fresh** worker, and a fix round MUST NOT go back to the worker that produced the
  code. The spec carries everything the next worker needs, and inherited context is how a step stops judging
  the artifact on its own merits.
- MUST launch every worker with its Unattended flag, and MUST confirm each started from observed activity —
  never from a readiness match alone.
- MUST NOT dispatch to a CLI that cannot spawn subagents. `blocked / no subagents` is a CLI capability failure,
  not a story failure: re-dispatch the same step on the other CLI in that row.
- MUST NOT reorder or drop a step. A step with nothing to do MUST be reported as such, not skipped silently.
- A spec already at `status: blocked` MUST be repaired and its status reset before re-dispatch.

### What every worker brief MUST carry

Three rules this corpus adds. All three MUST be stated in the dispatch of any step that writes code.

- **Debugging is conditional, never a phase.** When a test or build fails and the cause is not known, the
  worker MUST run `wdi-systematic-debugging` before proposing any fix. A third failed fix attempt is the signal
  to escalate, not to try a fourth.
- **The corpus is not the worker's to change.** A worker MUST NOT edit `.what/`, `.how/`, or an `applied`
  `DEC-`. A deviation from the SDD or an `AD-N` is **reported**, and it becomes a `DEC-` through
  `wdi-decision` — never absorbed as a code patch.
- **Verification is run, not assumed.** The commands are this product's, and they live in
  `.constitution/project/codebase-stack-guide.md` — build, test, and whatever the front end needs, each with
  the directory it runs from. A skill MUST NOT carry one product's build line. A green registry workflow
  MUST NOT be reported as proof the code compiles; they answer different questions.

### Step 1 — plan

- MUST include `Halt after planning.` Without it the worker runs straight through implementation and Step 2
  loses its gate.
- Validation is not a separate step. Step-02's READY-FOR-DEVELOPMENT gate verifies the spec, repairs it once,
  and re-verifies. MUST NOT wrap a second validation loop around it.
- `blocked / spec failed ready-for-development standard` means that repair did not converge. MUST escalate the
  failing criteria; MUST NOT hand-patch the spec into a pass.
- `blocked / intent gap` MUST reach the owner with the worker's unanswered questions verbatim.

### Step 2 — build

- MUST dispatch with the spec file path and the three brief rules above. The worker commits locally and **never
  pushes**.
- `blocked / review repair loop exceeded 5 iterations` means its internal loop did not converge. MUST escalate;
  MUST NOT re-dispatch for a sixth.
- On `blocked / intent gap` the worker has reverted the code and saved a patch file. MUST retrieve that patch
  path from the triage log before escalating — the work is recoverable, and losing it costs the whole step.

### Step 3 — panel, then judge

Panel composition follows `risk_accepted`: at `low` a two-reviewer panel is **required** on the code; at
`medium` and `high` it is available and SHOULD be used when the diff touches money, personal data, or a third
party. The Agent Rules `bmad-code-review panel` section defines the pairing, and it MUST be followed exactly —
the worker's own review layers are same-family by construction and never satisfy it.

- MUST adjudicate every contested finding by reading the cited lines. Votes MUST NOT settle a finding. A finding
  neither reviewer can locate in the diff is dismissed with that reason stated.

**MUST return to Step 2:**

- Breaks a story AC, or contradicts the SPEC, the SDD, an `AD-N`, or an `applied` `DEC-`
- Wrong behaviour, crash, or data loss reachable from the running app
- Corpus drift: an `LC` touched but not registered, a contract changed in code but not in `02-contracts/`, a
  screen added without its `01-ux/` entry
- An enum value rendered straight to the screen instead of read off its label map
- Payment or private data reaching a tracked file
- A weakened guard, or a test that cannot fail — including one asserting a literal instead of the behaviour it
  claims to cover

**MUST record as follow-up and MUST NOT return to Step 2:** style or naming with no behaviour delta · a
refactor outside this story's scope · a pre-existing defect this story did not touch · a speculative risk with
no reachable path.

A must-fix MUST return as a **spec amendment**, never a chat instruction: amend the sections outside
`<intent-contract>`, append a `## Spec Change Log` entry naming the finding, reset `status` to `ready-for-dev`,
then re-dispatch. Content inside `<intent-contract>` is the owner's alone; a must-fix rooted there is an intent
gap and goes to the owner.

Cap: **2 return trips.** MUST re-run the whole panel after each fix round — a fix introduces defects. On hitting
the cap MUST escalate and MUST NOT open a PR carrying an unresolved must-fix.

### Step 4 — story-closing checklist, then push and PR

The checklist is **three items** now, and it MUST be answered before the PR opens:

1. A decision worth remembering? → `wdi-decision`. A story contradicting an `AD-N` **stops** rather than
   closing.
2. A trap for the next agent? → recorded where the next agent will read it.
3. Test names matching what `waves.yaml` records?

The five items that left this list moved to Phase 4, where the information actually exists.

- MUST run the repository's commit/push audit before `git push`: refuse the forbidden paths, run the guard test,
  fix content on failure. A failing guard is a finding about the content — MUST NOT weaken the guard or the test.
- MUST NOT push to `main`/`master`, MUST NOT force-push, MUST NOT merge.
- The coordinator MUST be the hand that pushes and opens the PR.

### Step 5 — watch CI, then judge

- MUST wait for every check to conclude, then confirm the checks belong to the **pushed head SHA**. A green
  report from a stale run is a false report.
- `korpus.yml` validates the corpus, not the code. Build and test evidence comes from Step 2's own runs.
- Classify each failure before acting: a defect from this change → Step 2, with `wdi-systematic-debugging` when
  the cause is unknown · infrastructure or flake → re-run **once**, and MUST NOT patch code to mask it; a second
  identical failure is a defect · a guard failure → fix the content.
- Cap: 2 return trips. On hitting the cap MUST report red honestly rather than keep pushing.

### Parallel stories

Stories without a `depends_on` path between them MAY run at once, but four conditions MUST hold: each worker in
its own worktree; V11 green for every pair released together; the first story of an epic already `done` so later
stories inherit its code map; and no shared registry write in flight.

The pattern that MUST be preferred: run the biggest blocker alone first, let its shape decisions land, then fan
out.

## Phase 4 — Close the wave

Run in this order and stop at the first failure:

1. **Registry catch-up.** Every `LC` the wave's design named is registered in `components.yaml`, and every
   `touches` value resolves — V12. This is the moment those questions have answers.
2. **Inventories refreshed from code.** Run `.constitution/method/scripts/inventory.py`. The plan-versus-reality
   difference is reported as a finding; it MUST NOT be patched into agreement by hand.
3. **Structure maps refreshed** through `wdi-init` intent `structure`, if a base folder was born or removed or a
   key file moved.
4. **Distillation.** Every applicable row of the ownership table in `corpus-guide.md` has been landed by its
   owner. Anything durable in the spec folder leaves it now, or dies with it.
5. **Retrospective.** On wave `L`, dispatch `bmad-retrospective` and archive `RETROSPECTIVE.md` as
   `RTR-<wave>.md` in `.control/reports/`. On `S` and `M` it is advisory — V19 says so, and skipping it MUST be
   stated rather than silent.
6. **RTM green.** Every traceability row for this wave is closed. New risks are in the risk register with an
   owner.
7. Mark the wave `status: closed` in `waves.yaml`.

- You MUST NOT close a wave with an open distillation row. The whole point of an ephemeral working layer is that
  durable truth leaves it first.
- You MUST NOT reopen a closed wave to add scope. Scope arriving late opens a new wave, or goes through
  `wdi-decision` if it invalidates what is already planned.
- A change invalidating more than 30% of a wave's stories MUST go through `wdi-decision`, not a patch to
  `waves.yaml`.
- Fast Path work is recorded as `fastpath` with no gates. If an `FR` turns out to be touched, the work MUST stop
  and be raised to a wave `S`.

## Red Flags — STOP

- "One reviewer approved, good enough"
- Judging a step from a chat report instead of the spec's frontmatter `status`
- Dispatching Step 1 without `Halt after planning.`
- Editing content inside `<intent-contract>` on the owner's behalf
- A worker editing `.what/`, `.how/`, or an `applied` `DEC-` to make its code fit
- Fixing a failing test without knowing why it failed
- Opening a PR with an unresolved must-fix, or before the story-closing checklist is answered
- Editing a guard, a test, or an assertion to turn something green
- Reporting green without checking the head SHA, or reading green `korpus.yml` as a passing build
- A reviewer from the same CLI family as the builder
- Dispatching a worker without its Unattended flag
- Closing the wave without the registry catch-up in Phase 4 — that is where five checklist items now live
- Letting `SPEC.md` state something `.what/` and `.how/` do not

**Each of these means: stop, return to the step or phase that owns it, or escalate to the owner.**

## Output

MUST follow the Agent Rules `Answer Closing` block, carrying these additions:

- **what was done** — wave, `FR` satisfied, every story with its branch and PR URL, what the code now does
- **what blocked it** — every step that looped, every dismissed finding and why, anything left red, and every
  Phase 4 item that did not pass
- **what comes next** — every finding recorded as follow-up, every entry in a spec's `deferred` list, every
  story-closing item routed to another skill, and the plan-versus-code inventory differences. A follow-up absent
  here is a lost finding.

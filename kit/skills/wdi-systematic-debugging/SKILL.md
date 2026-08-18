---
name: wdi-systematic-debugging
description: Use when encountering any bug, test failure, build failure, or unexpected behavior, before proposing any fix. Covers root-cause investigation, hypothesis testing, and the escalation rule when repeated fixes fail.
---

# Systematic Debugging

BMad has no debugging workflow — `bmad-build` assumes you already know what to build. This skill
covers the gap: something is broken and the cause is unknown.

## The Iron Law

**NO FIX WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

You MUST complete Phase 1 before proposing any fix. A fix that treats a symptom is a failure even
when the symptom disappears.

## When to use

Use for any technical issue: test failure, production bug, unexpected behavior, performance problem,
build failure, integration failure.

**Its home is G5, but its trigger is not positional.** Most invocations happen while coding, and
that is why `AGENTS.md`, `bmad-build`, and the ship-story orchestration carry this rule in their
worker context. What actually fires it is a pair of conditions — *something is broken* **and** *the
cause is unknown* — so it MAY be invoked in any stage, by anyone, to investigate: a red
`validate.py` while writing an SRS at G3, a `wdi-reconcile` report that makes no sense, a
generator producing an empty timeline. None of those wait for G5, and none of them are a
misuse of this skill.

The second condition matters as much as the first. A test failing because of a missing import is not
a trigger — you already know the cause. A test failing for a reason you cannot name is.

Nor does the finding always land in code: three of the four `root_cause` categories send it back to
`.what/` or `.how/` — see [Where the finding lands](#where-the-finding-lands).

Use it *especially* when the pressure argues against it — an emergency, an "obvious one-line fix", a
previous fix that did not hold. Systematic debugging is faster than guess-and-check, and the
pressure cases are exactly where guessing costs the most.

A simple-looking bug has a root cause too. You MUST NOT skip phases because the issue looks small.

## Phase 1 — Root cause investigation

1. **Read the error completely.** Full stack trace, line numbers, file paths, error codes. The
   answer is often already in it.
2. **Reproduce it.** Exact steps, every time. If it is not reproducible, gather more data — you
   MUST NOT proceed on a guess.
3. **Check what changed.** `git diff`, recent commits, new dependencies, config, environment.
4. **Instrument the boundaries.** When more than one component is involved (browser → API →
   service → database; CI → build → deploy), add logging at *each* boundary before proposing
   anything: what enters, what exits, what config propagated. Run once to find *which* boundary
   fails, then investigate only that one.
5. **Trace the bad value backward** to where it originates — see
   [references/root-cause-tracing.md](references/root-cause-tracing.md). Fix at the source, never
   where the symptom surfaced.

## Phase 2 — Pattern analysis

1. Find working code in this repo that does the same kind of thing.
2. Read the reference implementation **completely**. Skimming produces partial understanding, and
   partial understanding produces the next bug.
3. List every difference between working and broken, however small. You MUST NOT dismiss a
   difference as irrelevant before testing it.
4. Name the dependencies the broken path assumes: config, environment, state, ordering.

## Phase 3 — Hypothesis

1. State one hypothesis in writing: "X is the root cause because Y."
2. Test it with the **smallest possible change**. One variable at a time.
3. Worked → Phase 4. Did not work → form a *new* hypothesis. You MUST NOT stack a second fix on
   top of a failed one.
4. If you do not understand something, say so plainly and investigate further. Pretending to know
   is what produces fix #4.

## Phase 4 — Implementation

1. **Write the failing test first.** Simplest reproduction that fails for the right reason. Run it
   and confirm it fails before writing any fix. A fix without a test that failed first does not
   stick and cannot be proven.
2. **One fix, addressing the root cause.** No bundled refactoring, no "while I'm here" improvements.
3. **Verify with evidence.** The test passes, no other test broke, and you have the command output
   to show it. Claiming success without the output is prohibited.
4. **If the fix fails, count your attempts.**
   - Fewer than 3 → return to Phase 1 with what you now know.
   - **3 or more → STOP. Do not attempt fix #4.**

## Phase 5 — Record the finding

An investigation that ends in chat has to be repeated. Before you close out — whether the fix landed
or the three-fix rule stopped you — record what you found in `.control/registry/defects.yaml`. This
is the only registry write this skill owns, and it exists so one question can be answered with a
number rather than a memory: **how many of our defects turned out to be a wrong requirement rather
than wrong code.**

### Find the row, or open one

A defect found by a tester is usually already there, carrying only `id`, `title`, `found_in`, and
`reported`. Anyone MAY open such a row without running any skill, and an empty `root_cause` is a
legitimate state meaning *not yet diagnosed* — you are the step that fills it, not the step that
guards it. When no row exists, open one yourself, taking the next number in the `BUG-` sequence
(`HOT-` when it arrived through the hotfix path).

You MUST NOT require a row to exist before investigating. A defect nobody recorded is still a
defect; refusing to work until the paperwork is right is how the file becomes a formality.

### Write three fields, and only these three

| Field | Where it comes from |
|---|---|
| `root_cause` | Your Phase 1–3 conclusion, in the four categories of the table above |
| `violates` | The `FR-` or `UC-` the defect breaks. MUST be filled for `requirement` and `architecture`: a defect that violates something without naming what cannot be traced back to the corpus, and V20 fails it |
| `fix` | `fastpath` for a pure code defect, the wave id otherwise. The table above already decides this — `requirement` and `architecture` MUST NOT be `fastpath` |

You MUST NOT write a closure date. It is derived from the history of `defects.yaml` itself by
`.constitution/method/scripts/timeline.py`, and a hand-written date would be a second home for one fact —
the stored copy being the one that goes wrong.

You MUST NOT edit `title`, `found_in`, or `reported`. Whoever opened the row owns those; correcting
them silently erases what was actually reported.

### `status: fixed` follows the route, not the merge

The moment the patch merges is not the moment the defect closes. What closes it depends on the row's
own `root_cause`:

| `root_cause` | Closes when |
|---|---|
| `code` | The failing test from Phase 4 passes and the fix is merged |
| `requirement` | The `FR-` or `UC-` in `violates` has actually changed — the code alone MUST NOT close it |
| `architecture` | The `DEC-` is `accepted` and named on the row. V20 fails a `fixed` row without one |
| `environment` | The handling is in place and the monitoring exists |

Setting `fixed` before its row's condition is met is the failure this whole registry exists to
prevent: it turns "we patched the code" into "the requirement was right all along".

### When the three-fix rule stopped you

You MUST still record. The rule triggering *is* the finding — `root_cause: architecture`, `violates`
naming what the architecture broke, and the row left `open` until the `DEC-` exists. An escalation that
leaves no trace looks identical to a bug that was never investigated.

## The three-fix rule

Three failed fixes is not three failed hypotheses — it is a signal that the architecture is wrong.

Symptoms: each fix uncovers new coupling or shared state somewhere else; each fix needs "a bit of
refactoring" to land; each fix creates a new symptom elsewhere.

When this happens you MUST stop and raise it with the owner rather than continue. In this project's
terms, the outcome is a `DEC-` — a correction of course is one too — not another patch.

## Where the finding lands

| What the root cause turns out to be | Where it goes |
|---|---|
| Genuine code defect, no artifact was wrong | Fast Path — fix, test, done |
| A requirement was missing or wrong | Back to the Impact Matrix in `.constitution/method/document/delivery-flow-guide.md`; the FR/UC changes before the code does |
| An architecture decision was wrong | `wdi-decision`, which wraps `bmad-correct-course`; MUST NOT be absorbed as a code patch |
| Environmental, timing-dependent, or external | Document the investigation, implement handling (retry, timeout, clear error), add monitoring |

These four categories are exactly the values of `root_cause` in `.control/registry/defects.yaml`.
Phase 5 is where your verdict lands in that file.

The last row is real but rare. Most "no root cause" conclusions are incomplete investigations —
treat that verdict with suspicion in yourself.

## Red flags — stop and return to Phase 1

If you catch yourself thinking any of these, the process has already broken down:

| Thought | Reality |
|---|---|
| "Quick fix now, investigate later" | The first fix sets the pattern. There is no later. |
| "Just change X and see if it works" | That is guessing with extra steps. |
| "It's probably X, let me fix that" | Seeing a symptom is not understanding a cause. |
| "I'll skip the test and verify manually" | Untested fixes regress silently. |
| "Several changes at once saves time" | You will not know which one worked, or what else broke. |
| "The reference is long, I'll adapt the pattern" | Partial reading guarantees the next bug. |
| "One more fix attempt" (after 2+) | Three failures means the architecture is the problem. |
| "Emergency — no time for process" | Thrashing is slower. Always. |

Signals from the owner that mean the same thing: *"stop guessing"*, *"is that actually
happening?"*, *"will that show us anything?"*, *"we're stuck?"*

## Supporting techniques

| File | Use when |
|---|---|
| [references/root-cause-tracing.md](references/root-cause-tracing.md) | The error surfaces deep in a call stack and you must trace backward to the origin |
| [references/defense-in-depth.md](references/defense-in-depth.md) | Root cause is found and you are deciding where validation belongs |
| [references/condition-based-waiting.md](references/condition-based-waiting.md) | Flaky timing, arbitrary sleeps, race conditions |
| [references/find-polluter.sh](references/find-polluter.sh) | A test passes alone but fails in the suite — bisects to find the polluting test |

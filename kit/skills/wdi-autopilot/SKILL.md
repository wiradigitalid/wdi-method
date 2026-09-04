---
name: wdi-autopilot
description: Use when the owner wants the agent to carry the product from where it stands to every FR delivered, without being asked a question in between. Two doors — a preflight that ends in one mandate the owner accepts, then unattended iterations fired by a loop, each working as far as it safely can. One run, one branch, one PR. Every decision the agent takes lands in one ledger the owner reviews in parallel, never as a prompt.
---

# WDI Autopilot

The method spends owner time at five gates. This skill spends it at **two points instead**: one **mandate**
before the work, one **review of the result** after it. Between them the agent decides, records, and keeps
going. Nothing else in the method changes — the same skills write the same documents, the same validators
hold, the same panel reviews the code. What changes is who answers when a skill would otherwise stop and ask.

Two doors, and one fact in the registry picks the door: **is there a `DEC-` of `type: mandate` at
`status: accepted` whose `expires` has not passed?**

| Door | When | Does | Asks |
|---|---|---|---|
| **Preflight** | No active mandate | Checks everything, prints one page, waits for the owner's confirmation, writes the mandate, starts the loop | Yes — this is the only place this skill MAY ask |
| **Iteration** | Active mandate | Reads the registry and the ledger, works from where the last iteration stopped for as long as it safely can, records, returns only at one of three stops | **Never** |

Typing `/wdi-autopilot` while a mandate is active opens the iteration door, not the preflight. To change a
setting, the owner supersedes the mandate with a new one — `wdi-decision` owns supersession.

## Door 1 — Preflight

Run every check, then print **one page**. A check that fails is printed with what fixes it; the page MUST
NOT start the loop while any row in the first two groups is red.

### What is checked

| Group | Row | Red when |
|---|---|---|
| **Engines** | BMad installed; every `wdi-*` skill the run will call present | A wrapper is missing — name it and `npx wdi-method update` |
| | `to-spec` · `to-tickets` · `implement` found, with the **path** of each `SKILL.md` | Not found. Name the two install paths `wdi-build` names |
| | A route past `disable-model-invocation` — see below | Neither route is available |
| | The tracker the engines publish to is configured — `docs/agents/issue-tracker.md`, written once by `/setup-matt-pocock-skills` | Missing. `to-tickets` would stop to ask for it, and this skill never asks; the owner runs the setup before confirming |
| | Reviewers separate from the builder can be dispatched | The session cannot spawn a second agent and any touched component is `risk_accepted: low` — Step 3 of `wdi-build` would block |
| **Position** | `gates_passed` in `index.yaml`, `g4_passed` per component, validators green (`validate.py`) | A red validator. Name it; autopilot MUST NOT start on a corpus already red |
| | An isolated worktree | A shared checkout. `wdi-build` refuses one, so this skill refuses earlier |
| | `from_gate` — the first gate the run will hold itself | Below the last passed gate. Default: the gate after the last one passed |
| **Settings** | `scope` — the `FR` ids to deliver, or `all` | — (default `all` open `FR`) |
| | `parked` — what stops for the owner instead of being decided: any of `promise` · `ad-n` · `sensitive` | — (default **empty**: full authority) |
| | `smoke_test` — `agent` or `owner` | — (default `agent`) |
| | `loop` — the interval between iterations | — (default `5m`) |
| | `expires` — the date the mandate lapses | — (default 7 days from today; a `/loop` task expires then too) |
| | Where the ledger and the final report will be written | — |
| | The **run branch** — `autopilot/<mandate-id>` in the isolated worktree — and that the run will open **one** PR from it | The branch already exists with commits nobody can account for |
| **Runtime** | The session runs with permission prompts bypassed | Cannot be verified from inside the session. Printed as a line the owner confirms |

**Every row arrives with its default already in it**, and the owner changes only what they want changed —
the same rule the installer follows. A preflight that asks fourteen questions one at a time has failed.

### The route past `disable-model-invocation`

The three engines carry `disable-model-invocation: true`. That flag blocks the Skill tool — for this session
and for every subagent — and no setting lifts it. It does **not** block reading the file. Two routes exist,
and preflight names which one it found:

| Route | How | Trade |
|---|---|---|
| **Read and follow** — preferred | The builder brief says: *read `<path>/SKILL.md` and carry out its process*. The engine's rules arrive whole; only the trigger changed | Nothing in the plugin is touched; the author's updates still arrive |
| **Copy into the repo** | `npx skills@latest add mattpocock/skills` copies the skills under the repo's skill folder; the flag is removed from the three copies, and the project skill `/to-spec` coexists with the plugin's namespaced one | The copies stop receiving the author's updates |

The `to-tickets` quiz — granularity and blocking edges — is **answered by this skill**: ticket count from the
size table in `delivery-flow-guide.md`, edges from `depends_on` and `touches`. Each answer is one ledger row.

### Confirmation becomes the mandate

On the owner's confirmation, and not before:

1. Open a `DEC-` through `wdi-decision`, `type: mandate`, at `status: accepted`. `accepted_by` names the
   owner — a person and a date, the way `risk_accepted_by` does. **The mandate is the one `DEC-` that MUST
   NOT be accepted by delegation** (`mandate-accept`). Its parameters — `from_gate` · `scope` · `parked` ·
   `smoke_test` · `loop` · `expires` — live **only** on its row in `decisions.yaml`; the file carries
   Decision, Why, and Cost, and points at the row. One fact, one home.
2. Write the ledger header — see § The ledger.
3. Start the loop. In Claude Code, invoke the `loop` skill with `<interval> /wdi-autopilot`. Where that is
   not available, print the command for the owner to type, and name the alternative the platform has:

```
/loop 5m /wdi-autopilot
```

The interval is the **pause between** iterations, not the length of one. An iteration that outlives it
finishes first; the next firing waits.

## Door 2 — One iteration

Read `.control/generated/status`, the mandate row, and the ledger's last entry. Then work the table below
**from the top, for as long as the work can be done safely** — not one row and return. The loop is a safety
net that restarts a run that died, not the pacer of one that is alive; an iteration that stops after one step
while work remains turns a five-minute interval into five minutes of waiting per step.

An iteration returns at exactly **three stops**, and names which:

| Stop | Means |
|---|---|
| **Done** | Every `FR` in scope is closed, or only parked rows remain — go to § Finish |
| **Capacity** | The session's context is near its limit, or a dispatched step cannot be spawned here. The ledger's last row is a boundary the next firing resumes from |
| **Blocked** | A step failed at its cap — two return trips in `wdi-build`, a third failed fix — and is recorded as blocked. The next firing tries the next runnable row, not the same one |

The ledger is what makes the next firing continue rather than restart, so every step boundary lands there
**before** the next step starts.

### Faster is allowed; unsafe is not

Everything that shortens the run without changing what it produces is in scope: dispatching a step to a
subagent, running the review panel while the next ticket's tests are being written, building tickets with no
blocking edge between them at once, holding G3 for several components in one pass. Four limits, all already
the method's, and none of them relaxes here:

- **`wdi-build` § Parallel tickets sets the conditions** — each concurrent builder in its own worktree,
  `parallel-tickets-blocked` green for every pair released together, the shape-setting ticket closed first, no shared registry
  write in flight. The coordinator holds every registry write and every merge into the run branch, serially.
- **Specs run in parallel only where `depends_on` says they may.** A wide refactor's batches never do.
- **Every step is judged from the artifact**, never from a builder's report — the same rule, whoever runs
  the step. A step whose reviewer is also its builder is a self-report and does not count.
- **Nothing lands on the run branch red.** A ticket merges into it only with its tests green and the full
  suite green once; a merge that turns the branch red is reverted, not patched forward.

### One run, one branch, one PR

A mandate is **one unit of work**, and it reaches `main` through **one door**: a single PR from the run
branch, which the **owner** merges after the final review. This is what makes the result reviewable as a
whole instead of as a stream of PRs nobody read.

| In `wdi-build` | Under a mandate |
|---|---|
| Step 4 pushes a ticket branch and opens a PR per ticket | The ticket is committed to the run branch — directly, or merged in from its own worktree by the coordinator. The ticket-closing checklist is still answered first. **No PR per ticket** |
| Step 5 watches CI per PR | The coordinator pushes the run branch **at every spec close**; the first push opens the one PR as a **draft**; CI is watched per push, on the pushed head SHA, and judged exactly as Step 5 says |
| `MUST NOT merge` | Holds harder. The run never merges to `main`; the owner does, once, after § Finish |

A second PR is a red flag. Where a change cannot ride the run branch — a hotfix `main` needs today — it is
reported for the owner, not opened by the run.

| The registry says | Do |
|---|---|
| `from_gate` is G1 and no brief | `wdi-problem`. Then **hold G1**: answer its ★ questions in the ledger, record `G1` in `gates_passed` |
| G1 passed, no PRD for the scope | `wdi-product` intent `prd` — `wdi-ux` first where the interface is the promise. Hold G2 the same way |
| G2 passed, no components | `wdi-init` intents `component` · `mode` · `risk`. Each `mode` and `risk_accepted` is a ledger row with its reason |
| Components, no catalogue or spine | `wdi-blueprint` `catalog`, then `platform`. Hold G3 |
| G3 passed, a component above `catalog` lacks depth | `wdi-component`. Hold G4 for that component; set `g4_passed` |
| G4 clear for a candidate row | `wdi-report` intent `estimate`, pick the top candidate row, `wdi-build` for it — **unattended branch** |
| A spec is open | Continue `wdi-build` from its next phase or ticket. The frontier is read from the tickets |
| A spec just closed | `wdi-reconcile` over the gate scope; carry every drift finding to its owning skill in one edit pass |
| Every `FR` in scope closed, or only parked rows remain | § Finish |
| `expires` passed | § Finish, with the run marked lapsed |

**Holding a gate here means answering its checklist, not skipping it.** Every ★ question is answered in the
ledger, `yes` or `change`; a `change` is acted on in the same iteration. The ★ questions a validator answers
are answered by the validator, never re-derived.

### What the agent decides, and what it does with the answer

| Would have asked the owner | Under a mandate |
|---|---|
| A gate checklist | Answered and recorded, as above |
| Seams, testing decisions, the `to-tickets` quiz | Decided; one ledger row each |
| An `owner` row in `wdi-question` | Answered with a default, filed in `assumptions.md` with its cost and `under: DEC-<mandate>`, closed in `answered.md` in the same pass |
| Code right, document wrong (`wdi-build` § When the code turns out to be right) | Decided; the owning skill edits in the present tense; one ledger row naming the promise that moved |
| A `DEC-` to accept | Accepted with `accepted_by: DEC-<mandate>`, then applied in the same pass |
| Drift with a clear right side | Carried to the owning skill |
| A conflict with no right side | A `DEC-`, accepted by delegation |
| Anything in `parked` | **Not decided.** One row in the final report's parked list; the `FR` it holds is skipped and the run moves to the next |

Three things the mandate MUST NOT reach, whatever `parked` says: a guard, a test, or an assertion edited to
turn something green; a ticket's `satisfies` amended to make a must-fix go away; a builder editing `.what/`,
`.how/`, or an `applied` `DEC-`. `wdi-build` owns all three and this skill adds no exception.

### Recording is not optional here

Under supervision a decision nobody recorded is normal, because the owner was in the room. Here the owner
was not, so **every decision this skill takes for them is a ledger row** — that is the whole price of the
mandate. The `DEC-` threshold in `decision-guide.md` still decides which of them also become a `DEC-`; the
ledger decides nothing and records everything.

## The ledger

`.control/memlog/autopilot-<YYYY-MM-DD>.md`, one per mandate. A memlog is a run log — *which skill ran, and
what it decided while running* — and this is exactly one. `memlog-home` holds it where every memlog lives.

Frontmatter `artifact:` names the mandate's `DEC-` file — `memlog-home` demands it of every memlog. Header: the
mandate id, its parameters as a pointer to the row, the run branch, the start commit. Then one row per
decision, appended, never rewritten:

| Column | Holds |
|---|---|
| When | Iteration number and commit |
| Where | The skill and step that would have asked |
| Decided | One sentence, present tense |
| Instead of | The alternative that lost, one line, or `—` |
| Cost if wrong | One line. `one setting changes` is a valid answer and a short one |
| Landed in | The files edited, or the `DEC-` / `OQ-` id |

The owner MAY read it at any time while the loop runs. **Reading it never pauses the run**; disagreeing with
a row is a new `DEC-` that supersedes, opened through `wdi-decision`, and the next iteration applies it.

## Finish

When the table above reaches § Finish:

1. **Smoke test.** At `smoke_test: agent`: run the application with the commands
   `.constitution/project/codebase-stack-guide.md` names, exercise every closed `FR`'s proof of done from
   the PRD, record pass or fail per `FR` in the ledger. At `owner`: run nothing; the test script below is
   the whole deliverable.
2. `validate.py --generate`, then `wdi-report` intent `progress`.
3. Raise the mandate to `applied`, `touches` naming the ledger.
4. Push the run branch, wait for CI to conclude on that head SHA, and mark the one PR **ready for review**.
   Red CI here is reported red; the run MUST NOT patch to turn it green at the door.
5. Cancel the loop: in Claude Code, the `loop` skill's cancel; elsewhere, tell the owner the loop has nothing
   left to do.
6. Write the final report as the Output below. The owner merges; the run never does.

## Red Flags — STOP

- Asking the owner anything through the iteration door
- Starting the loop before the mandate is `accepted`, or on a red validator
- A mandate accepted by delegation, or with no `expires`
- Deciding something the mandate parks, or parking something the mandate did not
- A decision taken and not written to the ledger
- Restarting from the first row instead of reading the ledger's last entry
- Returning after one step while work remains and none of the three stops applies
- A second PR, a ticket branch pushed on its own, or any merge into `main` by the run
- Merging a red ticket into the run branch, or patching the branch forward instead of reverting the merge
- Parallel builders sharing a worktree, or a registry written by anyone but the coordinator
- Claiming a Skill-tool invocation of `to-spec`, `to-tickets`, or `implement` — the route is read-and-follow
  or a repo copy, and the ledger names which
- Editing a guard, a test, or an assertion to go green — no mandate reaches that
- Answering a ★ question a validator already answered

## Output

Preflight: the one page, then the mandate id and the loop command actually issued.

Iteration: the steps taken in order, the ledger rows added, which of the three stops ended it and why, and
what the next firing will find.

Finish, following the Agent Rules `Answer Closing` block and carrying:

- **what was done** — the one PR, its branch and head SHA, and CI's verdict on it; every `FR` closed, with
  its spec; the smoke test result per `FR`, or the words *not run, by mandate*; the ledger path and its row
  count
- **what blocked it** — the parked list, each with the `FR` it holds and the decision the owner owes;
  anything left red; whether the run lapsed at `expires`
- **what comes next** — **the test script**: for every closed `FR`, its proof of done from the PRD as one
  step the owner performs; then every follow-up `wdi-build` recorded, and the plan-versus-code inventory
  differences

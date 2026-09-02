---
name: wdi-report
description: Use when someone needs numbers about this project — progress for a client update, an estimate before the work is committed, task rows ready to paste into a tracker, or a self-contained brief/PRD deliverable. Four intents, progress and estimate and dispatch and render. Never invents a number.
---

# WDI Report

Four intents. The first three are fenced off from each other **because their rules are opposite**; `render`
answers a different question from all three — not a number, a document.

| Intent | Answers | Rule |
|---|---|---|
| `progress` | What has moved, what is late, how much is proven | **Entirely derived.** MUST NOT write one number, date, or percentage that did not come from the registry or from git |
| `estimate` | How big this is, what the tasks are, how much load, what the timeline looks like | **Forward-facing.** MUST state which inputs exist and how precise that makes it, and MUST be labelled an estimate |
| `dispatch` | Task rows ready for an outside tracker | Reads the same table as `estimate`; recomputes nothing |
| `render` | The page a human reads at each gate — brief, PRD, blueprint, SDD — and a complete SRS per component | **A projection.** Assembles the working document verbatim plus what the registry and `.control/questions/` complete; adds no fact and no sentence of its own |

Confusing the first two is the failure that split exists to prevent: a forward-looking figure presented in the
voice of a derived one is the most expensive kind of wrong.

## What owns what

| Owner | Produces |
|---|---|
| `.constitution/method/scripts/validate.py` | `generated/rtm` · `dag` · `status` · `risks` · `components` · `decisions` · `estimate` — and every page under `.what-rendered/` and `.how-rendered/` |
| `.constitution/method/scripts/timeline.py` | `generated/timeline` · `generated/report` · `.control/reports/<period>.md` |
| `.constitution/method/scripts/inventory.py` | The three inventories, derived from code |
| `wdi-reconcile` | Drift between corpus and registry — read-only, no file |
| **this skill** | The judgment on top: whether the tables are fresh enough to report on, and the human commentary written at publish time |

All three scripts are deterministic and already written. You MUST NOT hand-derive anything they produce, and you
MUST NOT write into `generated/` yourself. Your job starts where their output stops being self-explanatory.

---

# Intent `progress`

## Step 1 — Refresh, or refuse

```bash
uv run .constitution/method/scripts/timeline.py --refresh --generate
```

`--refresh` runs the validators first, so both halves of `generated/` are derived at the same commit. Read what
it prints before reading anything else:

| What it says | What you MUST do |
|---|---|
| `rtm/status not yet generated` (exit 3) | Stop. The tables cannot be built, so there is nothing honest to report |
| `git did not respond` (exit 3) | Stop. Every actual date comes from git; without it there is no time dimension |
| `the registry has uncommitted changes` | Say so in the report header. The numbers describe a working tree, not `main` |
| `tickets with no git history` | Name those tickets. They count toward promise progress but cannot appear under Proven |
| `n findings` | Report the count and, if any are red, say which gate they block |

A report built on stale tables is worse than no report: it looks authoritative and is not.

## Step 2 — Read the derived time dimension

You MUST NOT derive dates yourself. `timeline.py` reads each ticket file's history and takes the first commit whose
status left the not-started set as the start, and the commit where it became `done` as the end. `FR` spans its
tickets; `CAP` spans its `FR`, and closes only when every ticket under it is closed.

None of this is written back into any registry. A stored copy would be a second home for one fact, and the stored
copy is the one that goes wrong.

## Step 3 — Read `generated/timeline` and `generated/report`

`timeline` gives one row per `CAP`, plan beside actual, plus a gantt. `state` is `not-started`, `in-progress`,
`done`, or **`overdue`** — the last being `plan-dates`.

You MUST list every overdue row **by name**, with what it is waiting on. The script prints them individually for
the same reason: aggregating them into a count is how a slipping plan stays comfortable.

`report` gives five composed sections covering the span since the last published report: **Proven** (RTM rows that
turned green, named) · **Moved** (`CAP` and `FR` that started or closed) · **Late** · **Defects** (grouped by
`root_cause`) · **Gates** (dated from the history of `index.yaml`).

Section 4 grouped by root cause is worth reading twice: it answers how many defects were a wrong requirement rather
than wrong code, and that ratio is a fact about the method, not about the team.

The left edge is the `asof` of the newest published report. When there is none, the script says the period is
unbounded on the left, and you MUST repeat that rather than picking a date.

## Step 4 — Publish

```bash
uv run .constitution/method/scripts/timeline.py --publish weekly
```

A published report is **frozen**. It states what was true on a date, exactly like minutes. The script refuses to
overwrite one (exit 4) rather than trusting anyone to remember.

- You MUST NOT edit a published report. If it was wrong, the next report says so.
- The `## Note` block is the one part a person writes, once, at publish time, before the commit.
- Commentary MUST cite rather than restate: a slip has a cause, and that cause already lives in a `DEC-`, an
  `OQ-`, a risk, or a defect.

## Step 5 — Lead with the honest number

| Measure | Formula | Answers |
|---|---|---|
| **Progres janji** | green RTM rows ÷ total RTM rows | How much is **proven** |
| Progres kerja | tickets `done` ÷ tickets in spec | How much was worked on |
| Kesiapan gate | green validators ÷ applicable validators | Whether the next gate can open |

You MUST present **progres janji** first and label it as the one that counts. Progres kerja MUST NOT lead a
client-facing report: a ticket can be `done` while its RTM row is still red because the test has no name or the `UC`
does not exist — and that gap is exactly what the client is entitled to know.

---

# Intent `estimate`

**It runs as early as G1, and sharpens every time an input arrives.** That is what makes it useful for sizing a
project before there is a line of code.

## Step 1 — State the input, and the precision it buys

You MUST say which of these exist and stop at the honest level. Claiming precision the inputs do not support is the
one thing this intent can get badly wrong.

| Input available | What can be estimated | Precision |
|---|---|---|
| **G1** — the brief | T-shirt size · rough capability count · the first risk list | very rough |
| **+ G2** — the PRD | **The candidate task list = the `FR` list** · `estimate_mandays` per `CAP` · `must/should/could/wont` · order from `depends_on` between `CAP` | rough |
| **+ tail of G2** — components born | Tasks grouped per Product Component · **`mode` per component, so document load is counted too** · `risk_accepted` marks exposure | medium |
| **+ G3** — the blueprint | Table, endpoint, and screen counts → real implementation load, not load guessed from an `FR` count | good |
| **+ G4** — component depth | Tickets and test names → measured load | best |

## Step 2 — Inputs

`goals.yaml` (the `BG` list) · every `requirements-<slug>.yaml` (`CAP` with `estimate_mandays`, `priority`, `depends_on`, `target_release`, plus its `FR`) · `components.yaml` (`mode`,
`risk_accepted`, `risk_note`) · the three `inventory-*.md` when they exist.

`estimate_mandays` on `CAP` is the **source**, and it is used for real here rather than being decoration. When it is
absent, say so — an estimate with no mandays input is a T-shirt size, and it MUST be reported as one.

## Step 3 — The output: one task table

Written to `.control/generated/estimate.md` by `validate.py --generate`. **Default one row per `FR`**, because that
is the ideal shape of a spec and because an `FR` has had a proof of done since birth.

| Column | Content |
|---|---|
| Task | The title, from the `FR` |
| `FR` | Its id |
| Component | The Product Component |
| `mode` | That component's depth — this is what makes document load visible |
| Exposure | `risk_accepted` + `risk_note` |
| Effort | Mandays, derived from the parent `CAP`'s `estimate_mandays`, divided among its `FR` |
| Priority | From the `CAP` |
| Depends on | From `depends_on` |
| Release | The `CAP`'s `target_release` |

## Step 4 — Say what it is, and what it is not

> A row in the estimate table is a **candidate** task. A spec in `specs.yaml` is a **real** one. The first missing
> is normal; the second is not.

The table is planning, not commitment. One row MAY become one spec, and three neighbouring rows MAY be merged into
one. **That merge is a human decision made when the spec opens**, and this intent MUST NOT pretend to already know
the answer.

- Every output MUST carry the word estimate, visibly, at the top.
- You MUST NOT present a mandays figure without naming what it was derived from.
- You MUST NOT include a date this intent computed itself. Plan dates come from `planned_end` on a `CAP`; where
  there is none, the timeline is stated in sequence and dependency, not in dates.

---

# Intent `dispatch`

Reads `.control/generated/estimate.md` and `specs.yaml`. **It recomputes nothing.**

It emits rows in a form that can be pasted into an outside tracker: a **parent issue** for the spec — or the
candidate row where no spec exists yet — an **issue** per ticket where tickets exist, with its blocking edges,
labels for `FR` and `CAP`, and Fix Version from the release. A ticket is an issue and not a sub-task, because a
sub-task cannot carry the blocking relation the frontier is read from; `delivery-flow-guide.md` owns that mapping.

- Output goes **to the screen**. This intent MUST NOT write a file, and MUST NOT write to the tracker — entering it
  is a human act.
- The corpus never reads back from the tracker. **The corpus is the source of truth; the tracker is a view.**
- A row whose Task is still a candidate MUST be marked as one. A candidate pasted as a real Task is how a tracker
  fills with issues nobody committed to.

---

# Intent `render`

Produces a self-contained reader's copy of the brief or a PRD — the shape that used to be written by hand,
now assembled instead of duplicated. `brief-guide.md` § The generated deliverable and `prd-guide.md` § The
generated deliverable own what each page assembles; this intent is the one place either is actually run.

Both working templates point here by name, so this is what an owner will type:

| They ask for | They run |
|---|---|
| The full, readable brief | `/wdi-report render brief` |
| The full, readable PRD | `/wdi-report render prd` |

Either form runs the same single command in Step 1 — the argument says which page they came for, and
which path to lead the report with. It does NOT narrow what gets regenerated, and you MUST NOT pretend
it did.

## Step 1 — Generate

```bash
uv run .constitution/method/scripts/validate.py --generate
```

This regenerates the machine tables in `.control/generated/` AND every human page in `.what-rendered/` and
`.how-rendered/` — the brief, every PRD, the blueprint, every SRS, and the SDD of every component above
`catalog`. One run, not a per-document command, because the pages cite each other's ids.

## Step 2 — Report what changed

`generate()` writes `brief.md` unconditionally and one `prd-<slug>.md` per folder found under
`.what/_prd/`. Name the paths written. If a working document does not exist yet, its page says so instead
of a crash — report that as "not started" rather than a failure.

## Step 3 — Say what the page is, and is not

> This is a **projection**, assembled from `brief.md` / `prd.md`, the requirement registry,
> `.control/product-glossary.md`, and `.control/questions/`. It carries no fact the working documents and
> the registry do not already hold, and it MUST NOT be edited by hand — the next `render` overwrites it.

- You MUST NOT hand-patch a generated page to "fix" something that reads wrong. The defect is in the
  working document or the registry, and that is where it MUST be fixed.
- A reader asking for "the full brief" or "the complete PRD" wants this page, not `.what/_product-brief/brief.md`
  or `.what/_prd/<slug>/prd.md` read directly — those are now pointer-heavy working documents, not the
  deliverable.

---

## Rules

- You MUST NOT invent progress. When a table is missing or stale, name it and stop.
- You MUST NOT report `progress` in tickets. The planning layer speaks in `CAP`, `FR`, and defects; tickets are the
  execution layer and are born too late to plan against.
- You MUST NOT hand-write anything under `generated/`, `.what-rendered/`, or `.how-rendered/`. There is no exception.
- You MUST NOT re-run `--publish` to "fix" a report. The refusal is the rule working.
- When plan dates have moved since the last report, you MUST say so and point at the commit.
- When there is no previous report, say the period is unbounded on the left rather than picking a date.
- You MUST NOT mix the intents in one output. A derived number and a forward-looking one MUST NOT appear in the same
  table without the labels that separate them.

## Output

**`progress`:** the published path, the freshness commit, progres janji, then the five sections — overdue rows named
individually, never counted away.

**`estimate`:** which inputs exist and the precision that buys, the task table, and what is a candidate rather than
a commitment.

**`dispatch`:** the paste-ready rows, on screen, with candidates marked.

**`render`:** the paths written, which working documents were missing, and the projection notice above.

# WDI Method

**The review layer BMad leaves thin — documents a human reads to check a decision before code gets written, sized to what the change actually deserves.**

[BMad](https://github.com/bmad-code-org/BMAD-METHOD) decides *what* to build and *how* to build it well. WDI Method wraps it — it does not replace it — and adds the part between those two decisions and the code: inventories, a use case catalogue, a component design record, and a way to choose how much of that a given change actually needs.

> This repository is **public and generic**. It MUST NOT carry a client name, a product name, or a
> link to a private repository — product identity lives entirely in the repo that installs it.

---

## Prerequisites — two engines, and which gates need them

| Engine | What it does here | Needed from | Install |
|---|---|---|---|
| **BMad Method** | Writes the documents behind G1–G4 — brief, PRD, architecture, UX | the first skill | `npx bmad-method install` — the installer refuses to run without it |
| **mattpocock-skills** | Cuts the work at G5 — `to-spec`, `to-tickets`; runs the Fast Path — `implement` | `wdi-build` | `/plugin install mattpocock-skills@claude-plugins-official`, then `/setup-matt-pocock-skills` to name your issue tracker. The installer reports whether it found them and does not block |

No engine skill is invoked on its own. Each has a wrapper (`wdi-*`) that checks where the project is,
runs the engine, verifies what came back, and records it. The engine is the pen; the wrapper knows what
page it is on.

---

## Install

BMad first, then this — see the prerequisites above.

```bash
cd /path/to/your/product-repo
npx bmad-method install
npx wdi-method
```

The second command opens a TUI: it checks BMad, detects install versus update, asks the product name and
the document language, lets you pick agents, shows what it will write, and prints what to do next.

**Every field arrives with an answer already in it, and Enter accepts it.** On an update that answer is
what the repo already says; on a first install the product name is the folder name made readable —
`acme-billing-portal` offers `Acme Billing Portal`. Nothing is validated as required: a prompt that
refuses an empty submission while already holding a sensible default is asking you to retype something
the installer knows.

A value only changes when you actually answer. A run that does not mention language keeps the language the
repo already chose, and says so.

```bash
npx wdi-method update      # later, to take a newer method
npx wdi-method verify      # check the method files are all present
```

Non-interactive, for CI:

```bash
npx wdi-method install --yes --agents claude,codex --product "Your Product" \
  --doc-language "Bahasa Indonesia"
```

Then invoke the **`wdi-help`** skill and ask what to do next. It reads where the project actually is and
answers with the gate you are at, not with a menu.

---

## How to use it — the walk

A gate is a moment where a human reads **one page** and decides. Between gates the AI works in a
pointer-heavy working set it does not need you to read. So the walk is: run a skill, read the page it
renders, decide — advance or refine.

| # | You run | You read | You decide |
|---|---|---|---|
| 0 | `wdi-init` intent `setup` | — | the global `mode`: how deep this product goes by default |
| 1 | `wdi-problem` | `.what-rendered/_product-brief/brief.md` | **G1** — is this the problem, whose is it, and does it earn the work? |
| 2 | `wdi-product` intent `prd` — `wdi-ux` first when the interface *is* the promise | `.what-rendered/_prd/<slug>/prd.md` | **G2** — is this what we build, and how does it feel? |
| 3 | `wdi-init` intent `component` | the rows it adds to `components.yaml` | each component's `mode` and `risk_accepted` |
| 4 | `wdi-blueprint` — `catalog`, then `platform` | `.how-rendered/blueprint.md` | **G3** — does the whole hold together? **Once per product** |
| 5 | `wdi-component` — one component | `.how-rendered/<pc>/SDD-<pc>.md` | **G4** — is this how we build it? **Skipped at `mode: catalog`** |
| 6 | `wdi-report` intent `estimate` | `.control/generated/estimate.md` | which candidate row becomes the next spec |
| 7 | `wdi-build` — for that row | nothing: tickets are machine contracts. You answer `to-tickets`' quiz on granularity and blocking edges | **G5** — is it done and proven? Once per spec |
| 8 | `wdi-report` intent `progress` | the report it writes | what has moved, what is late, what is proven |

**Refine, do not advance.** When a page does not convince you, run the same skill again and say what is
wrong — it updates the document it owns. Nothing downstream exists yet, so nothing breaks. Advancing past a
page you did not believe is how every later page inherits the doubt.

**After the first pass**, steps 0–4 never run again for that product. The next component enters at step 5
(or 6, at `catalog`); a new initiative enters at step 2; a small fix touching no `FR`, `UC`, `AD-N`, or
domain model skips every gate and runs `/implement` directly — and **stops to become a spec `S`** the
moment it touches an `FR`. `wdi-help` tells you which of these you are in; it reads the registry, not you.

---

## Why the steps are in this order

- **One question per gate.** The brief answers *why*, the PRD *what*, the blueprint *the whole*, the SDD
  *how one part*, the spec *is it done*. Every document that grew unreadable did so by answering a
  neighbour's question too. A gate that asks one question can be passed in ten minutes.
- **The page you read is rendered; the page the AI edits points.** A goal lives once, in
  `goals.yaml`; the working brief says `Goals — see goals.yaml`; the rendered brief shows the goals in
  full. So the human gets a complete document and the corpus has no copies — and the validators check
  **drift against the code**, never whether two copies agree, because there are none to compare.
- **Cost follows the unit of change.** G3 is once per product because the portrait is one thing. G4 is per
  component because that is what changes when you build. G5 is per spec because that is what ships.
  Repeating the blueprint per component was the single largest waste the earlier shape carried.
- **Two knobs that never merge.** `mode` decides which gates *exist* for a component (`catalog` skips G4
  outright); `risk_accepted` decides how much *proof* a gate demands. Merged into one "rigor" dial, a
  low-risk component either drowns in ceremony or a high-risk one escapes it.
- **Estimate before build.** Step 6 derives the candidate tasks from the promises already made —
  `CAP` and `FR` — so nobody invents a backlog. One candidate row becomes one spec, three neighbours
  may merge into one, and the estimate page says so about itself: it is forward-looking, never a record.
- **The engine cuts; the wrapper frames.** `to-spec` and `to-tickets` are the best ticket-cutting
  engine we found: vertical tracer-bullet slices, blocking edges, a quiz with the owner. What a cutter
  cannot know, `wdi-build` supplies: that every component the spec touches passed G4; that every ticket
  names the `UC` it `satisfies`, so `FR → UC → ticket → test` stays one chain; that a spec restates
  promises and never makes new ones; that code is judged by the test suite going red then green, from a
  fresh context per step, never by a builder's report; and that a closed spec leaves the registry caught
  up and the inventories re-derived from code.
- **Documents follow the code.** At spec close the inventories are regenerated from what was built and
  the difference is *reported*, never patched into agreement. A record that contradicts the code is
  corrected; code is never changed to match a record.

---

## The file tree, and why

```
.constitution/
  method/            the method — overwritten by every update; never edit here
  project/           your own rules and readers — kept by every update
.control/
  registry/          SSOT for every ROW: goals.yaml · requirements-<slug>.yaml · components.yaml
                     usecases.yaml · specs.yaml · risks.yaml · defects.yaml · index.yaml
  questions/         open questions, assumptions, external prerequisites — one row each
  decisions/         DEC-N files; frozen once applied
  generated/         machine tables: rtm · dag · status · estimate · timeline — regenerated, never edited
.what/               what is PROMISED — the AI's working set, pointer-heavy, few files
  _product-brief/brief.md
  _prd/<slug>/prd.md · addendum.md
  <pc>/SRS-<pc>.md + 02-rules · 03-domain · 04-usecases · 05-scenarios
.how/                how it is BUILT — same discipline
  _platform/         ARCHITECTURE-SPINE.md · c4-l2-containers.md · inventories
  <pc>/SDD-<pc>.md + 01-ux · 02-contracts · 04-components · 05-model · 06-flows
.what-rendered/      the human's tree: brief · _prd/<slug>/prd.md · <pc>/SRS-<pc>.md — one complete page each
.how-rendered/       blueprint.md (root — it spans every component) · <pc>/SDD-<pc>.md
_bmad-output/        a skill run's working output; empties as its spec closes
.work/               scratch; empties when the task closes
<spec_folder>/issues/  one file per ticket — the tracker's payload, not yours to read
```

Three layers, and the rule that keeps them honest:

| Layer | Holds | Who writes | Who reads |
|---|---|---|---|
| **Registry** | every row — a goal, a requirement, a component, a ticket index | the skill that owns the gate | validators, renderers, every other skill |
| **Working documents** (`.what/`, `.how/`) | the prose that reasons — why, boundaries, what makes it different — and **pointers** at the rows | the owning skill | the AI |
| **Rendered pages** (`*-rendered/`) | one complete page per gate, rows filled in from their homes | `validate.py --generate`, never a hand | the human, and the client |

Why split the human's tree from the AI's: a document that is both the AI's working surface and the
human's deliverable ends up serving neither — too long to point, too gappy to hand over. Why the
registry is per initiative (`requirements-<slug>.yaml`) but goals are per product: a capability is
declared by one feature in one PRD; a goal belongs to the product before any PRD exists. Why
`blueprint.md` sits at the root of `.how-rendered/` and not under `_platform/`: `_platform` means
"belongs to no component"; the blueprint spans all of them. Why rendered pages are never a skill's
input: a skill that read a projection would be reading a copy, and the copy would start to drift the
day someone edited it. A test in this package fails if any `SKILL.md` lists a `-rendered` path as an
Input.

---

## Why WDI Method?

- **Depth separate from scrutiny.** `mode` sets how much gets written; `risk_accepted` sets how hard it
  gets reviewed. Neither is derived from the other, so a component MAY be thin on purpose and reviewed the
  hardest.
- **Ground truth over plan.** Once code exists, the tables, endpoints, and screens are **derived from it**
  — the gap between plan and reality is a finding to resolve, not an argument to have.
- **Containers that match what actually ships.** C4's containers follow deployability, not folders, and a
  component view is drawn for every container that carries more than one Product Component.
- **A gate that can be skipped honestly.** `mode: catalog` skips the component gate entirely — a fast
  default is fast because the work is genuinely gone, not nominally trimmed.
- **Decisions that don't rot.** A `DEC-` is recorded only when the reason would not survive reading the
  code, and it freezes the moment it is applied — a change of mind writes a new one rather than editing
  the old.
- **Wraps BMad, never forks it.** Every `wdi-*` skill is a wrapper around a BMad skill. Upgrading BMad
  does not strand you, and no BMad skill is meant to be invoked directly.

---

## The gap this fills

A gate is only as good as the artifact it reads. Between *"the architecture is decided"* and *"the code
is written"* there is a set of questions that decide whether a build goes straight or crooked, and they
are all **list-shaped**:

- Which use cases exist, and which of them touch money, personal data, or something irreversible?
- Which tables exist, and which component is allowed to **write** each one?
- Which endpoints exist, on which host, and which promise does each serve?
- Which screens exist, in which application?
- When a boundary fails halfway — the other side slow, absent, or lying — what does the user see?

Those questions have answers inside an architecture document and a build spec. What they usually do not
have is a **place where a person can read all of one kind at once** and notice the row that is missing,
the table with two owners, or the endpoint nobody promised.

WDI Method's whole contribution is that place, plus the discipline that keeps it honest:

| | |
|---|---|
| **Inventories** | Tables, endpoints, and screens as three flat lists — **derived from the code**, not hand-written, so the difference between plan and reality is a finding rather than an argument |
| **Use case catalogue** | One line per use case with its actor, the requirement it satisfies, and whether it is `critical` |
| **SRS / SDD** | What a component promises, and how it is built — one pair per component, in human language |
| **C4** | Context, containers, and one component view per container that carries more than one domain slice |
| **Robustness** | For the deepest mode: boundary, control, and entity objects per critical use case, before code |
| **Invariants** | A spine of `AD-N` rules that constrain every component, separate from the decisions that produced them |

---

## Two knobs, never merged

The reason a method like this usually fails is that it asks for the same depth everywhere, so people
either drown in it or abandon it. WDI splits depth from scrutiny into **two independent fields**:

| Field | Controls | Values |
|---|---|---|
| `mode` | **Document depth**, and nothing else | `catalog` · `outline` · `guarded` · `deep` |
| `risk_accepted` | **Review intensity**, and nothing else | `low` · `medium` · `high` |

| `mode` | What is written per component | G4 |
|---|---|---|
| `catalog` | Nothing. Code is written from the use case catalogue, the three inventories, and C4 | **skipped** |
| `outline` | + a decision summary and the component list in the SDD, full flows for at most 3 use cases, local rules | 20 min |
| `guarded` | + **failure behaviour for every boundary**, inherited invariants quoted verbatim, integration documents | 20 min |
| `deep` | + robustness analysis, a contract per endpoint, data dictionary, flow diagrams, state machines | 30 min |

Neither field is derived from the other, and that is the point: **a component MAY be thin on purpose and
reviewed the hardest.** A component at `catalog` skips the component gate entirely — which is what makes
a shallow default genuinely fast rather than nominally fast.

Depth is a preference and needs no defence. Accepting risk on something that touches money, personal
data, or an irreversible action is **not** free: it requires a recorded decision, and a validator checks
that the decision exists.

All twelve combinations are legal. The installed kit carries
`.constitution/method/why/mode-risk-map.md`, which puts them side by side — what each cell costs at G4,
which review lenses run, and which review traces a validator will demand.

---

## Five gates, sixteen skills

| Gate | Decides | Skill |
|---|---|---|
| **G1 Problem** | What the problem is, whose it is, why it earns work | `wdi-problem` |
| **G2 Product** | What is built, and how it feels to use | `wdi-product` · optional `wdi-ux` |
| **G3 Blueprint** | The whole portrait, once per product | `wdi-blueprint` |
| **G4 Component** | How one component is built — **skipped at `catalog`** | `wdi-component` |
| **G5 Release** | Whether it is done and proven | `wdi-build` |

Around them: `wdi-init` (scaffold, component birth, depth and risk settings, structure maps),
`wdi-decision`, `wdi-question`, `wdi-log`, `wdi-help`, `wdi-reconcile`, `wdi-review`, `wdi-report`,
`wdi-systematic-debugging`, and `wdi-upgrade` (moves a corpus written under an older kit into the current
shape — content moves, nothing is invented).

**No BMad skill is invoked directly.** Each has a wrapper, and the wrapper is what checks position,
verifies the result, and records what happened.

### Decisions, not ADRs

A decision is a `DEC-`, and **recording one is not mandatory.** The test is one sentence: *if somebody
asks in three months why it is like this, is the answer readable from the code?* If yes, it MUST NOT be
recorded — a register nobody trusts is worse than no register. One case is mandatory: contradicting an
invariant on the spine.

A `DEC-` freezes when it is applied. A change of mind produces a new one; it never edits the old.

---

## The mechanical half

`validate.py` runs twenty-six named validators — `goal-has-fr`, `cites-resolve`, `no-cycles`,
`id-allocated-once`, and the rest, each named for the thing it checks — over the registries and the
corpus, and `inventory.py` derives the three inventories from code and reports the difference against the
plan without patching either side. There is no validator that compares two copies of one fact, because
the corpus keeps no copies.

The validators exist because prose that nothing checks is prose that gets contradicted by the first
person in a hurry. Every one of them also states **the state in which it does not apply** — a rule that
demands a trace before the trace can exist is a rule that gets switched off, and a validator nobody
reads guards nothing.

---

## What is generic, and where your own rules live

`.constitution/` holds **exactly two folders**, and the folder is the whole answer to who owns a file:

| Folder | Owner | `update` | `promote` |
|---|---|---|---|
| `.constitution/method/` | the method | **overwritten** in full | carries it into the package |
| **`.constitution/project/`** | you | **never touched** — seeded once when absent | never carries it, so your rules cannot be published |

Everything in the room is yours: `project/constitution.md` (Articles 1, 2, 5 — scope, repo checklist,
method ownership), `project/codebase-*-guide.md` (stack, conventions, brownfield, protected at **any**
`status:` — `Draft` is when they actually get written), and any rule file you add.

**The seam is a folder, never a marked region inside a generic file.** Prose has no merge algebra: you
cannot "merge" your paragraph with the method's, so only a path can say unambiguously whose a file is.
`AGENTS.md` is the one exception, and only because it is a single file with nowhere else to go.

Two more things are yours, outside `.constitution/`:

| Yours | Because |
|---|---|
| `.control/registry/index.yaml` → `product:` | The product and client name live in exactly one place |
| `_bmad/custom/*.user.toml` | Your BMad overrides — TOML, so these genuinely merge: a string replaces, a list appends, a table merges per key |

`.control/` `.what/` `.how/` are never touched by an update at all — they are your state, your promises,
and your design.

The custom room takes whole files, not marked blocks inside generic ones: `AGENTS.md` can use a marked
block because it is *one* file, while `.constitution/` has fifty-odd, and blocks inside them would make
an update perform surgery in every file. A file there declares `scope: project` and a one-line
`purpose:`; to **contradict** a generic rule it must name that rule and carry the decision that allowed
it. **An empty room is a valid state** — filling it so that it gets used is the failure the rule prevents.

### Language

Two settings, both free text, both defaulting to English:

```yaml
policy:
  doc_language: "English"           # prose of working documents
  doc_filename_language: "English"  # the slug part of a document filename
```

Write whatever names the language — `English`, `Bahasa Indonesia`, `id`. What reads the value is a model,
and a model does not need a lookup table.

Always English, and never asked: method terminology, document code prefixes (`UC-`, `DEC-`), machine
markers (`[NEEDS CONFIRMATION]`, `[MISSING]`), and code identifiers. `.constitution/` itself is always
English, whatever the settings say — it travels to every repo through this package.

---

## What update does

| | |
|---|---|
| Overwrites | everything in `.constitution/method/` · the sixteen wrappers · `_bmad/custom/*.toml` · the marked block in `AGENTS.md` |
| Removes | Wrappers the method has retired — a `wdi-*` folder with a `SKILL.md` that is no longer one of the fifteen. Each removal is printed |
| Keeps | All of `.constitution/project/`, plus your initiative slug and your language choice. A setting somebody already chose is not the installer's to change behind their back |
| Never resurrects | A folder you retired. On update, absence is treated as a decision |

It prints the version it replaced, what it wrote, what it kept, and what to do next.

---

## Changing the method

**This repository is where a method change is authored** — a guide, a template, a skill wrapper, a
validator. It is proven here before publishing, against a fixture corpus the three registry scripts
actually run against:

```bash
npm test        # includes validate.py, timeline.py and inventory.py over tests/fixture/
```

The fixture is small but complete, and kept **green**, so a new finding is a regression rather than
noise. One test plants a defect in a copy and requires the matching validator to name it — a green
baseline is worthless if it is green because every check is broken.

A consuming repo then takes the change with `npx wdi-method update`, and that is where the judgement
half gets tested: whether a guide actually helps a person at G3 is only provable in use.

`promote` — pulling the method back out of a consumer — is a **rescue tool**, not the workflow. It
overwrites the whole kit from one copy, so it refuses to run without `--rescue`.
[`CONTRIBUTING.md`](CONTRIBUTING.md) records why the direction was reversed and what it cost.

**Patch releases are routine; minor and major are the maintainer's call.** This package overwrites files
in repos that already hold months of work, and the version is the only signal a reader has for how
carefully to read the diff. [`CONTRIBUTING.md`](CONTRIBUTING.md) has the detail, and
[`AGENTS.md`](AGENTS.md) states it for agents working on the package.

---

## Support and Contributing

Open an [issue](https://github.com/wiradigitalid/wdi-method/issues) for a bug or a proposal. Read
[`CONTRIBUTING.md`](CONTRIBUTING.md) before sending a pull request — it explains where a change belongs,
how versioning works here, and what to check before publishing.

## License

MIT — see [LICENSE](LICENSE). Requires Node 20+ and [uv](https://docs.astral.sh/uv/) for the Python
scripts.

[![Version](https://img.shields.io/npm/v/wdi-method?color=blue&label=version)](https://www.npmjs.com/package/wdi-method)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

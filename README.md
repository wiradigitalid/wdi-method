# WDI Method

A software delivery method for agent-driven work. It **wraps [BMad](https://github.com/bmad-code-org/BMAD-METHOD); it does not replace it.**

BMad decides *what to build* and *how to build it* well. What it leaves thin is the middle: the
documents a **human** reads to check that the decision is right before anybody writes code. WDI Method
adds that middle, and a way to choose how much of it you want.

This repository is **public** and generic. It MUST NOT contain a client name, a product name, or a link
to a private repository. Product identity lives in the consuming repo.

---

## Install

BMad first, then this. The wrappers call BMad skills; without BMad they cannot run.

```bash
cd /path/to/your/product-repo
npx bmad-method install
npx wdi-method
```

The second command opens a TUI: it checks BMad, detects install versus update, asks the product name and
the document language, lets you pick agents, shows what it will write, and prints what to do next.

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

---

## Five gates, fifteen skills

| Gate | Decides | Skill |
|---|---|---|
| **G1 Problem** | What the problem is, whose it is, why it earns work | `wdi-problem` |
| **G2 Product** | What is built, and how it feels to use | `wdi-product` · optional `wdi-ux` |
| **G3 Blueprint** | The whole portrait, once per product | `wdi-blueprint` |
| **G4 Component** | How one component is built — **skipped at `catalog`** | `wdi-component` |
| **G5 Release** | Whether it is done and proven | `wdi-build` |

Around them: `wdi-init` (scaffold, component birth, depth and risk settings, structure maps),
`wdi-decision`, `wdi-question`, `wdi-log`, `wdi-help`, `wdi-reconcile`, `wdi-review`, `wdi-report`, and
`wdi-systematic-debugging`.

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

`validate.py` runs **V1–V27** over the registries and the corpus, and `inventory.py` derives the three
inventories from code and reports the difference against the plan without patching either side.

The validators exist because prose that nothing checks is prose that gets contradicted by the first
person in a hurry. Every one of them also states **the state in which it does not apply** — a rule that
demands a trace before the trace can exist is a rule that gets switched off, and a validator nobody
reads guards nothing.

---

## What is generic, and where your own rules live

`.constitution/` belongs to the method and is **overwritten** on every update. Four rooms are yours:

| Room | Yours because |
|---|---|
| `.control/registry/index.yaml` → `product:` | The product and client name live in exactly one place |
| `constitution.md` Articles 1, 2, 5 | Scope, repo checklist, method ownership |
| `.constitution/codebase/*-guide.md` | Your stack and conventions, protected once `Accepted` |
| **`.constitution/project/`** | Any rule that binds **only this product** |
| `_bmad/custom/*.user.toml` | Your BMad overrides |

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
markers (`[NEEDS CONFIRMATION]`, `[MISSING]`), and code identifiers.

---

## What update does

| | |
|---|---|
| Overwrites | `.constitution/` guides, templates and scripts · the fifteen wrappers · `_bmad/custom/*.toml` · the marked block in `AGENTS.md` |
| Removes | Wrappers the method has retired — a `wdi-*` folder with a `SKILL.md` that is no longer one of the fifteen. Each removal is printed |
| Keeps | Everything in the table above, plus your initiative slug and your language choice. A setting somebody already chose is not the installer's to change behind their back |
| Never resurrects | A folder you retired. On update, absence is treated as a decision |

It prints the version it replaced, what it wrote, what it kept, and what to do next.

---

## Carrying a change back into this package

The published source is this repository. A product repo that holds a newer working copy of the method
promotes it here before the change counts as published:

```bash
npx wdi-method promote /path/to/the/product-repo
npm test
git commit && git push
```

`promote` copies the portable method, replaces product-named files with their generic versions, scrubs
initiative slugs, and **skips `.constitution/project/`** so a product's own rules can never be published.

---

MIT. Requires Node 20+ and [uv](https://docs.astral.sh/uv/) for the Python scripts.

---
name: wdi-upgrade
description: Use right after `wdi-method update` moved this repo to a newer method version. Finds every document and registry file still in the OLD shape, re-homes their content into the new one — registry rows out of prose, pointers where copies were, the rendered trees born — and verifies green. Runs once per version jump; safe to re-run.
---

# WDI Upgrade

`wdi-method update` does the mechanical half of a version jump: it overwrites the kit, renames files whose
content needs no judgment, seeds what is new, prunes what is retired. It stops exactly where a decision
about **content** begins — which PRD an `FR` belongs to, whether a sentence in the old brief was an
assumption or a constraint. Those are this skill's half.

**This is the one skill allowed to edit `brief.md`, `prd.md`, an SRS, an SDD, or a C4 file directly.**
Every other skill is forbidden, because a hand edit makes the memlog lie about how the document was
produced. An upgrade produces nothing: it moves sentences that already exist into the home the new
version gives them, word for word. The memlog stays true, and this skill's report is the record.

## Inputs

| Source | What it answers |
|---|---|
| `.control/wdi-method.yaml` | The version now installed — the shape everything below MUST end in |
| The `update` run's own output | The `upgrade` line lists what it detected as pending; start there |
| `.control/registry/` | What is already a row, so nothing is landed twice |
| `.what/_product-brief/brief.md` · `.what/_prd/*/prd.md` | The two documents whose shape changed most |
| `.what/<pc>/SRS-<pc>.md` · `.how/<pc>/SDD-<pc>.md` · `.how/_platform/c4-l2-containers.md` | The three that used to carry a copy of a registry table |
| `.constitution/method/document/templates/` | The target shape of every document above |

## Step 1 — Detect, and show the list before touching anything

Probe each item below; a probe is a file or heading that exists only in the old shape. List every hit
to the owner as a checklist, in the order below — it is a dependency order, and doing a later item
before an earlier one lands content in a file that the earlier item is about to change.

| # | Probe | Old shape | New home |
|---|---|---|---|
| 1 | `.control/registry/requirements.yaml` exists | one file for `BG` · `CAP` · `FR` · `NFR` · `UJ` | `goals.yaml` (`BG`) · `requirements-<slug>.yaml` per PRD (`CAP` · `FR` · `NFR` · `UJ`) |
| 2 | `specs.yaml` has `W<n>` ids, or `epics:` / `stories:` keys | pre-rename plan | re-cut through `wdi-build` — **not this skill**; report it and move on |
| 3 | `brief.md` has `## Executive Summary`, `## Vision`, `## Assumptions`, or `## Prerequisites`; or `## Goals` lists `BG-` statements | 14-section brief | 8 sections: `Why` merges Summary + Vision; Goals is a pointer, its rows in `goals.yaml`; Assumptions → `questions/assumptions.md`; Prerequisites → `questions/external.md` |
| 4 | any `prd.md` has a section **named** Document Purpose, Glossary, Non-Goals, Open Questions, or Assumptions Index — under whatever number that kit gave it — or `**Proof of done:**` under a feature | 12-section PRD with `FR` blocks | 7 sections; `FR`/`NFR` text → `requirements-<slug>.yaml`, the PRD keeps `Realizes:` ids; Glossary → `product-glossary.md`; §8/§9 → `questions/`; §1 becomes a delta |
| 5 | any `SRS-<pc>.md` `## UC Catalogue` has `\| UC-` rows | catalogue copied from `usecases.yaml` | one pointer line; the rows live in `usecases.yaml` |
| 6 | any `SDD-<pc>.md` `## Inherited Constraints` has a `Quoted rule` column, or `> ` blockquote lines under an `**AD-N — …**` heading, or the sentence `Quoted verbatim from` | `AD-N` text copied from the spine, in either of the two shapes SDDs were written in | ids only; the rendered SDD shows the text |
| 7 | `c4-l2-containers.md` has a `\| Container \| Product Components living in it \|` table | matrix copied from `components.yaml` | one pointer line |
| 8 | `.control/generated/brief.md`, `blueprint.md`, or `prd-*.md` exist | human pages in the machine folder | `.what-rendered/` · `.how-rendered/` — `render` clears the old ones |
| 9 | `.what-rendered/` or `.how-rendered/` absent | no reader's tree yet | born by `render` |
| 10 | any `.md` outside `.constitution/` cites `.control/generated/brief.md`, `blueprint.md`, or `prd-<slug>.md` | a pointer at a page that moved | `.what-rendered/_product-brief/brief.md` · `.how-rendered/blueprint.md` · `.what-rendered/_prd/<slug>/prd.md` — `cites-resolve` fails until it is repointed |

Anything not in the list is not this skill's. A brief that already has `## Why` is done; skip it.

## Step 2 — Registry first

**1 — the requirement split.** Which PRD a row belongs to is read from the rows before it is read
from the prose. A `CAP` or `UJ` with a `prd:` field goes to `requirements-<that slug>.yaml`; an `FR`
follows its `capability:` to that CAP's file; an `NFR` follows its `component:` to the PRD whose CAPs
own that component — a `BG` is product-level and never decides an NFR's home on its own, so `goal:` is
only a tie-breaker when that component's CAPs span two PRDs. On a product with exactly **one** PRD every row belongs to that
PRD by construction — write them all to its file and skip the citation scan. Otherwise, only a row with
none of those fields falls back to the PRD whose prose cites its id — and an id cited by **two** PRDs
is reported, not placed. The citation scan still runs on every row as a cross-check: a row whose
structural home and citing PRD disagree is reported with both names. Write the row, unchanged, into
its file; `goals:` rows go to `goals.yaml`. A sentence moved into a YAML value keeps its punctuation
and its markup: when it holds `: ` or `#` or starts with a quote, wrap the value in double quotes or a
`>-` block — never trade a colon for a dash or strip `**` and backticks to make it a plain scalar. A row with no home is reported by id, not guessed: the
owner names it. When every row has moved, delete `requirements.yaml`; `id-allocated-once` fails if a
row was copied instead of moved.

Run `validate.py --check`. Green here means the registry is whole before any document starts pointing
at it.

## Step 3 — Documents, oldest gate first

**3 — brief.** Merge `## Executive Summary` and `## Vision` into one `## Why`, keeping every sentence
that says something the other did not. Each `BG-N` statement under `## Goals` MUST already be a row in
`goals.yaml` (Step 2); replace the list with the pointer line from the template. Each `## Assumptions`
item becomes a row in `.control/questions/assumptions.md` with `Whose: owner`; each `## Prerequisites`
item a row in `external.md` — **after** checking that no `OQ-` row already states it, because a brief
written under an earlier kit usually landed them already and a second row is a copy. A prerequisite
the brief itself marks satisfied is dropped, not landed as open. A `questions/` table written before
the `Whose` column existed (`| id | Assumption | Cost if wrong | Taken | By |`) gets the column added —
header and separator, and an empty cell on every existing row, which the validator counts as
`unstated`, which is what they are. The rows this skill lands say `owner`. `Cost if wrong` is `—` when
the source never stated one; it is not invented. An open question the source never marked blocking is
filed in `assumptions.md`, as the template's three tests say. Delete both sections, and say how many
items were already rows. Check `## Success Criteria` names one measurable
figure — if it does not, that is a finding for the owner, not a sentence for this skill to invent.

**4 — each PRD.** Sections are matched **by name, never by number**: the numbers moved between kits
(one kit numbers Non-Goals §5 and Open Questions §8; an older one numbers Non-Goals §7, MVP Scope §8,
Open Questions §10), so a step that says "delete §8" deletes MVP Scope on the wrong corpus. Delete
`Document Purpose`. Every `Glossary` term not yet in `.control/product-glossary.md` is added there,
verbatim; then delete `Glossary`. Every `Non-Goals` item MUST already be in the brief's Scope Out or
this PRD's `MVP Scope → Out of Scope` — if neither holds it, add it to the one it belongs to; then
delete `Non-Goals`. Every `Open Questions` and `Assumptions Index` item becomes a `questions/` row
(after the same already-a-row check as the brief's); delete both.
Under each feature, every `FR` block is folded into its row in `requirements-<slug>.yaml` (Step 2)
before the block goes: the block's description paragraph — the prose between the `#### FR-N` heading
and the first `**…:**` label — becomes the row's `statement:` when the row has none (the row's `title`
stays). **This is the one move with no validator behind it**, so count it: blocks with a paragraph
versus rows that now carry `statement:` MUST match, and Step 5 reports both numbers. A run that deletes
the blocks and lands zero statements has thrown the requirement's own sentence away; its `**Consequences (testable):**` bullets move verbatim to
`addendum.md` under `## Technical how — testable consequences per FR`, appended **after** the sections
already there, one `### FR-N — title` each,
because `prd-guide.md` repealed the double proof of done and that is where the technical restatement
lives now; its `**Proof of done:**` is compared with the row's `proof` — when they differ, the
**registry is kept** (it is the declared SSOT), the PRD's is dropped, and both texts are reported side
by side for the owner, never merged. Then the block becomes `**Realizes:** FR-a, FR-b, NFR-c`, and a
`**Functional Requirements:**` label left with nothing under it is deleted — the rendered page rebuilds
the blocks from the rows. When the deletions are done, **renumber the surviving `##` headings to the
template's order** — 1 Why This Initiative · 2 Target User · 3 Features · 4 MVP Scope · 5 Success
Metrics · 6 Cross-Cutting NFRs · 7 Constraints and Guardrails — and the `###` beneath them to match
(`### 8.2` → `### 4.2`). Numbers are not sentences; leaving `## 4. Features` beside `## 8. MVP Scope`
tells the next reader two sections went missing. A `UJ-N` the prose names that has no row in any requirement file is
not given one — it is marked with an HTML comment where it stands and reported; `wdi-product`
allocates ids. A moved sentence that cites a section number (`§ 8`) of a section this step deletes
keeps the number — it is reported as wording for the owner, not repointed, because its new home is a
judgment. `## 1. Vision` becomes `## 1. Why This Initiative`: delete only the sentences
that also appear, word for word, in the brief's `Why`; what remains is left whole under an HTML comment
saying the new shape wants a delta, because deciding which paraphrases are copies is the owner's. On a
single-initiative product that is one line pointing at the brief — write it and say so.

**5 — each SRS.** Every `| UC-` row MUST already be in `usecases.yaml` with the same `critical`. A row
missing there is landed first. Then the table becomes the template's pointer line.

**6 — each SDD.** In `## Inherited Constraints`, drop the `Quoted rule` column; keep `AD` and `How it
lands here`. In the blockquote shape, drop the `> ` lines and the `Quoted verbatim from` sentence; keep
the `**AD-N — title**` heading and the landing prose under it, each heading on its own line. An `AD-N`
cited here that is not in the spine is a finding.

**7 — C4 L2.** Every PC listed in the table MUST have that container in its `containers:`. Then the
table becomes the pointer line.

**8 — pointers at the moved pages.** Every `.md` that cites `.control/generated/brief.md`,
`blueprint.md`, or `prd-<slug>.md` **and that `cites-resolve` reads** is repointed to the new path — a
path substitution, nothing else in the sentence changes. That includes a product's own scratch and
issue notes. It excludes what the validator excludes: `.control/memlog/`, `.control/decisions/`,
`.control/reports/`, `questions/answered.md`, and `_bmad-output/` — those describe the past, and a
path rewritten there falsifies a record; the installer's probe skips them for the same reason.

## Step 4 — Render, then validate

```bash
uv run .constitution/method/scripts/validate.py --generate
```

This writes every reader's page into `.what-rendered/` and `.how-rendered/`, and clears the human pages
that used to sit in `.control/generated/`. Then `--check` MUST be green. Every finding at this point is
either a row that moved wrong in Step 2 or a pointer that points at nothing — both are this skill's to
fix before it reports done.

## Step 5 — Report, and commit once

What moved, file by file · what was landed into the registry, by id · what could not be placed and
needs the owner · the rendered pages now waiting to be read, one per gate · validators green. Then
**one** commit: `chore(method): upgrade <from> → <to>`. Not one per document — the upgrade is one
event.

## Rules

- You MUST NOT change a sentence while moving it. Wording that reads wrong in its new home is a
  finding for the owning skill, later.
- You MUST NOT invent a home. An `FR` no PRD cites, a Non-Goal neither boundary holds, an `AD-N` not
  in the spine — each is reported by id and left where it was.
- You MUST NOT write your findings into the corpus. A registry file carries rows and nothing about
  the upgrade that produced them; a gap in this skill goes in the Step 5 report. The one exception is
  the HTML comment the steps above name, placed where the owner will read the document.
- You MUST NOT re-cut `specs.yaml`. That is `wdi-build`'s, where a human can see it.
- You MUST NOT touch `.control/decisions/` or `.control/reports/`. A frozen `DEC-` that cites `V26` or
  `W3` is history; the alias rule in `corpus-guide.md` covers it.
- Re-running on an upgraded repo MUST find nothing and say so. Every probe in Step 1 is idempotent.

## Output

The Step 1 checklist with each item marked done · skipped (already new shape) · left for the owner, with
the id list for the last · the registry rows landed · **statements landed / FR blocks that had a
paragraph** · consequences moved · `questions/` rows added and rows found already present · proof-of-done
divergences, both texts · the path of every rendered page · the validator result · the commit.

---
status: Reference
---

# Rationale — why the method is shaped like this

**Opened when:** you are about to change a rule and need to know what you would break.

`wave` and `story` appear below wherever this file records **what happened** — a past incident, a repealed
ceremony, a skill's old name. Those are evidence and MUST NOT be rewritten into `spec` and `ticket`;
`../method-glossary.md` owns that rule. Where this file states a rule still in force, it uses the current
terms.

This file **explains**. It does not bind — `../document/*-guide.md` does, and where the two disagree the guide
wins and the disagreement is a defect to report. **A rule MUST NOT be born here.** If this file notices a
rule that should exist, it says so as a finding and the rule is written in its guide.

## What happened, and what fixed it

The previous version of this method was run in full on one real product as far as its third stage, then stopped by its
owner: `.what` had jammed, `.how` was being skipped, and coding was running straight from a `.what` that was
not finished. Six complaints, their causes, and where each is answered now:

| Complaint | Cause | Answered in |
|---|---|---|
| Open questions in floods — ids reached `OQ-146`; one review produced 200 findings, then another produced 90 | Three rules combined into a generator: the `edge-case-hunter` lens mandatory over a whole SRS at once; no route for *"take the assumption, record it, continue"*; no budget and no severity class | `../document/decision-guide.md`, `.control/questions/` |
| Ceremony drift into the PRD; three corrections ended "reported but not fixed" | Correcting a *sentence* of an `FR` was treated as changing its *promise* — both had to go through the PRD skill | `../document/prd-guide.md` |
| Gates failing repeatedly over unanswered questions | No rule said that only a **blocking** question holds a gate | `.control/questions/blocking.md` |
| The spine had to be updated every story | Invariants and inventories were mixed, and the tax was paid before the story, when the information was thinnest | `../document/architecture-guide.md` |
| A large PRD made `.what` over-think — 41 of 56 use cases marked `critical` (73%) | Not the PRD's length. The stage's scope was the whole corpus at once, plus a `critical` definition with two elastic criteria that passed everything | `../document/delivery-flow-guide.md` |
| Too slow for a small-to-medium application | A composite of the five above | all of it |

One cause was **not** the method: **model choice.** A "find the gap" lens with no upper bound, run by the
most careful model, produces the most gaps, and each gap became an open question. That is a policy question,
and its answer is in `README.md`.

## Six principles

Every decision in this method traces to one of these. Anything that traced to none of them was left out.

1. **The size of the application does not set the depth of the documents.** Size sets how many components
   there are, not how deep each one goes.
2. **Depth is set by the owner's preference, not by an objective threshold.** A preference is a legitimate
   input and does not have to be justified.
3. **Accepting risk must be cheap.** One recorded line, not a debate. If accepting risk is expensive, people
   avoid it by writing documents they do not need.
4. **Breadth once, depth per component.** The global portrait is born once and thin; depth is born when its
   component is actually worked on.
5. **What can be derived is not written by hand.** Inventories, structure maps, the decision index, the
   global catalogue, ticket status. This principle stood here alone for a long time, binding nothing —
   this file explains and MUST NOT hold a rule — while reviews kept re-finding the same drift. It is now
   a rule: `../document/corpus-guide.md` § A derived fact has exactly one home.
6. **Mandatory is a cost and must buy something.** A mandatory rule that prevents no concrete failure is
   repealed, not loosened.

## Why `mode` and `risk_accepted` are two fields

The most important separation in the method, and the easiest to undo by accident.

Documents and reviews are **two different mitigations.** Merging them makes one legitimate position
impossible to state:

> *"This part is risky, I know that, and I manage it with tests and review — not with prose."*

If depth were controlled by `risk_accepted`, the only route to a thin document would be raising
`risk_accepted` — which means **lying in the risk record** to buy the depth you wanted. And the entire reason
that field exists is to record what was accepted.

So a component may sit at `mode: catalog` and `risk_accepted: low` at the same time: thin on purpose, and
reviewed the hardest precisely there. No matrix can hold that position, and it is a position people actually
have.

The control over it is **disclosure, not veto**. The agent does not judge; it reads the `FR` that fall to
the component and names what is touched — money moving, personal data, an irreversible action, a contractual
promise, an un-rollbackable integration — and only then proposes values. The owner may always choose fast.
They may never choose it without knowing what is being staked.

One hard floor is not negotiable against preference: when an outside party — a regulator, an auditor, a
client through a contract — will demand the artifacts as a deliverable, the touched component goes to
`mode: deep` and `risk_accepted: low`. There the risk is not the owner's alone to accept.

## Why `mode` has no third scope

`mode` cannot be overridden per spec or per `SPEC.md`. A spec MAY cross several components, so a per-spec
override would give one component two different depths depending on which spec touched it — while the
document is one, and living.

> Depth belongs to the component, not to the work.

## Why the blueprint is bounded to lists

The most decisive boundary in the method. The previous run broke because "complete" was read as "fully
specified".

The blueprint carries **one line per thing**: one line per use case, per table, per endpoint, per screen.
Plus the entities, the actors, the spine, C4, and the rules that cross components. What it does **not**
carry is the flows, the failure behaviour, the contracts, the data dictionary — those are per component, at
G4, and only as deep as that component's `mode`.

Two consequences worth knowing:

- **The order stops being circular.** Blueprint content is untouched by `mode`, and `mode` is first needed at
  G4 — by which point it has existed since the tail of G2.
- **Nobody needs a fifth mode.** The wish for one is almost always *"I need at minimum the use cases, the
  API, and the database"*, and all three are in `catalog` already, because none of them is part of the knob.

**G3 is written per component and gated once**, and that is not a compromise. Writing parallelises with the
component as the key. The gate is one, because its whole value is seeing the picture entire before choosing
which component to build — gating per component means approving seven times, each time seeing a seventh.

What is reviewed at G3 is the **generated roll-up**, not seven files. The catalogue and the actor lists stay
in their component kernels as their permanent home. One fact, one home, one view.

## Why `critical` was narrowed to three words

It used to mean: touches money, personal data, or an irreversible action; **or** is the reason the component
exists; **or** is expensive to discover late. With the last two, every use case passed — 41 of 56, 73%.

Both were repealed. What is left is the first clause, and the one-third sanity check that follows from it: if
more than a third of a component's use cases are marked, the definition was misapplied.

## Why decisions stopped being mandatory, and stopped being called ADRs

The old name was ADR — *Architecture Decision Record* — and the word "Architecture" forced the wrong
question at the moment of writing: *"is this architectural?"*. That question discards exactly the decisions
most worth keeping, the ones that sound small: *"the filter works like this"*.

So the name is `DEC-`, and the test is memory rather than category:

> If someone asks in three months why it is like this, is the answer readable from the code?

Recording is **not mandatory**, with one exception: a decision that contradicts or changes an `AD-N`. And
one sentence has to be said out loud or "not mandatory" gets read as "mandatory but allowed to be late":

> A decision nobody recorded is normal, not negligence, and MUST NOT be logged as debt.

Three more things changed, each closing a hole that already existed:

- **`applied` became a status.** The old form already said that *applying* is what freezes a decision — but
  there was no status for it, so "applied or not" was readable from nowhere.
- **`layer:` was repealed.** It was a classification demanded before anything was known, and it was guessed
  as often as derived. `touches:`, filled from what actually changed, replaces it.
- **Finding a decision stopped going through the memlog.** A generated flat table does it. The memlog is a
  run log again.

## Why the folders stay `.what/` and `.how/`

Naming folders after the gates — `.problem/`, `.product/`, `.blueprint/`, `.component/`, `.release/` — was
weighed and **not taken**, for four reasons:

| Reason | Concretely |
|---|---|
| Two folders for two files | `.problem/` would hold one brief; `.product/` would hold PRDs. That is ceremony, not clarity |
| One folder with nothing in it | G5's output is code, tests, a PR, a green RTM — no document |
| **Time would become a folder axis** | A gate is a moment. One SRS would split across two homes — half written at G3, half at G4. One living document, two folders, divided by the calendar |
| **A mechanical guard would be lost** | Today a skill cannot write into a layer that is not its own, because the boundary is enforced **by path**. Put behaviour and mechanism in one folder and that boundary drops to prose |

So "Blueprint" and "Component" name a **gate and a skill** — not a document, not a folder. The split between
them is horizontal, not vertical: the blueprint holds the breadth of both layers, the component holds the
depth of both.

What actually answered the original complaint — that `.what`/`.how` feel abstract — is not a rename. It is
**one table in `AGENTS.md`**: the thing in your hand → its folder. Nobody has to reason about the abstraction
if the answer is already written where they are standing.

## Why each skill exists, and why the merged ones merged

Twenty-one skills became fifteen. Skills are named for the **gate they serve** rather than the artifact they
write, so *"which skill do I run"* is answered by *"which gate am I at"*.

| Gone | Merged into | Why |
|---|---|---|
| `wdi-product-brief` | `wdi-problem` | Renamed to its gate |
| `wdi-analysis` | `wdi-blueprint` + `wdi-component` | It branched three ways in its own first step — the sign of two jobs in one skill. The split now falls exactly on the gate boundary |
| `wdi-architecture` | `wdi-blueprint` intent `platform` | Spine, C4, and the inventories are all G3 output |
| `wdi-design` | `wdi-component` intent `design` | Renamed to its gate |
| `wdi-glossary` | `wdi-blueprint` | It was already the first step of the writing order |
| `wdi-component` (old) | `wdi-init` intent `component` | Its work was a registry row and two skeletons. That is init |
| `wdi-structure` | `wdi-init` intent `structure` | Its scope widened to everything that must exist before work starts |
| `wdi-apply` | `wdi-decision` | Applying is part of a decision's life, and it is what writes `applied` |
| `wdi-correct-course` | `wdi-decision` | A course correction **is** a decision |
| `wdi-wave` · `wdi-ship-story` | `wdi-build` | One unit of work must not need four invocations, three of them bookkeeping |
| `wdi-project-log` | `wdi-log`, with `wdi-meeting` | Both record a fact that came from outside the code |
| — | **`wdi-product` was born** | `bmad-prd` was the only writer of a primary artifact with no wrapper, so nothing checked its position, verified its result, or landed its memlog |

**`wdi-ux` stands alone and was deliberately not merged.** It is the one skill that straddles: its decision
sits at G2 altitude — *how does this feel to use* — while its landing is per component. Merged into
`wdi-product` its landing home would be wrong; merged into `wdi-component` its decision altitude would be.
Left standing, it is more honest than either, and honesty beats the count.

## Why fan-out has a rule

> Parallel fan-out is only for output with a natural key. Output that is a shared list with no key must be
> written by one agent that reads the whole input.

Not theory. In the previous run, 41 cross-component business rules from seven parallel agents had to be
merged and de-duplicated **serially**, because the target file had no key — and that merge was the most
expensive part of the pass.

Keys that exist: the Product Component, the inventory source, the endpoint number, the ticket, the spec.
Things with no key: the glossary, the cross-component rules, the spine.

## Why nine ceremonies were repealed

Each cost something and bought nothing, and principle 6 says that is grounds for repeal rather than
loosening:

| Repealed | Because |
|---|---|
| The `ANX-` annex, its "referenced in ≥2 places" rule, and its `Verified` + SHA line | Zero annexes were ever born |
| The `No-op` lane rule on flow diagrams | A heavy convention for a folder that had never carried a file |
| `layer:` on a decision, and the whole `both`-versus-pair section | Replaced by `touches:`, filled from what happened |
| The double proof of done — a business sentence plus a technical restatement | The business one stays; the technical form is the test name, checked mechanically |
| The `SCP-` code | A course correction is a `DEC-`. No second code names the same thing |
| The 400-line threshold for splitting a slot | Dropped from mandatory to advice |
| Having to open a written decision at five different points | One is left: contradicting an `AD-N` |
| 21 of the 35 gate-checklist questions, at `mode: catalog` | They remain in the guide as material. Asking them is never wrong; requiring them was |
| Five of the eight story-closing items | They moved to **wave close**, where the information actually exists |

Two of those were leaks of a different kind, and naming the kind matters more than the two instances: the
`No-op` lane rule and the annex `Verified` line were both **how to do the work** written as **what binds**.
The test that separates them:

> If next year's model is twice as capable, does this rule still buy something? Yes → it belongs in a guide.
> No → it belongs in a template comment.

A guide carries the layer boundary, the required shape, the failure prevented, the acceptance test, and the
ownership. A template comment carries the phrasing, the examples, and the heuristics — and template comments
are already designed to be deleted, which makes them the right home for what ages.

## Why a container is a runtime, not a folder

Three places in this repo used the word "container" for three different things with zero overlap, and the
argument that followed was not about which list was right. It was about a definition nobody had written, so
each place had quietly invented one. `DEC-017` settled it: a container runs its own code or stores its own
data, and can be replaced without rebuilding another. **Deploying two of them in one release does not merge
them** — that is a deployment choice, and reading it as an architectural one is what collapses a browser
bundle into "static assets of the web server", where it carries real behaviour with no owner and no NFR.

The part worth carrying is not the definition but **why one rule could not be obeyed**. The old rule said
every container heading in the codebase map must match the registry, and the next sentence said a container
with no code of ours gets no section. A database satisfies the second and cannot satisfy the first. Read as
symmetric, the rule demanded a section that would be empty or invented — and the way out was not an
exception but a field: `built` says whether the implementation is ours, and the match became one-directional.

**A definition left unwritten will be re-argued in the next corpus.** That is the general lesson, and it is
why `built` is checked by `container-built` rather than merely described here: prose that nothing verifies is prose that
gets contradicted by the first person in a hurry.

## What is not here

The change plan that produced this shape — which guides changed, which templates were born, which folders
were deleted, in what order — was archaeology the moment the change landed. Its trace is in git.

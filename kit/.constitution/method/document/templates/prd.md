# PRD Template

**The PRD states the current promise. It is not a history of itself** — with one deliberate exception:
Revision History, which is written for a reader who was not in the room and MUST NOT be collapsed into
the corpus's present-tense rule. Everywhere else, see `corpus-guide.md` § The corpus is written in the
present tense.

**A derived fact has exactly one home, and it is never this document.** `FR`/`NFR`/`CAP` statements
live in `.control/registry/requirements-<slug>.yaml`; this PRD cites their ids under each feature, never their
text. The Glossary, Open Questions, and Assumptions Index are not sections here — see the WDI overrides
below for where each actually lives. See `corpus-guide.md` § A derived fact has exactly one home.

## Essential Spine *(almost always present)*

```markdown
---
title: {Initiative Name}
initiative: {slug}
created: {YYYY-MM-DD}
---

# PRD: {Initiative Name}
*Working title — confirm.*

> **This is the working PRD.** It cites requirement ids instead of repeating their text, so §3 lists
> `FR`/`NFR` by id, and there is no Glossary, Non-Goals, Open Questions, or Assumptions Index section
> here — each of those facts has its own home.
>
> **To read or hand over one complete, self-contained document, run `/wdi-report render prd`.**
> It writes `.what-rendered/_prd/<slug>/prd.md` with the capabilities, the requirement statements and
> proofs of done, the glossary terms this PRD uses, the non-goals, and the open questions filled in
> from their own homes. That file is regenerated, never hand-edited.

## Revision History

| Date | What changed | Why | Releases affected |
|---|---|---|---|
| {YYYY-MM-DD} | Initial version | — | {target release} |

[One row per Update run, newest last. Written for an outside reader — a client or sponsor who was
not in the room — so state what the promise now is, not which section was edited. This table is not
the memlog: the memlog records every decision inside a run and is an audit trail; this records what
changed for the reader. Neither replaces the other.]

## 1. Why This Initiative

[ONE paragraph, stated as a DELTA against the product's `Why` in `.what/_product-brief/brief.md`:
what does THIS initiative change, add, or unlock that the brief's narrative does not already say? For
a product with a single initiative, this MAY be a single sentence pointing back to the brief — "This
initiative IS the product's Why; see brief.md." It MUST NOT restate the product's vision from scratch.]

## 2. Target User

### 2.1 Jobs To Be Done
[Bulleted. Emotional, social, functional, contextual — whichever apply. Even "this is for me as the builder" is a valid framing for a hobby project.]

### 2.2 Non-Users (v1) *(add when the audience boundary is non-obvious)*
[Who this is explicitly not for in v1.]

### 2.3 Key User Journeys
*Named-persona narratives the product enables. Numbered globally as UJ-1 through UJ-N. FRs reference journeys by ID inline ("realizes UJ-3"); SMs may also cross-reference. If a UX doc already exists, mirror its UJ IDs here and point to the source.*

**Default shape:** a named scene with entry state, path, climax, and resolution. Each beat forces specificity the team would otherwise leave implicit — auth assumptions, screen order, what tells the user value landed. Read together as a short narrative; the example below shows the form.

- **UJ-1. {One-line title — persona doing the thing.}**
  - **Persona + context:** one line, grounded enough to explain the *why*.
  - **Entry state:** authenticated? which surface? coming from where?
  - **Path:** 3-5 concrete beats — taps, screens, decisions.
  - **Climax:** the moment value is delivered and how the user knows.
  - **Resolution:** state they're left in, what's next.
  - **Edge case** *(optional)*: one real failure mode and what the user does next.

  *Written out, that becomes:*
  > **UJ-3. Priya checks the trip damage before she's even home.**
  > Priya, budgeting on a single income with a new baby, finishes a grocery run and gets in the car. Already authenticated via biometric on a previous session. She opens the app, taps the FAB camera, and scans the receipt. The app OCRs the total and shows a single-screen overlay: this trip $84.20, weekly cap $250, $172.10 remaining, three days left in the week. She closes the app and drives home. **Edge case:** if she scanned a receipt earlier today, the app asks whether this replaces or adds to that trip before counting it against the cap.

- **UJ-2. ...**

**Scope dial:**
- **Lighter** — hobby/solo, library/CLI, or when the UJ is essentially a JTBD restated: a single sentence works (`{Persona}, {context}, {what they do and why}.`).
- **Heavier** — auth, multi-device handoff, complex navigation, or anything feeding downstream UX/architecture: add a numbered Flow, an Edge cases list, and a capability → FR mapping (`The system must {capability}. → FR-N`).

## 3. Features
*Each subsection is a coherent feature: behavioral description first, requirement ids nested under it,
optional feature-specific NFRs and notes. Reference user journeys by ID inline ("realizes UJ-2") where
the chain matters.*

### 3.1 {Feature Name}
**Capability:** CAP-N — serves BG-N. *(One feature is one capability; both IDs come from
`requirements-<slug>.yaml`. This is the link that makes the feature schedulable — size, priority, owner,
target release, and dependencies on other capabilities all live on the `CAP` entry, not here.)*

**Description:** [Behavioral narrative — how this feature works, who uses it, the user experience, edge cases. Realizes UJ-X, UJ-Y. Use Glossary terms exactly. Embed inline `[ASSUMPTION: ...]` tags where you inferred without confirmation.]

**Realizes:** FR-1, FR-2, NFR-3

[The statement, proof of done, and enforcer for each id above live in `requirements-<slug>.yaml`, landed there
by `wdi-product` as part of producing this PRD — landing the registry row is part of writing the
feature, not a follow-up. Do NOT write a full FR block here; the registry entry is the only copy. If a
requirement needs a longer technical restatement, that belongs in `addendum.md` or the SDD, never a
second proof of done.]

**Feature-specific NFRs:** *(only if any apply uniquely to this feature — cite the id; see §6)*

**Notes:** *(optional — open questions specific to this feature, `[NOTE FOR PM]` callouts)*

### 3.2 {Feature Name}
...

## 4. MVP Scope

### 4.1 In Scope
[Bulleted, crisp.]

### 4.2 Out of Scope for MVP
[Bulleted. Each item with a one-line reason if the reason matters. Mark items deferred to v2/v3 explicitly. Add `[NOTE FOR PM]` callouts where a deferred item is emotionally load-bearing — flags it for revisit if timeline permits.]

## 5. Success Metrics

*Each SM cross-references the FR(s) it validates, and the primary metric MUST relate back to the
brief's Success Criteria — either the same figure narrowed to this initiative, or a stated reason it
diverges. Counter-metrics counterbalance specific primary or secondary metrics.*

**Primary**
- **SM-1**: Metric — definition, target. Validates FR-X, FR-Y. Relates to the brief's Success Criteria: {how}.

**Secondary**
- **SM-2**: Metric — definition, target. Validates FR-Z.

**Counter-metrics (do not optimize)**
- **SM-C1**: Metric — why this should *not* be optimized. Counterbalances SM-1.

[Length scales with stakes. Hobby/utility PRD: a single sentence may be enough ("Success: I use this weekly and don't abandon it after a month"). Public launch / enterprise: full quantitative breakdown with measurement methods. Counter-metrics are as load-bearing as primary metrics — they prevent the architect from optimizing the wrong thing and the dev from gaming the wrong target.]

## 6. Cross-Cutting NFRs

[System-wide non-functional requirements not tied to a single feature — cite the `NFR-N` id; the
statement and `enforced_by` live in `requirements-<slug>.yaml`, same as any other NFR.]

## 7. Constraints and Guardrails

[MUST state only the delta beyond `.what/_product-brief/brief.md` — what binds THIS initiative beyond
the product's own constraints. MUST say "none beyond the brief" when there is nothing; an absent
section reads as "not checked."]
```

---

## Adapt-In Menu *(add the clusters the product calls for)*

### Consumer / branded products
- **Aesthetic and Tone** — visual references, anti-references, voice/tone for any product-generated text.
- **Information Architecture** — top-level surfaces, navigation, screens.
- **Monetization** — free vs. paid, pricing assumptions, ads policy.
- **Platform** — web, mobile, PWA, native, v1 vs. v2+.

### Enterprise initiatives
- **Stakeholders and Approvals** — who must sign off, at what stage.
- **Risk and Mitigations** — operational, security, business, reputational risk register.
- **ROI / Business Case** — quantified benefit, cost, payback period.
- **Operational Requirements** — SLAs, RTO/RPO, support tier, on-call expectations.
- **Integration and Dependencies** — SSO, existing enterprise systems, data sources, downstream consumers.
- **Rollout and Change Management** — phased rollout plan, training, internal communication.
- **Data Governance** — residency, sovereignty, classification, retention.
- **Audit Trail / Decision Provenance** — formal documentation requirements for regulated environments.

### Regulated domains
- **Compliance and Regulatory** — HIPAA, PCI-DSS, GDPR, SOX, SOC 2, Section 508 / WCAG 2.1 AA, FedRAMP, etc. — whichever apply. If any item needs depth, add a `[NOTE FOR PM]` callout to revisit or move to an addendum.

### Developer products (libraries, APIs, CLIs, SDKs)
- **API Contracts / Public Surface** — endpoint shapes, breaking change policy.
- **Versioning and Deprecation Policy**.
- **Performance Budgets** — latency, throughput, resource use.
- **Language / Runtime Targets and Dependency Policy**.

### Embedded / hardware
- **Hardware Constraints** — memory, power, form factor.
- **Deployment and Update Mechanism** — OTA, manual, image-based.
- **Environmental and Reliability Requirements**.

### Small-scope all-inclusive *(use when scope is 1-2 tickets' worth and the user wants a single captured artifact — chosen during the Right-skill check in Discovery)*
- **Tickets** — ticket-level detail listed inline at the end of the doc. Each ticket: *"As a [persona], I can [action] [under conditions]. Acceptance: [testable criteria]."* Numbered Ticket-1, Ticket-2, ... for reference. Pair with very lean §1 Why, §2 Target User (often just JTBD + one UJ), §3 Features (often a single feature), §4 MVP Scope (in/out very tight). The whole doc fits on a page or two and captures intent + implementable tickets in one place. If the user doesn't want the captured artifact at all, running `/to-tickets` straight from the conversation is the better path — this cluster is only for "I want a doc *and* the tickets."


---

## Project overrides — WDI

These rules replace the corresponding BMad defaults for this project.

- **Scope.** One PRD per **initiative / functional area** — not per product, not per component, and
  not per release. It is a **living document** and is never frozen.
- **Change.** A behaviour change, a correction, or a new feature closely tied to what is already
  here MUST land through `bmad-prd` intent *Update* on this same file. A second PRD MUST NOT be
  created because the release changed; create one only when the functional area is genuinely
  different and would not read well merged in.
- **Revision History.** Every Update run MUST add exactly one row, written for an outside reader.
  It is what preserves "what did we promise back then" now that the document is not frozen. This is
  the one place in this template where history is written on purpose — nowhere else in the PRD is.
- **§1 Why This Initiative is a delta, not a restatement.** BMad's default §1 Vision writes the
  product's vision from scratch; that duplicates the brief's `Why` on the first PRD a product ever
  gets. This section states only what changes, or points back to the brief when nothing does.
- **§3 carries requirement IDs, not requirement text.** `FR-N`/`NFR-N` statement and proof of done
  are authored straight into `requirements-<slug>.yaml` by `wdi-product` — landing the registry row is part
  of writing the feature. A full FR block (statement, consequences, proof of done) MUST NOT be
  written in this document; it is the registry's only copy.
- **No Document Purpose section.** BMad's §0 explains what a PRD is in general — true of every PRD
  in every project, so it carries no information specific to this one. Dropped.
- **No Glossary section.** Every domain noun MUST already exist in `.control/product-glossary.md`,
  used verbatim. A new noun this PRD needs MUST be raised through `wdi-question` in the same pass —
  it is NOT added to a PRD-local glossary, which `wdi-blueprint` does not read at G3.
- **No Non-Goals section.** What this PRD does not promise is either the product's own Scope Out
  (already in the brief) or this release's Out of Scope for MVP (§4.2) — a third list restating both
  is the same fact twice. The generated deliverable assembles both under one heading for a reader.
- **No Open Questions section.** An unresolved question goes through `wdi-question` into
  `.control/questions/` the moment it is found, not batched into a section read once at Finalize.
- **No Assumptions Index.** Every `[ASSUMPTION]` tag is a marker for the conversation that produced
  it, not an index entry — it MUST be registered through `wdi-question` into `assumptions.md` before
  this PRD passes G2, and the tag is then just prose color, not a second bookkeeping copy.
- **Release.** Carried by `CAP.target_release` in `.control/registry/requirements-<slug>.yaml` — the only
  place a promise's release is written — and by `release` in `specs.yaml` for the execution side. It
  MUST NOT be expressed through this document's folder name or title, and an `FR` MUST NOT carry a
  release of its own; it inherits one from its capability. Naming a release in prose as context MAY
  happen; the registry is what binds.
- **Numbering.** `FR-N`, `NFR-N`, `UJ-N`, and `CAP-N` MUST be allocated from
  `.control/registry/requirements-<slug>.yaml`, and `BG-N` from `goals.yaml`. They MUST NOT restart at 1 in a new PRD — the sequence is
  global to the product, and a later PRD continues the earlier one.
- **Two Adapt-In clusters are not optional here.** `Cross-Cutting NFRs` (§6) and `Constraints and
  Guardrails` (§7) MUST be present — they are in the Essential Spine above, not conditional. G2
  passes on numbered FR **and** NFR, so a PRD with no NFR cited cannot clear it; and a constraint
  discovered at G4 costs a decision that a sentence here would have prevented.
- **Constraints state the delta.** Product-wide constraints already live in
  `.what/_product-brief/brief.md`. §7 MUST carry only what binds *this initiative* beyond
  them, and MUST say "none beyond the brief" when there is nothing — an absent section reads as
  "not checked".
- **Prerequisites are not written here.** An initiative that cannot start until another one ships is
  a `depends_on` between `CAP` entries, which MAY point at a capability in another initiative's file. Restating it in prose creates a
  second home that will drift.
- **§2 MUST name which stakeholders from the brief this initiative serves**, using the same role
  names. A PRD that invents its own user labels breaks the trace back to `BG-N`.
- **Boundary.** This document promises; it MUST NOT design. Behaviour of the system belongs to
  `SRS-<pc>.md`, and solution shape to `SDD-<pc>.md`.
- **Memlog.** Written to `.control/memlog/prd-<slug>.md` via `--path`, never beside this file. The
  slug matches this PRD's folder.

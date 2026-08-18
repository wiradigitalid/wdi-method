# PRD Template

## Essential Spine *(almost always present)*

```markdown
---
title: {Initiative Name}
initiative: {slug}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
---

# PRD: {Initiative Name}
*Working title — confirm.*

## Revision History

| Date | What changed | Why | Releases affected |
|---|---|---|---|
| {YYYY-MM-DD} | Initial version | — | {target release} |

[One row per Update run, newest last. Written for an outside reader — a client or sponsor who was
not in the room — so state what the promise now is, not which section was edited. This table is not
the memlog: the memlog records every decision inside a run and is an audit trail; this records what
changed for the reader. Neither replaces the other.]

## 0. Document Purpose
[1 paragraph: who this PRD is for (PM, stakeholders, downstream workflow owners), how it's structured (Glossary-anchored vocabulary, features grouped with FRs nested, assumptions tagged inline and indexed). If UX work or other inputs already exist, name them here and reference where they live — this PRD builds on them, it does not duplicate.]

## 1. Vision
[2-3 paragraphs: what this is, what it does for the user, why it matters. Compelling enough to stand alone.]

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

## 3. Glossary
*Downstream workflows and readers must use these terms exactly. FRs, UJs, and SMs use Glossary terms verbatim; introducing a synonym anywhere in the PRD is a discipline violation. If §4 introduces a new domain noun, add it to the Glossary in the same pass.*

- **Term** — Definition. Relationships to other Glossary terms. Cardinality where relevant.
- **Term** — ...

[Every domain noun the rest of the document uses. Defined once. No synonyms anywhere else in the PRD.]

## 4. Features
*Each subsection is a coherent feature: behavioral description first, FRs nested under it, optional feature-specific NFRs and notes. FRs are numbered globally (FR-1 through FR-N) so downstream artifacts have stable references even if features get reorganized. Reference user journeys by ID inline ("realizes UJ-2") where the chain matters.*

### 4.1 {Feature Name}
**Capability:** CAP-N — serves BG-N. *(WDI. One feature is one capability; both IDs come from `requirements.yaml`. This is the link that makes the feature schedulable — size, priority, owner, target release, and dependencies on other capabilities all live on the `CAP` entry, not here.)*

**Description:** [Behavioral narrative — how this feature works, who uses it, the user experience, edge cases. Realizes UJ-X, UJ-Y. Use Glossary terms exactly. Embed inline `[ASSUMPTION: ...]` tags where you inferred without confirmation.]

**Functional Requirements:**

#### FR-1: {Short capability name}

[Actor] can [capability] [under conditions]. Realizes UJ-X.

**Proof of done:** *(WDI, required)* [One sentence a Product Owner can check without opening the code. Business language, no HTTP codes and no table names. This is the sentence that lets one FR become one testable unit of work — it is not the same as the technical consequences below, and one MUST NOT be written in place of the other.]

**Consequences (testable):**
- {Specific testable condition, e.g. "System returns HTTP 429 when request rate exceeds 100/sec per merchant."}
- {Another testable condition.}

**Out of Scope:** *(optional — what this FR explicitly does NOT cover)*
- {bound}

#### FR-2: ...

**Feature-specific NFRs:** *(only if any apply uniquely to this feature)*
- Performance / security / accessibility / etc. specific to this feature.

**Notes:** *(optional — open questions specific to this feature, `[NOTE FOR PM]` callouts)*

### 4.2 {Feature Name}
...

## 5. Non-Goals (Explicit)
[Bulleted. What this product is *not* and what it will *not* do in v1. Does outsized work for downstream readers and workflows — prevents the "let me also add this nearby thing" failure mode at every level (epic, ticket, code). Inline `[NON-GOAL for MVP]` callouts within §4 Features cover deferred items within features; this section captures the broader "we are not building X / we are not becoming Y" statements.]

## 6. MVP Scope

### 6.1 In Scope
[Bulleted, crisp.]

### 6.2 Out of Scope for MVP
[Bulleted. Each item with a one-line reason if the reason matters. Mark items deferred to v2/v3 explicitly. Add `[NOTE FOR PM]` callouts where a deferred item is emotionally load-bearing — flags it for revisit if timeline permits.]

## 7. Success Metrics

*Each SM cross-references the FR(s) it validates. Counter-metrics counterbalance specific primary or secondary metrics.*

**Primary**
- **SM-1**: Metric — definition, target. Validates FR-X, FR-Y.

**Secondary**
- **SM-2**: Metric — definition, target. Validates FR-Z.

**Counter-metrics (do not optimize)**
- **SM-C1**: Metric — why this should *not* be optimized. Counterbalances SM-1.

[Length scales with stakes. Hobby/utility PRD: a single sentence may be enough ("Success: I use this weekly and don't abandon it after a month"). Public launch / enterprise: full quantitative breakdown with measurement methods. Counter-metrics are as load-bearing as primary metrics — they prevent the architect from optimizing the wrong thing and the dev from gaming the wrong target.]

## 8. Open Questions
[Numbered. Things still unknown — they become future tickets or follow-up research, not silent gaps.]

## 9. Assumptions Index
*Every `[ASSUMPTION]` from the document, surfaced for explicit confirmation:*
- Inline assumption from §X.Y — short description.
- ...
```

---

## Adapt-In Menu *(add the clusters the product calls for)*

### Cross-cutting quality and shape *(most non-trivial PRDs)*
- **Cross-Cutting NFRs** — system-wide non-functional requirements not tied to a single feature (performance, security, reliability, observability). Add when system-wide quality attributes are meaningful.
- **Constraints and Guardrails** — Safety, Privacy, Cost. Subsection per cluster. Add when any of these are real concerns.
- **Why Now** — add when timing is load-bearing (a market shift, a technology enabler, a regulatory deadline). Drop when timing is incidental.

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

### Small-scope all-inclusive *(use when scope is 1-2 stories' worth and the user wants a single captured artifact — chosen during the Right-skill check in Discovery)*
- **Stories** — story-level specs listed inline at the end of the doc. Each story: *"As a [persona], I can [action] [under conditions]. Acceptance: [testable criteria]."* Numbered Story-1, Story-2, ... for reference. Pair with very lean §1 Vision, §2 Target User (often just JTBD + one UJ), §3 Glossary (handful of terms), §4 Features (often a single feature), §6 MVP Scope (in/out very tight). The whole doc fits on a page or two and captures intent + implementable stories in one place. If the user doesn't want the captured artifact at all, `bmad-build` is the better path — this cluster is only for "I want a doc *and* the stories."


---

## Project overrides — WDI

These rules replace the corresponding BMad defaults for this project. They are additive to the
shape above; nothing in the shape is removed.

- **Scope.** One PRD per **initiative / functional area** — not per product, not per component, and
  not per release. It is a **living document** and is never frozen.
- **Change.** A behaviour change, a correction, or a new feature closely tied to what is already
  here MUST land through `bmad-prd` intent *Update* on this same file. A second PRD MUST NOT be
  created because the release changed; create one only when the functional area is genuinely
  different and would not read well merged in.
- **Revision History.** Every Update run MUST add exactly one row, written for an outside reader.
  It is what preserves "what did we promise back then" now that the document is not frozen.
- **Release.** Carried by `CAP.target_release` in `.control/registry/requirements.yaml` — the only
  place a promise's release is written — and by `release` in `waves.yaml` for the execution side. It
  MUST NOT be expressed through this document's folder name or title, and an `FR` MUST NOT carry a
  release of its own; it inherits one from its capability. Naming a release in prose as context MAY
  happen; the registry is what binds.
- **Numbering.** `FR-N`, `NFR-N`, `UJ-N`, and `CAP-N` MUST be allocated from
  `.control/registry/requirements.yaml`. They MUST NOT restart at 1 in a new PRD — the sequence is
  global to the product, and a later PRD continues the earlier one.
- **Two Adapt-In clusters are not optional here.** `Cross-Cutting NFRs` and `Constraints and
  Guardrails` MUST be present. G2 passes on numbered FR **and NFR**, so a PRD with no NFR section
  cannot clear it; and a constraint discovered at G4 costs a decision that a sentence here would
  have prevented. Every other Adapt-In cluster stays conditional as BMad intends.
- **Constraints state the delta.** Product-wide constraints already live in
  `.what/_product-brief/brief.md`. This section MUST carry only what binds *this initiative* beyond
  them, and MUST say "none beyond the brief" when there is nothing — an absent section reads as
  "not checked".
- **Prerequisites are not written here.** An initiative that cannot start until another one ships is
  a `depends_on` between `CAP` entries in `requirements.yaml`. Restating it in prose creates a
  second home that will drift.
- **§2 MUST name which stakeholders from the brief this initiative serves**, using the same role
  names. A PRD that invents its own user labels breaks the trace back to `BG-N`.
- **Vocabulary.** Every domain noun MUST already exist in `.control/product-glossary.md`, used verbatim. A
  new noun introduced here MUST be added to the Glossary in the same pass, not defined inline.
- **Boundary.** This document promises; it MUST NOT design. Behaviour of the system belongs to
  `SRS-<pc>.md`, and solution shape to `SDD-<pc>.md`.
- **Assumptions.** Every `[ASSUMPTION]` left unresolved at Finalize MUST be registered through
  `wdi-question` before this PRD passes G2.
- **Memlog.** Written to `.control/memlog/prd-<slug>.md` via `--path`, never beside this file. The
  slug matches this PRD's folder.

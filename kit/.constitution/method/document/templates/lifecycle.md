---
type: lifecycle
component: '{pc}'
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
updated: '{YYYY-MM-DD}'
entities: []             # the domain entities whose lifecycles this file carries
---

# State Lifecycle — {Product Component}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Home: .what/<pc>/03-domain/state-machines.md. Written at G4, at mode: deep ONLY. Below deep it
     MUST NOT be written to fill a slot.

     One section per entity that has more than one state. An entity with a single state has no
     lifecycle and MUST NOT get a section.

     WHY THIS HAS ITS OWN TEMPLATE: a transition table does not resemble an ERD, so it cannot be
     lodged inside model.md. What it needs stated — who may move a thing, and what makes a state
     terminal — has no column in an entity diagram.

     THIS IS BEHAVIOUR, NOT SCHEMA. The state VALUES are English, because they are enum values and
     language-guide.md governs that. Their LABELS — what a user reads — are not written here; they
     belong to the screen. A value rendered straight to the screen is the known pitfall this repo
     already records.

     G3 asks whether there is a state that can be entered but not left. This file is where that is
     answered, and an unreachable or inescapable state is a FINDING, not a documented fact. -->

## {Entity}

**States:** `{value}` · `{value}` · `{value}`
**Initial:** `{value}` — and what creates it
**Terminal:** `{value}` · `{value}` — and why nothing leaves them

| From | To | Trigger | Who may | Guard | Side effect |
| --- | --- | --- | --- | --- | --- |

<!-- `Who may` names an actor from the SRS Actor Register, or `System` for an automatic transition.
     `Guard` is the business rule that has to hold — cite the BR- id rather than restating it.
     `Side effect` is what else changes; a transition with an invisible side effect is the one that
     surprises someone while the code is being written.

     Every state in the list above MUST appear at least once as a `To`, except the initial one, and
     at least once as a `From`, except a terminal one. That is the check, and it is mechanical. -->

### What is deliberately not modelled

<!-- A state someone will look for and not find, and why. A schema value nothing uses — say so:
     until the schema is cleaned, it has no label, no transition, and no meaning. -->

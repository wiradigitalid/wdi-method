---
type: model
component: '{pc}'
layer: physical              # conceptual (.what/<pc>/03-domain/) · physical (.how/<pc>/05-model/)
created: '{YYYY-MM-DD}'
---

# Model — {name}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     THE LAYER RULE, and it is the one most often broken:

       conceptual — .what/<pc>/03-domain/ — things, their relationships, their cardinality, and the
                    states they move through. Column types MUST NOT appear. This is what the
                    Product Owner can read.

       physical   — .how/<pc>/05-model/ — tables, columns, types, indexes, constraints, migrations.

     Set `layer` in the frontmatter and keep to it. A conceptual model with `VARCHAR(255)` in it has
     already become a physical one, and the Product Owner has quietly lost the ability to review
     the domain. -->

## Entities

<!-- One row per thing. For a conceptual model the description is what it IS to the business, not
     how it is stored.

     `Code name` closes the loop this table used to leave open. The conceptual model is written for
     the Product Owner, so its Entity column carries the word the BUSINESS uses — which is not always
     the identifier code must use. Naming both, in one row, is what stops an agent inventing a third
     word. `../language-guide.md` owns which language the code name is written in, and the one
     exception for an Indonesian administrative or legal noun.

     `Never called` is the synonym that was rejected, kept on purpose. A term resolved silently comes
     back: the losing word is still in somebody's head, in an old document, and in the client's
     email. Naming it here is what makes reintroducing it a finding instead of a habit. Leave the
     cell empty when no synonym ever competed — an invented one is noise.

     Every row's definition MUST live in `.control/product-glossary.md`, not here. This table points;
     the glossary defines. -->

| Entity | What it is | Identified by | Code name | Never called |
| --- | --- | --- | --- | --- |

## Relationships

<!-- Direction and cardinality. State them as sentences a person would say: "one member has zero
     or one sponsor". -->

## State Lifecycle

<!-- For entities that change status: which states exist, what triggers each transition, and who is
     allowed to trigger it. G3 asks whether any state can be entered but not left — that question is
     answered here or not at all. Cut this section for entities that never change status. -->

| From | To | Trigger | Who may |
| --- | --- | --- | --- |

## Invariants

<!-- What MUST always be true regardless of path taken. These usually become BR- entries and
     database constraints at the same time; state them once here and reference from both. -->

## Physical notes

<!-- ONLY when layer: physical. Indexes, partitioning, retention, migration ordering. Cut entirely
     for a conceptual model. -->

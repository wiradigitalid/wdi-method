---
type: model
component: '{pc}'
layer: physical              # conceptual (.what/<pc>/03-domain/) · physical (.how/<pc>/05-model/)
created: '{YYYY-MM-DD}'
updated: '{YYYY-MM-DD}'
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
     how it is stored. -->

| Entity | What it is | Identified by |
| --- | --- | --- |

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

---
type: lc
id: LC-{NNN}                 # allocated from .control/registry/components.yaml
name: '{name}'
lc_type: service             # ui-screen · ui-composite · ui-element · gateway · service · job · store
container: '{container}'     # the runnable/deployable unit it lives in
component: '{pc}'            # the Product Component it belongs to
owner: '{team or person}'
area: '{area}'
created: '{YYYY-MM-DD}'
---

# LC-{NNN} — {name}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     A Logical Component is ONE addressable unit of build. It is not a Product Component: a PC is a
     domain slice and the box at C4 L3; an LC is something you can point at and change.

     `lc_type` decides where this prose lives, and the mapping is not negotiable:
       ui-screen · ui-composite → .how/<pc>/01-ux/
       ui-element               → .how/_platform/design-system.md
       gateway                  → .how/<pc>/02-contracts/ or 03-integrations/
       service · job            → .how/<pc>/04-components/
       store                    → .how/<pc>/05-model/

     An LC MUST be registered by the time its wave CLOSES — V12 checks that
     every `touches` entry resolves. -->

## Responsibility

<!-- One paragraph. What this unit is answerable for. If it needs "and" more than once, it is
     probably two units. -->

## Depends on

<!-- Other LC ids, and the direction. Dependency direction is a rule carried by the spine, not a
     preference — a dependency pointing the wrong way is a conflict to surface, not to document. -->

## Interface

<!-- What it exposes to the rest of the system. For a gateway this points at the contract in
     02-contracts/ rather than restating it. -->

## Notes

<!-- Anything a builder cannot read off the code. Cut if there is nothing. -->

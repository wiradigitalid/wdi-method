---
type: inventory
kind: db                 # db · api · screen · endpoint — decides the row shape below
scope: _platform         # `_platform` for the three product-level inventories; `{pc}` for kind: endpoint
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
updated: '{YYYY-MM-DD}'
derived_from: plan       # plan · code — see the TEMPLATE GUIDE
verified: ''             # commit SHA the derivation was read at; required when derived_from: code
---

# Inventory — {tables | endpoints | screens | endpoints of {pc}}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     ONE template, four kinds. Only the row shape differs; the rules are the same for all four.

       kind: db      -> .how/_platform/inventory-db.md
       kind: api     -> .how/_platform/inventory-api.md
       kind: screen  -> .how/_platform/inventory-screen.md
       kind: endpoint-> .how/<pc>/02-contracts/00-inventory.md, at mode: deep only

     The first three are BLUEPRINT output, born at G3 by wdi-blueprint intent `platform`. They exist
     at every `mode`, including catalog, and they are what makes catalog usable at all: the use case
     list plus these three plus C4 is the whole record a builder gets there.

     THE NUMBER IS STABLE. A new row takes the next `No`, never a renumber. Renumbering renames every
     file after it and breaks every link pointing at them. A removed row keeps its number and its
     status becomes `removed`; the number MUST NOT be reused.

     TWO WAYS THIS FILE COMES TO EXIST, and derived_from says which:
       plan  no code yet. Written as intent — the tables, endpoints, or screens planned. Nothing can
             be derived, because there is no source.
       code  code exists. Derived by .constitution/method/scripts/inventory.py, reading this product's
             patterns from .constitution/project/inventory-readers.py — and THEN compared with the plan.
             The difference is a FINDING, reported. It MUST NOT be patched into agreement by hand.

     MUST NOT be assembled from a README, from a route name that looks plausible, or from memory. -->

## Rows

<!-- kind: db -->

| No | Table | Owning component | What it holds | Key columns | Status |
| --- | --- | --- | --- | --- | --- |

<!-- kind: api  — keep this block and delete the others
| No | Method | Path | Owning component | Description | Status |
| --- | --- | --- | --- | --- | --- |
-->

<!-- kind: screen
| No | Screen | Route | Owning component | Actor | UC served |
| --- | --- | --- | --- | --- | --- |
-->

<!-- kind: endpoint
| No | Method | Path | Spec file | Status |
| --- | --- | --- | --- | --- |
-->

<!-- Status values: draft · published · deprecated · removed. A row with no status reads as
     published, which is the one reading that is never safe. -->

## Findings

<!-- Only when derived_from: code. Each difference between the plan and what the code actually does,
     one line each, with which side is being reported — not which side was changed. Nothing here is
     resolved by editing the other side; a finding routes to the skill that owns it. -->

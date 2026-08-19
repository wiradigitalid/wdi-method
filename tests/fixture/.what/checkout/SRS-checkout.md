---
type: srs
component: checkout
status: reviewed
mode: outline
reviewed:
  date: '2026-01-01'
  sha: '0000000'
  by: fixture
  lenses: [edge-case-hunter]
---

# SRS — Checkout

## Actor Register · [G3]

| Actor | Is |
| --- | --- |
| Visitor | Somebody buying without an account |

## UC Catalogue · [G3]

| id | Use case | Actor | Satisfies | critical |
| --- | --- | --- | --- | --- |
| UC-1 | Place an order without an account | Visitor | FR-1 | yes |
| UC-2 | Reopen my last order | Visitor | FR-2 | no |

## Constraints · [G3]

An order MUST be readable by the code given at checkout.

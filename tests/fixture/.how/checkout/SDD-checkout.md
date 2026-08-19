---
type: sdd
component: checkout
status: reviewed
mode: outline
reviewed:
  date: '2026-01-01'
  sha: '0000000'
  by: fixture
  lenses: [edge-case-hunter]
---

# SDD — Checkout

## Decision Summary

One writer owns `orders` and `order_lines`. Both are written in one transaction — `DEC-001`.

## Structure

| Logical Component | Does | Container |
| --- | --- | --- |
| `checkout.orders` | Writes an order and its lines | `app` |

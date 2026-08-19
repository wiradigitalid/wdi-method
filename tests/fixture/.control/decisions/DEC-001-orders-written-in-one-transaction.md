---
type: decision
id: DEC-001
status: applied
title: "Orders are written in one transaction"
date: '2026-01-01'
touches:
  - .how/checkout/SDD-checkout.md
---

# DEC-001 — Orders are written in one transaction

## Decision

An order and its lines are written in one transaction, or not at all.

## Why

A half-written order is indistinguishable from a paid one, and the visitor has no account to
recover it from.

## Trace

`.how/checkout/SDD-checkout.md` § Structure.

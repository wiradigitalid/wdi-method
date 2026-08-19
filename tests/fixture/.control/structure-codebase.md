---
type: structure
scope: codebase
verified: '2026-01-01'
commit: '0000000'
---

# Codebase Structure

## Verified

2026-01-01 at `0000000`. A fixture: small on purpose.

## Top level

```text
fixture/
└── app/                      # [container: app] the one thing we build
```

## Containers

### app

```text
app/
└── orders.go                 # ★ the one writer of orders and order_lines
```

`★` marks a key file.

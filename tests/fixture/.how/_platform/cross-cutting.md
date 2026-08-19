---
type: cross-cutting
status: draft
---

# Cross-cutting

## Error envelope

Every API error carries `code` and `message`.

## Platform-owned

| What | Kind | Why no component explains it | Who touches it | The shape every toucher obeys |
| --- | --- | --- | --- | --- |
| `audit_log` | data | Every component writes to it and none of them promises it | `checkout`, and any component added later | Append-only; a row is never updated |

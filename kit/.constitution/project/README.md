---
status: Accepted
scope: project-room
---

# `.constitution/project/` — this product's custom rules

**This folder belongs to the product, not to the method.** It is seeded once at install, and after
that `wdi-method update` **never** writes over a file in it. `wdi-method promote` **skips it entirely**,
so nothing you write here can reach the public package.

This README is the one exception: it is authored in the package and `promote` never carries it home.
You MAY edit it, but the edit will not survive the next install elsewhere — so **your rules MUST be
other files.**

## What goes here

Normative rules that hold **only in this product**, and are not code conventions:

- a review policy a client requires
- a process rule that came out of a contract
- a naming or language policy that differs from the method default
- a prohibition or obligation specific to this domain

## Not a rule, but it lives here anyway

`inventory-readers.py` — how this product's code is read, for the three inventories. It sits in the
room for the same reason the rules do: the method's engine is generic, reading a stack is not, and
`update` MUST NOT overwrite what a product wrote about its own code. What ships is a **skeleton** —
no patterns, no stack — and `wdi-init` intent `readers` fills it in against this repo. `custom-room-declared` does not
look at it: only `.md` is a rule.

## What does not

| The thing | Its home |
|---|---|
| Product or client name | `.control/registry/index.yaml` → `product:` |
| Code conventions, stack, brownfield patterns | `codebase-*-guide.md`, here in this room — protected at **any** `status:` |
| Scope, method ownership, repo checklist | `constitution.md` Articles 1, 2, 5, here in this room |
| Agent instructions for this product | `AGENTS.md`, **outside** the marked `wdi-method` block |
| BMad overrides for this product | `_bmad/custom/*.user.toml` |
| State, promises, design | `.control/` · `.what/` · `.how/` |

**A generic rule MUST NOT be moved here.** If it holds in any project, it belongs to the package — fix
it there, then `promote`. Using this room to bypass the package is how a method stops being generic
with nobody deciding it, and **an empty room is a valid state**: filling it so that it gets used is the
very failure this rule prevents.

## The shape of a file here

Frontmatter is required, and `custom-room-declared` checks it:

```yaml
---
scope: project              # REQUIRED, and exactly this value
purpose: ""                 # REQUIRED, one line: what this rule protects
overrides: null             # optional: the kit file it narrows or contradicts
decision: null              # REQUIRED when `overrides:` is set — the DEC- that decided it
---
```

- A file here MAY **narrow** or **add to** a generic rule with no `overrides:` at all.
- To **contradict** a generic rule it MUST name that rule in `overrides:` and carry `decision:`.
  Without both, this room becomes the place where generic rules are broken with no trace — and that is
  what stops a method being trustworthy in the next repo.
- An `overrides:` pointing at a file that does not exist is a finding, not a typo: it means the rule
  being contradicted is gone, and the contradiction may no longer have a reason.

## Why whole files, and not marked blocks

`AGENTS.md` uses a marked block because it is **one** file. `.constitution/` has fifty-odd, and marked
blocks inside them would make `update` perform surgery in every file — one broken marker and either
the product's rule is erased, or the generic rule freezes forever.

Whole files in their own room avoid both, and they keep a product's rules **readable in one place**
instead of scattered inside fifty files that belong to somebody else.

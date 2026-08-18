# WDI Method

Metode pengiriman perangkat lunak WDI. Membungkus BMad; tidak menggantikannya.

WDI software delivery method. It wraps BMad; it does not replace it.

This repository is **public**. It MUST NOT contain a client name, a product name, or a
link to any other private repository. Product identity lives in the consuming repo, at
`.control/registry/index.yaml` (`product.name`, optional `product.client`), filled at G1.

## Install

BMad first, then WDI Method. The wrappers call BMad skills; without BMad they cannot run.

```bash
cd /path/to/your/product-repo

npx bmad-method install
# pick the agents you use (Claude Code, Cursor, …) in BMad's installer

npx github:wiradigitalid/wdi-method install
# optional: --agents cursor,claude
```

Then, in that repo:

1. Set `product.name` (and `product.client` if there is a client) in `.control/registry/index.yaml`.
2. Rewrite `.constitution/constitution.md` Articles 2 and 5 for this product. Article 1 points at `index.yaml` — do not invent a second name.
3. Merge method routing into `AGENTS.md` if that file already existed.
4. Run skill `wdi-init` intent `setup`.
5. Sort existing documents. A file that is already the artifact one slot asks for goes into that slot through the skill that owns it; everything else goes to `_bmad-output/prior-knowledge/`.

```bash
npx github:wiradigitalid/wdi-method verify
```

## Update

```bash
npx github:wiradigitalid/wdi-method update
```

Update overwrites method files. It MUST NOT touch `.what/`, `.how/`, filled `.control/` state,
existing `constitution.md` Articles 1–2 and 5, `codebase/*-guide.md` once `Accepted`, extra
constitution files this repo added, `AGENTS.md` that already exists, or `_bmad/custom/*.user.toml`.

A stamp is written to `.control/wdi-method.yaml` (`wdi_method`, `bmad_method` if detectable).
It is a trace, not a lockfile.

## Agents

`--agents` chooses **where skills are copied**, not a different method. Default: all.

| Flag | Writes |
|---|---|
| `claude` | `.claude/skills/wdi-*`, `CLAUDE.md` |
| `cursor` | `.agents/skills/wdi-*`, `.cursorrules` |
| `codex` | `AGENTS.md` |
| `antigravity` | `.agents/skills/wdi-*`, `.agents/AGENTS.md` |

`AGENTS.md` is created on first install if missing (every agent reads it). It is never overwritten.

## What travels, what does not

| Travels (the method) | Stays in the product repo |
|---|---|
| `.constitution/` guides, templates, scripts, `method/` | `.control/` `.what/` `.how/` `_bmad-output/` `.work/` |
| fifteen `wdi-*` skills | `constitution.md` that already exists (Articles 1, 2, 5) |
| `_bmad/custom/*.toml` | `codebase/*-guide.md` once `Accepted` |
| | extra files already in `.constitution/` |
| | `_bmad/custom/*.user.toml` |

`.control/` empty stubs are written only when that folder is absent.

## Product name — one room, filled at G1

`.control/registry/index.yaml`:

```yaml
product:
  name: "{product}"   # set at G1; the brief title uses this value
  client: ""          # empty when there is no client
```

The brief at `.what/_product-brief/brief.md` uses that name. `constitution.md` Article 1 cites
the field. Neither document is a second source of the name.

## Gitignore (optional)

This package does not require method files to be committed or ignored. Each product repo decides.
BMad does not mandate it either. A repo that ignores the payload reinstalls with `update`.

Example, if you choose not to commit skills:

```
.claude/skills/wdi-*/
.agents/skills/wdi-*/
```

Do not ignore all of `.constitution/` — Articles 1, 2, 5 and extra product files belong to the
product and MUST stay tracked.

## Carrying a method change into this package

The published source is this repository. A product repo that still holds a newer working copy
of the method MUST promote it here before the change is treated as published.

From a checkout of this repo:

```bash
npx wdi-method promote /path/to/the/product-repo
npm test
git commit && git push
```

`promote` copies the portable method, replaces product-named files with `kit-overlay/`, and
scrubs initiative slugs to the placeholder `ISI-slug-inisiatif`.

Do not run `update` against a repo you are about to promote from — that would overwrite the
newer working copy.

A product name, a client name, or a link to another private repository MUST NOT land in this
tree. If the cleanliness test fails, fix the overlay or the source, never weaken the test.

## Commands

| Command | Direction |
|---|---|
| `install [dir]` | this package → product repo (first time) |
| `update [dir]` | this package → product repo (again) |
| `verify [dir]` | list missing method files |
| `promote <dir>` | product repo → this package (maintainers) |

`install` and `update` share one copy path. `install` seeds empty `.control/` if it is missing.

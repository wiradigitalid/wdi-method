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
npx github:wiradigitalid/wdi-method
```

Tanpa subcommand, installer membuka **TUI**: cek BMad, deteksi install vs update, tanya nama
produk / klien, pilih agen, tampilkan folder yang akan ditulis, lalu langkah sesudahnya.

Folder korpus (`.constitution` `.control` `.what` `.how` `.work`) **bukan** opsi — namanya
identitas metode. Yang dipilih di TUI adalah repo tujuan dan agennya.

Non-interactive (CI):

```bash
npx github:wiradigitalid/wdi-method install --yes --agents cursor,claude --product "Nama Produk"
```

## Update

```bash
npx github:wiradigitalid/wdi-method update
```

Update overwrites method files. It MUST NOT touch `.what/`, `.how/`, filled `.control/` state,
existing `constitution.md` Articles 1–2 and 5, `codebase/*-guide.md` once `Accepted`, extra
constitution files this repo added, or `_bmad/custom/*.user.toml`.

`AGENTS.md` has a marked method block (`<!-- BEGIN:wdi-method -->` … `<!-- END:wdi-method -->`).
Update replaces **that block only** — including how to install and update. Product sections
outside it (`## Code`, extra boundaries) stay. A file without the markers gets the block
injected before `## Code`; existing product prose above `## Language` is kept.

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

`AGENTS.md` is created on first install if missing. On update, only the marked method block
is replaced.

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
| `(no command)` | interactive TUI |
| `install [dir]` | this package → product repo (first time) |
| `update [dir]` | this package → product repo (again) |
| `verify [dir]` | list missing method files |
| `promote <dir>` | product repo → this package (maintainers) |

`install` and `update` share one copy path. `install` seeds empty `.control/` if it is missing.

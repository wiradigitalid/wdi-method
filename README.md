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
| | **`.constitution/project/`** — the product's custom room |
| | `_bmad/custom/*.user.toml` |

`.control/` empty stubs are written only when that folder is absent.

## `.constitution/project/` — the custom room

Everything else in `.constitution/` belongs to the method and is **overwritten** on update. This one
folder is not: `install` seeds it, `update` never writes over a file that exists in it, and `promote`
**skips it entirely** — so a rule that names a client cannot reach this public repository.

| Goes there | Does not, and where it goes |
|---|---|
| A review policy a client requires | product / client name → `index.yaml` `product:` |
| A process rule that came from a contract | code conventions → `codebase/*-guide.md` |
| A policy that differs from the method default | scope, method ownership → `constitution.md` Art. 1, 2, 5 |
| A prohibition specific to this domain | agent instructions → `AGENTS.md`, outside the marked block |

**A generic rule MUST NOT be moved there.** If it holds in any project it belongs to the package — fix
it there and `promote`. Using the room to bypass the package is how a method stops being generic with
nobody deciding it, and **an empty room is a valid state**: filling it so it gets used is the very
failure this rule prevents.

Required frontmatter, checked by `V27` in `validate.py`:

```yaml
scope: project      # exactly this
purpose: ""         # one line: what this rule protects
overrides: null     # optional: the kit file it narrows or contradicts
decision: null      # REQUIRED when `overrides:` is set — the DEC- that decided it
```

A file there MAY narrow or add with none of the last two. To **contradict** a generic rule it MUST name
it in `overrides:` and carry `decision:`; a method that can be contradicted without a decision stops
being trustworthy in the next repo.

**Whole files, not marked blocks.** `AGENTS.md` uses a marked block because it is *one* file.
`.constitution/` has fifty-odd, and blocks inside them would make `update` perform surgery in each —
one broken marker and either the product's rule is erased or the generic rule freezes forever.

The room's own `README.md` is authored in the package and `promote` never carries it home. Edit it if
you like; the edit will not survive the next install elsewhere, so **your rules MUST be other files.**

## Product name — one room, filled at G1

`.control/registry/index.yaml`:

```yaml
product:
  name: "{product}"   # set at G1; the brief title uses this value
  client: ""          # empty when there is no client
```

The brief at `.what/_product-brief/brief.md` uses that name. `constitution.md` Article 1 cites
the field. Neither document is a second source of the name.

## Language — two settings, and nothing else is a choice

The TUI asks two questions; `install`/`update` write the answers to `.control/registry/index.yaml`:

```yaml
policy:
  doc_language: en           # prose of working documents in .what/ .how/ .control/
  doc_filename_language: en  # the slug part of a document filename
```

Non-interactive: `--doc-language <en|id> --doc-filename-language <en|id>`.

**A setting that already exists is kept**, and the run says so. A language somebody already chose is
not the installer's to change behind their back.

Always English, and a skill MUST NOT ask about them:

| | |
|---|---|
| Method terminology | `DEC` `SRS` `SDD` `UC` `FR` `AD`, the gate names, `mode` and `risk_accepted` values |
| Document code prefixes | `UC-` `DEC-` `SRS-` — only the slug after them follows the setting |
| Machine-facing markers | `[NEEDS CONFIRMATION]` `[MISSING]` `[ASSUMED]` `[PARTIAL]`, `yes`/`no` |
| Code identifiers, DB columns, config keys | `language-guide.md` owns this |

**A corpus written before these settings existed is not migrated for them.** `validate.py` accepts both
languages — `yes|ya`, and V23's keyword set is the union of both — so existing documents keep working
and only new writing follows the setting.

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

---
status: Accepted
---

# BMad Guide

**Loaded when:** invoking any BMad skill, or placing its output

BMad supplies the skills; this method supplies the corpus they write into. This guide states which
route we run, where each skill's output belongs, and the places where BMad's defaults would put a
file somewhere this method cannot use.

The per-skill read/write map lives in `bmad-skill-register.md` and MUST NOT be duplicated here.

## Neither of BMad's two routes

BMad offers a sprint route and a stories route. This method ran the stories route, and **now runs
neither.** The engine layer below G5 is `to-spec`, `to-tickets`, `implement`, `tdd`, and `code-review`;
`wdi-build` owns the transition and states which BMad engines are retired.

What survived the change is the **reason** the sprint route was dropped, because it is the same reason
`ticket-status-one-home` still exists. That route keeps status in one hand-edited file: two builders running in parallel
contend for it, and status becomes something a builder declares about itself. Status is read from the
ticket instead, and it MUST NOT be copied into `specs.yaml`.

| Route | Status home | Why not |
|---|---|---|
| Sprint | `sprint-status.yaml` | One hand-edited file, contended, self-declared |
| Stories | story-file frontmatter | Its author, `bmad-spec`, is retired |
| **Ours** | **the ticket itself** | — |

`bmad-create-epics-and-stories` and `bmad-sprint-planning` are **NOT USED**. Neither MUST be invoked,
and neither MUST be named as a gate condition.

## When an engine earns being invoked at all

BMad is a **dependency of this package**: the installer checks for it, `--skip-bmad-check` exists to say so
out loud, and five artifacts here have no other author. Any *further* engine is a different question, and it
has one test:

> **Does it produce something this corpus keeps?**

Yes → it MAY be wrapped, and the wrapper rule applies: invoked through the WDI skill that owns the artifact,
which checks position, verifies against the guide, and lands the result in this method's template. A
non-BMad engine is named in **that skill**, never in `bmad-skill-register.md` — that register is BMad's
inventory, and putting somebody else's skill in it makes the register a lie.

No → **absorb the discipline and invoke nothing.** Prose we could have written is not an engine.

An engine whose output this corpus keeps is invoked even when it is a **plugin rather than part of this
package's install** — `mattpocock-skills:domain-modeling` is the case, and `wdi-blueprint` invokes it. Two
rules make that safe in a repo that does not have it:

- **A missing plugin is a state, not a defect.** Report it once, name the standard the work is still held
  to, and do the work. You MUST NOT block a gate on it, and you MUST NOT report its absence as a finding.
- **The wrapper carries the standard, never the plugin.** What the engine is invoked *for* MUST be written
  in the wrapping skill as behaviours to verify — so the same bar is met either way, and a run that
  produced none of them is reported as a transcription rather than landed.

An engine's **own** artifacts and tests are a separate matter, and the wrapping skill MUST name every one
this corpus already has a home for. `wdi-blueprint` names four for `domain-modeling`, one of which —
`docs/adr/` — is a folder **Article 3 forbids outright**. That is why an engine's write location is pointed
somewhere safe **before** it runs rather than corrected after.

## Skill classes

The criterion is **lifetime**, not importance:

| Class | Criterion | Output home |
|---|---|---|
| **A** | A living document, still correct after the spec has passed | Straight into `.what/` or `.how/` |
| **B** | Living, but its granularity is not configurable | Neutral `_bmad-output/` → the owner in `corpus-guide.md` lands it |
| **C** | Ends when its work does | `_bmad-output/`, committed, not curated |
| **D** | No artifact at all | — |

Class B exists because some skills write several things at once that belong to different layers.
`bmad-ux` is the case: `EXPERIENCE.md` is a promise and `DESIGN.md` is a build detail, and no
configuration can send them to two places.

Which skill lands which class-B output is the ownership table in `corpus-guide.md`. A skill MUST NOT
write into a layer it does not own.

## `_bmad-output/` is committed but not curated

Committing it makes citation by path stable, so a `DEC-` or a PRD MAY point into it. Two rules follow:

- Nothing there is promoted into the corpus. Research, brainstorming, forge, and PRFAQ output stays
  where it lands, permanently.
- A run folder MUST NOT be deleted. The `update` intents re-read the original inputs in place, and
  `bmad-deep-recon` refresh operates on the existing folder.

## `_bmad/custom/*.toml` are live rules, not documentation

The `persistent_facts` inside them are **injected into every BMad run from activation onward**. A skill
name that has been deleted, or a folder that no longer exists, left sitting in there is not merely
stale — it is a live instruction that a worker will carry out.

So every time a `wdi-*` skill is renamed or merged, a folder is deleted, or a document code is
repealed, `_bmad/custom/*.toml` MUST be swept **in the same pass**. No validator guards it — no `V`
reads TOML — so the only things guarding it are this rule and a sweep that includes it.

This lesson was paid for: the consistency sweep of 2026-08-18 used a path list that did not include
`_bmad/custom/`, and five TOML files went on telling workers to land `SCP-` into
`.control/supplements/` through `wdi-correct-course` — three things that no longer exist. **A
verification path list MUST be treated as a minimum, never as a boundary.**

`.claude/skills/bmad-*/customize.toml` is a different thing and MUST NOT be edited — it is overwritten
on every BMad update. What gets swept is `_bmad/custom/`.

## Memlog

**A memlog follows its artifact. What lands in the corpus leaves its memlog in `.control/memlog/`,
because a memlog is not a deliverable.**

```text
.control/memlog/    brief.md · prd-<slug>.md · spine.md · ux.md      class A and B only
```

`memlog.py` accepts `--workspace DIR` (the memlog is always `{DIR}/.memlog.md`) and `--path FILE`.
BMad skills call `--workspace` by default; the class-A home is reached by installing a `--path`
instruction as a `persistent_fact`.

- A class-A or class-B skill MUST use `--path`. `--workspace` MUST NOT be used — it would leave a
  `.memlog.md` inside `.what/` or `.how/`, which `memlog-home` rejects.
- Class-C memlogs stay beside their output in `_bmad-output/`.
- Every memlog MUST carry `artifact:` in its frontmatter, pointing at a file that exists.

## Configuration

Overrides live in `_bmad/custom/*.toml`, installed by `bmad-customize` so the merge is verified.

| Merge behaviour | Applies to |
|---|---|
| Scalar — override wins | `*_output_path`, `run_folder_pattern`, `*_template` |
| Array — **append**, base entries cannot be removed | `persistent_facts`, `doc_standards`, `activation_steps_*`, `external_*` |
| String — replaces the base entirely | `implementation_handoff` |

Two placement rules that are easy to get wrong:

- **`doc_standards` MUST NOT be chosen just because the file is a guide.** Each skill declares what
  its polish pass applies to, and that declaration MUST be read first. `bmad-architecture` excludes
  the spine — *"never to the spine"* — so `architecture-guide.md` installed there would only ever
  polish renderings. A guide governing an artifact outside the polish target MUST be a
  `persistent_fact`.
- **Facts MUST NOT be installed as `doc_standards`.** The two structure maps in `.control/` are
  facts; treating them as standards makes an agent read today's state as a rule.

`config.toml` sets `project_knowledge` to `.control/`. Personal files — `config.user.toml` — belong
to whoever runs the repo and MUST NOT be copied between projects.

## Only five skills review themselves

`doc_standards` exists on `bmad-product-brief`, `bmad-prd`, `bmad-ux`, `bmad-architecture`, and
`bmad-deep-recon`, and it runs two lenses: `structure` and `prose`.

Everything else MUST be reviewed by invoking `wdi-review` explicitly — the spine, every SRS, every
SDD, and every spec's contract. Three lenses never fire on their own anywhere: `adversarial`,
`edge-case-hunter`, and `verification-gap`.

**Code review is not `bmad-review`, and it is not BMad's at all any more.** The panel over a diff is
`code-review`, dispatched by `wdi-build`; it reviews along two axes, Standards and Spec, and both MUST
run. An override placed on `bmad-review` reaches documents only. Getting a document lens onto a diff
still requires calling `wdi-review` by hand, and that is a deliberate act, not a default.

## Renamed and retired

| Old name | Now |
|---|---|
| `bmad-create-prd` · `bmad-edit-prd` · `bmad-validate-prd` | Shims over `bmad-prd` — use the intent, not the shim |
| `bmad-create-architecture` | `bmad-architecture` |
| `bmad-create-epics-and-stories` · `bmad-sprint-planning` | **Not used** — sprint route |
| `bmad-spec` · `bmad-build` · `bmad-build-auto` · `bmad-code-review` · `bmad-retrospective` | **Retired** — the engine layer below G5 is no longer BMad's. Their `_bmad/custom/*.toml` overrides are withdrawn, and `update` removes any still installed |

Roughly a third of the installed skills are deprecated aliases. `bmad-skill-register.md` is the
authority on which is which, and it MUST be consulted rather than guessed from a name that looks
plausible.

## Rules

- A `wdi-*` wrapper, where one exists, MUST be called instead of the skill it wraps. The wrapper
  carries the position and content checks; going around it produces an artifact nothing verifies.
- `bmad-help` MUST NOT be used to answer "where am I". Its progress detection globs paths this method
  redirects, and it names gates this route never produces. Use `wdi-help`.
- Any output with no home in the distillation table MUST be reported as a gap in the method, not
  filed somewhere plausible.

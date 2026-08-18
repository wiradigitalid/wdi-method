---
status: Accepted
---

# BMad Guide

**Loaded when:** invoking any BMad skill, or placing its output

BMad supplies the skills; this method supplies the corpus they write into. This guide states which
route we run, where each skill's output belongs, and the places where BMad's defaults would put a
file somewhere this method cannot use.

The per-skill read/write map lives in `bmad-skill-register.md` and MUST NOT be duplicated here.

## Stories mode only

BMad offers two routes. We run one.

| | Sprint route | **Stories route — ours** |
|---|---|---|
| Planning artifact | `epics.md` | `.what/<pc>/SRS-<pc>.md` + `SPEC.md` + `stories.yaml` |
| Status home | `sprint-status.yaml` | Story-file frontmatter |
| Produced by | `bmad-create-epics-and-stories` · `bmad-sprint-planning` | `bmad-spec` |

`bmad-create-epics-and-stories` and `bmad-sprint-planning` are **NOT USED**. Neither MUST be invoked,
and neither MUST be named as a gate condition.

The sprint route was dropped because it keeps status in a hand-edited file. Two workers running in
parallel then contend for one file, and status becomes something a worker declares about itself.
Reading status from story-file frontmatter removes both problems — V18 checks it.

## Skill classes

The criterion is **lifetime**, not importance:

| Class | Criterion | Output home |
|---|---|---|
| **A** | A living document, still correct after the wave | Straight into `.what/` or `.how/` |
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
  `.memlog.md` inside `.what/` or `.how/`, which V16 rejects.
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
SDD, and every `SPEC.md`. Three lenses never fire on their own anywhere: `adversarial`,
`edge-case-hunter`, and `verification-gap`.

**Code review does not use `bmad-review`.** `bmad-code-review` reads its lenses from a bundled copy
under `review-prompts/`, and each layer ends with an instruction not to invoke any skill. An override
placed on `bmad-review` is therefore **invisible** to code review. Getting the current lenses onto a
diff requires calling `bmad-review` by hand.

## Renamed and retired

| Old name | Now |
|---|---|
| `bmad-create-prd` · `bmad-edit-prd` · `bmad-validate-prd` | Shims over `bmad-prd` — use the intent, not the shim |
| `bmad-create-architecture` | `bmad-architecture` |
| `bmad-create-epics-and-stories` · `bmad-sprint-planning` | **Not used** — sprint route |

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

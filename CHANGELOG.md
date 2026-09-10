# Changelog

What changed in `wdi-method`, newest first. Every entry says what it means for a repo that already has
the method installed — most often nothing beyond `npx wdi-method@latest update`.

A version here is a **git tag**. `npm publish` is a separate, deliberate step (see
[`CONTRIBUTING.md`](CONTRIBUTING.md)), so some versions exist as a tag and a GitHub release without ever
having been served from npm. The registry always holds the newest published version, and a published
version contains every fix below it.

---

## 0.6.19 — 2026-09-10

- **One autopilot run now costs one cloud CI run, not dozens.** A run over fifteen tickets pushed often
  enough to start GitHub Actions at every ticket commit and every spec close, and spent most of a month's
  Actions allowance in two days — a Windows runner bills at 2x the minutes and macOS at 10x, and on a
  private repository every one of those comes out of the allowance. **The fix is not fewer commits**: they
  stay granular, one per ticket, plus the memlog and the registry catch-up. What changed is what a push
  triggers.
  - `wdi-autopilot` gains **§ Cycle-end CI**. Every intermediate push starts nothing; the cloud runner
    fires **once**, at § Finish, when the final head is pushed and the one PR is marked ready for review.
    § Door 2 says an iteration MUST NOT dispatch a workflow or mark a PR ready mid-ticket, and § Finish
    says how the run is triggered at the end — ready-for-review, `workflow_dispatch`, or a final push with
    no `[skip ci]`, in that order of preference.
  - What a spec close is judged on until then is the run branch's **own full suite, run locally** — the
    check that used to be "the last pushed head is green in CI". Nothing closes over red; only the place
    the red is seen has moved to where it costs nothing.
  - Preflight gains a row: **no workflow may fire on an intermediate push.** It is red when one does, and
    it is checked at minute one rather than discovered on the invoice.
  - `wdi-build` Step 5 says the same thing for a supervised run: one unit of work earns one cloud run.
- **New guide — `.constitution/method/ci-guide.md`.** The trigger shape (`workflow_dispatch` always;
  `pull_request` `types: [ready_for_review]` as the one automatic trigger; never a bare `on: push`),
  `paths-ignore` for the prose and corpus layers, `concurrency` with `cancel-in-progress`, and two
  copy-paste templates: `ci.yml` for the product's build and test, and `korpus.yml` for the corpus
  validators, kept separate so the cheap one can still run when the expensive one is ignored.

**What a repo that already has the method installed does about it.** `npx wdi-method@latest update` brings
the guide and the two skills. The workflows themselves are yours and the installer does not write them:
open `.constitution/method/ci-guide.md` and compare your `.github/workflows/` against § Trigger shape. A
workflow with a bare `on: push` is the one that spends the allowance, and it is what the new preflight row
will refuse to start a mandate over.

## 0.6.18 — 2026-09-08

- **This file.** The version history was only readable as `git log`, which is the wrong place to look for
  it when you are deciding how carefully to read an `update` diff.
- **The README had the validator count wrong.** It said twenty-seven; `validate.py` has run twenty-nine
  named checks since `withdrawn-recorded` arrived in 0.6.14. It also now says what the validators treat as
  corpus, which 0.6.17 changed.

## 0.6.17 — 2026-09-08

- **The corpus walker honours `.gitignore`.** The walk pruned only a hardcoded folder list, so a vendored
  dependency tree inside an ignored folder was read as this product's corpus — one repo saw 172
  `cites-resolve` findings from source code it had deliberately ignored. The ignored set is now computed
  once per run (`git ls-files --others --ignored --exclude-standard --directory`), and the hardcoded list
  stays as the fallback for a checkout that is not a git repository. `.gitignore` still cannot hide real
  corpus: `corpus-in-git` fails when a folder the method commits is ignored.
- **`timeline.py` no longer crashes on a capability that has tickets.** `cap_tickets()` returns
  `(spec, ticket)` pairs and the span helper read each item as a ticket row, so generating the timeline
  raised `AttributeError` and `/wdi-report progress` could not publish at all.

**For a consuming repo:** `update`, then regenerate — a `timeline.md` or `report.md` written before this
is dated and must not be read as current.

## 0.6.16 — 2026-09-07

- **A superseded mandate still stands for what it accepted.** `mandate-accept` asked a question about the
  past — was there a mandate on the day this decision was accepted — and answered it with the mandate's
  status *today*. Superseding a mandate, which `wdi-autopilot`'s own instructions call for when a run
  ends, therefore turned every decision that run had accepted permanently red; and an `applied` decision
  is frozen, so there was no repair the corpus was allowed to make. The check now reads the mandate's
  state at the delegation date, and bounds the window by the **earlier** of `mandate.expires` and the date
  of the decision that superseded it — a revoked delegation ends when it was revoked, whatever its
  `expires` still says. `superseded_by` is read from the decision file's frontmatter as well as the
  registry row, because the template puts it there.

## 0.6.15 — 2026-09-07

- The dangling-promise finding carries its own repair. `withdrawn-recorded` named the problem without
  saying what to write, and a finding nobody can act on is a finding that gets switched off.

## 0.6.14 — 2026-09-07

- **New validator `withdrawn-recorded`:** a promise that was withdrawn stays in the registry and says who
  withdrew it. Deleting the row loses the fact that it was ever promised.

## 0.6.13 — 2026-09-07

- A story id already scoped to its wave is not scoped twice — the pre-0.6 rename was double-prefixing ids
  that had been written correctly.

## 0.6.12 — 2026-09-07

- Flattening a pre-rename wave is `wdi-upgrade`'s work, not a re-cut. The skill was inventing a new
  decomposition where it should have been moving one that already existed.

## 0.6.11 — 2026-09-07

- `update` leaves a closed spec's folder where it is. Moving a finished spec's folder rewrote history for
  nothing.

## 0.6.10 — 2026-09-07

- `update` reports the two things `wdi-upgrade` now has to move, instead of leaving them for a reader to
  discover.

## 0.6.9 — 2026-09-07

- The TUI refuses a missing engine too, in step 2's place. The CLI had checked since 0.6.8; the
  interactive path had not, and that is the path a first install actually takes.

## 0.6.8 — 2026-09-07

- **The G5 engines are the repo's own, invocable, and BMad's replacements are locked out.** `install` and
  `update` refuse until `to-spec`, `to-tickets`, `implement`, `tdd`, `code-review` and `domain-modeling`
  are in the repo; `wdi-build` invokes them itself, so `wdi-autopilot` can finish a spec unattended; and
  thirteen BMad skills retired at G5 are denied model invocation. A spec also gets one predefined home,
  `.scratch/<spec-id>-<slug>/`.

**For a consuming repo:** the largest jump in the 0.6 line. The README section *"Moving a repo from 0.6.7
or earlier to 0.6.8"* walks all four changes, and `npx wdi-method engines --fix` repairs what can be
repaired without touching anything you wrote.

## 0.6.7 — 2026-09-06

- `plan-dates` reported nothing at all, because it raised before it could report; and a legacy story file
  was looked for in the wrong folder.
- A closed pre-rename wave stays visible to the RTM instead of disappearing from it.

## 0.6.6 — 2026-09-06

- **New validator `corpus-in-git`:** a folder the method commits MUST NOT be gitignored. A corpus git
  cannot see is a corpus the clone lacks.
- The git rule is stated where the bootstrap reads it, not only where the detail lives.

## 0.6.5 — 2026-09-05

- The README said three things that 0.6.2 through 0.6.4 had made untrue.

## 0.6.4 — 2026-09-05

- The test suite depended on the author's machine, and 0.6.3 failed CI because of it.

## 0.6.3 — 2026-09-05

- The ticket engines are required, and their config ships pre-answered — so `/setup-matt-pocock-skills` is
  not part of getting started.
- *"What now"* is answered after install and after update, in the README and in `wdi-help`.
- Three real migrations, none of them `wdi-upgrade`'s: a mechanical rename, a printed warning, and a skill
  that heals its own ledger.

## 0.6.2 — 2026-09-05

- **New skill `wdi-autopilot`:** one mandate, then every `FR` in scope delivered unattended, every answer
  recorded in one ledger. It stops at one of three places — done, at capacity, or blocked — and one run
  lands as one pull request. An adversarial review closed ten findings before release, two of them in the
  validator.

**For a consuming repo:** `update` renames a pre-0.6.2 ledger to `autopilot-<mandate-id>.md`. The content
is never rewritten.

## 0.6.1 — 2026-09-03

- **New skill `wdi-explain-to-me`:** a decision briefing the owner reads, written in the owner's language.

## 0.6.0 — 2026-09-03

- **Two trees, one home per fact.** The working set points and the rendered page answers, so a human gets
  a complete document while the corpus keeps no copies. This is the release the validators' rule against
  comparing two copies of one fact comes from.
- The units are renamed: wave and story are retired, `waves.yaml` becomes `specs.yaml`, and size decides
  the spec.
- The BMad engine layer below G5 is retired in favour of `to-spec`, `to-tickets` and `implement`;
  `wdi-blueprint` wraps `domain-modeling` as its engine.
- UX runs and **lands** at G2, breaking a deadlock where the container was never in its path.
- A decision's first home is the document it governs, and no `DEC-` is mandatory.
- The corpus is present tense, and stale is not a finding.
- `wdi-review` stopped being a treadmill; gate *shape* and checklist *length* became separate knobs.

**For a consuming repo:** run `wdi-upgrade` after updating, before any other skill. The validators read
the new shape, and a corpus half in the old one answers them wrongly. The untagged 0.5.13 and 0.5.14
bumps — the review panel dropping its two-CLI-family requirement, and the platform picker aligning with
BMad — are included here.

## 0.5.12 — 2026-08-22

- Blueprint actor headings lose the orphaned separator a nameless actor left behind.

## 0.5.11 — 2026-08-22

- Version bump only; no method change.

## 0.5.10 — 2026-08-19

- The inventory engine littered the room it was asked to read.

## 0.5.9 — 2026-08-19

- The package ships no stack at all: a skeleton, and a skill that writes it. A stack baked into a generic
  package is an assumption every consumer inherits.

## 0.5.8 — 2026-08-19

- `inventory.py`: the engine stays in the package, the stack moves to the room that owns it.

## 0.5.7 — 2026-08-19

- The method assumed a stack, and a path was only the visible half of that assumption.

## 0.5.6 — 2026-08-19

- The guard a real component actually needed, which the retired V24 could never have been.

## 0.5.5 — 2026-08-19

- V24 was unsatisfiable for every consumer, and the language sweep had missed nineteen strings.

## 0.5.4 — 2026-08-19

- `portability.md` was right about the path and wrong about everything else.

## 0.5.3 — 2026-08-19

- The 0.5.0 split was unreachable for the repos that needed it.
- Python bytecode is kept out of the tarball — 0.5.2 shipped 123 kB of it, and a `.pyc` embeds the
  absolute path it was compiled from.

## 0.5.2 — 2026-08-19

- **The direction was reversed:** a method change is authored *here* and proven against a fixture corpus
  the registry scripts actually run against, instead of being promoted out of a live product. `promote`
  became a rescue tool that refuses to run without `--rescue`.
- An external audit of 0.5.0 found the `AGENTS.md` block calling the whole kit non-binding.
- Bahasa Indonesia is swept out of the generic package; the installer's interface is English.
- Included here: `.constitution/` becoming exactly two folders, `method/` and `project/` (0.5.0), and the
  0.5.1 republish of a kit that had shipped pre-fix overlay content.

## 0.3.0 — 2026-08-18

- First public release: an interactive installer, a replaceable `AGENTS.md` method block, two language
  settings asked separately, and `.constitution/project/` as the custom room `update` never overwrites and
  `promote` never publishes.

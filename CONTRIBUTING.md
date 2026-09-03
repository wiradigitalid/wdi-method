# Contributing to WDI Method

Thank you for considering it. WDI Method exists to make the middle between *decided* and *coded*
readable by a human — every contribution should make that middle clearer, not thicker.

---

> **Before you write code, open an [issue](https://github.com/wiradigitalid/wdi-method/issues)
> describing what you want to change and why.**
>
> If the change adds a skill, restructures a guide, or touches more than a couple of files, wait for a
> maintainer to weigh in before you invest the time. A change that arrives unannounced has a real
> chance of being asked to shrink or redirect — a two-line issue up front is cheaper than a PR that has
> to be reworked.

---

## Our philosophy

BMad decides *what* to build and *how* to build it well. WDI Method's only job is the review layer
between that decision and the code — sized to what the change actually deserves. Every contribution
should answer one question: **does this make that review layer more trustworthy, or does it just make
it thicker?**

**✅ What fits:**

- A guide, template, or validator that closes a real gap — one you hit in real work, not one imagined
  in the abstract, and provable against the fixture corpus
- A clearer explanation of a rule that already exists
- An installer fix: a broken update path, a lost setting, a message that misleads

**❌ What doesn't:**

- A new document layer, gate, or field "just in case" — depth here is a cost the method exists to
  ration, not to add to
- A rewrite of a guide's voice or structure with no behavioural change behind it
- Anything that assumes one product's stack, domain, or language choice

## Where a method change starts

**Here.** Every method change — a guide, a template, a skill wrapper, a validator — is authored in
this package and proven against the fixture corpus before it is published.

```bash
npm test        # includes the fixture corpus: validate.py, timeline.py, inventory.py all run
```

`tests/fixture/` is a small but complete corpus — one Product Component, two `FR`, two `UC`, an
applied decision, a built container and one that is not, a platform-owned entity, a code map. It
exists so a validator change can be **run** here rather than only reasoned about. It is kept
**green**: a new finding means a regression, and one test deliberately plants a defect in a copy and
requires the matching validator to name it, because a green baseline could otherwise just mean every
check is broken.

Building it immediately found two real defects, which is the argument for it in one sentence: the
V21 section heading was Indonesian while `language-guide.md` says a script-matched key is always
English, and a `sha:` of all digits was read by YAML as the integer `0` and reported as *absent* —
a finding that looked correct and was wrong.

### This direction was reversed on 2026-08-19, and here is what it cost

It used to run the other way: author a rule in a product repo, run it against real work, then
`promote` it here. That bought something real — a rule was always exercised before publishing.

It also had two structural faults that no amount of care fixed. `kit/` is derived and `kit-overlay/`
is source, so the two could disagree with nothing to notice — and in 0.5.0 they did, shipping three
dead links in the index a new install reads first. And nothing consumed the package, so a broken kit
reached the registry with no one to trip over it.

What replaces "it was run before publishing" is two things: the fixture corpus for the mechanical
half, and a consuming repo that updates promptly for the judgement half. A guide that reads well and
helps nobody at G3 is still only provable in use — the difference is that it now surfaces within one
update cycle instead of never.

### `promote` is a rescue tool now, not the workflow

It overwrites the whole kit from one consumer's copy, which silently reverts everything authored here
since that repo last updated. So it refuses to run unless you say you mean it:

```bash
npx wdi-method promote /path/to/the/product-repo --rescue
```

Use it when a method change really was made in a product repo by mistake and has to be recovered.
Read the diff before committing it.

### The installer, the tests, the docs

`bin/`, `lib/`, `tests/`, `kit-overlay/`, this file, the README: edited here directly, as always.

## Reporting issues

Bug reports and feature requests both go through
[GitHub Issues](https://github.com/wiradigitalid/wdi-method/issues). Before opening one, search existing
issues — open and closed — for the same report.

A bug report needs: what you ran, what you expected, what happened instead, and your `wdi-method`
version (`npx wdi-method --help` prints it). A feature request needs: what gap it closes, and — ideally
— the product repo where you hit that gap.

## Pull request guidelines

| Work type | Requirement |
|---|---|
| Typo, broken link, a message that misleads | Just open the PR |
| A new validator, guide, or skill change | Open an issue first; wait for a maintainer's go-ahead |
| Anything touching `kit/.constitution/` | Authored here, and the fixture corpus stays green — see above |

Keep one change per PR. A PR that mixes an installer fix with a guide rewrite makes both harder to
review and neither easier to revert.

### Commit messages

Written in English, one logical change per commit. A short imperative summary line is enough; a body is
welcome when the reasoning is not obvious from the diff.

### AI-assisted contributions

Most of this method is written with AI assistance, and that is fine — say so is not required. What is
required is that **you** can explain every line: why it is correct, why it belongs in this file and not
another, and what breaks if it is wrong. A PR that reads like unreviewed model output — sweeping
rewrites nobody asked for, a rule invented rather than run — will be sent back before it is merged.

## Versioning

`npm version` is the only way the version moves, and **who may move it depends on which part**:

| Part | Who | Why |
|---|---|---|
| **patch** | anyone doing the work, including an agent | A fix, a message, a test, a bug in the installer. It changes nothing a consumer has to think about |
| **minor** | **the maintainer only** | New behaviour means every consuming repo has a decision to make on its next update |
| **major** | **the maintainer only** | A break means somebody's repo needs work before it can update at all |

A contributor or an agent **MUST NOT** run `npm version minor` or `npm version major`. Propose it, say
what changed and why it is not a patch, and leave the release to the maintainer.

The reason is not ceremony. This package **overwrites files** in repos that already hold months of work,
and the version is the only signal a reader has for how carefully to read the diff. A minor released by
whoever happened to be working takes that signal away.

Patch releases are expected to be frequent. That is what a patch is for.

## Releasing — tag first, publish second

The GitHub release is drafted by a workflow; the npm publish is not. `.github/workflows/release.yml`
fires on a `v*` tag, runs `npm test`, refuses a tag that disagrees with `package.json`, and creates the
release with generated notes. It deliberately does **not** run `npm publish`: a patch bump is something
an agent may do, and a workflow that published on tag would hand npm releases to whoever bumped last.

```bash
npm test && npm publish --dry-run                 # below — the only command that shows publish warnings
npm version patch -m "chore(release): %s"         # minor/major: the maintainer only. Commits and tags v<version>
git push --follow-tags                            # a plain push does not send the tag npm version just made
# → Actions: release.yml tests, checks tag == package.json, drafts the GitHub release
npm publish                                       # the maintainer, after that run is green
gh release edit v<version> --notes-file NOTES.md  # optional — replace the generated notes with written ones
```

Then, in a consuming repo, `npx wdi-method@latest update --yes` is the tarball smoke test: the installed
package is not the working tree, and `files` in `package.json` decides what shipped.

## Before you publish

```bash
npm test                    # also runs automatically via prepublishOnly
npm publish --dry-run       # the ONLY command that shows publish-time warnings
npm pack --dry-run          # read the file list; tests/ and SOURCE MUST NOT be in it
```

**`npm pack --dry-run` does not show publish-time warnings, and `--json` output has no `bin` field at
all.** Use `npm publish --dry-run` for the manifest, or you will draw conclusions from a command that
never had the answer. A warning worth acting on looks like this:

```
npm warn publish "bin[wdi-method]" script name bin/wdi-method.js was invalid and removed
```

npm auto-corrects that one and the published package still works — but a package whose manifest depends
on the registry fixing it is a package one npm release away from breaking. `npm pkg fix` says what npm
wants; in that case it was the `./` prefix on the `bin` path.

This repository is **public**. It MUST NOT contain a client name, a product name, or a link to a private
repository. Before publishing, check:

```bash
git grep -ilE "your-client|your-product" -- kit kit-overlay scaffold bin lib README.md tests
```

An empty result is the only acceptable one. `tests/` is in the list because the fixture corpus is the
one place a real product name is easy to paste and never read again. `promote` scrubs the four files that normally carry a product
name, and `walkFiles` refuses build output — a `.pyc` embeds the absolute path it was compiled from,
which is how a client folder name once reached this repo through a file nobody wrote.

## Tests

`node --test tests/*.test.mjs`. A test that mutates `kit/` MUST copy the package to a temporary directory
first: Node runs test files in parallel, and `promote` deletes `kit/` before rewriting it.

## License

By contributing, you agree your contribution is licensed under this repository's [MIT License](LICENSE).

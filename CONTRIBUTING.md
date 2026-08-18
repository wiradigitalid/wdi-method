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

- A guide, template, or validator that closes a real gap — found by running the method on real work, not
  imagined in the abstract
- A clearer explanation of a rule that already exists
- An installer fix: a broken update path, a lost setting, a message that misleads

**❌ What doesn't:**

- A new document layer, gate, or field "just in case" — depth here is a cost the method exists to
  ration, not to add to
- A rewrite of a guide's voice or structure with no behavioural change behind it
- Anything that assumes one product's stack, domain, or language choice

## Where a method change starts

Two places, and which one depends on what you are changing.

**A generic rule** — a guide, a template, a skill wrapper, a validator: change it in a **product repo
that carries the method**, run it against real work, then promote it here. A rule that has never been
run is a rule nobody has tested.

```bash
npx wdi-method promote /path/to/the/product-repo
npm test
```

`promote` copies the portable method, replaces product-named files with their generic versions in
`kit-overlay/`, scrubs initiative slugs, and skips `.constitution/project/` so a product's own rules can
never be published.

**The installer itself** — `bin/`, `lib/`, `tests/`, `kit-overlay/`, this file, the README: change it
here directly. `promote` does not touch any of them.

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
| Anything touching `.constitution/` | Promoted from a product repo where it already ran — see above |

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
git grep -ilE "your-client|your-product" -- kit kit-overlay scaffold bin lib README.md
```

An empty result is the only acceptable one. `promote` scrubs the four files that normally carry a product
name, and `walkFiles` refuses build output — a `.pyc` embeds the absolute path it was compiled from,
which is how a client folder name once reached this repo through a file nobody wrote.

## Tests

`node --test tests/*.test.mjs`. A test that mutates `kit/` MUST copy the package to a temporary directory
first: Node runs test files in parallel, and `promote` deletes `kit/` before rewriting it.

## License

By contributing, you agree your contribution is licensed under this repository's [MIT License](LICENSE).

# Contributing

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

## Versioning

`npm version` is the only way the version moves, and **who may move it depends on which part**:

| Part | Who | Why |
|---|---|---|
| **patch** | anyone doing the work, including an agent | A fix, a message, a test, a bug in the installer. It changes nothing a consumer has to think about |
| **minor** | **the maintainer only** | New behaviour means every consuming repo has a decision to make on its next update |
| **major** | **the maintainer only** | A break means somebody's repo needs work before it can update at all |

An agent or contributor **MUST NOT** run `npm version minor` or `npm version major`. Propose it, say
what changed and why it is not a patch, and leave the release to the maintainer.

The reason is not ceremony. This package **overwrites files** in repos that already hold months of work,
and the version is the only signal a reader has for how carefully to read the diff. A minor released by
whoever happened to be working takes that signal away.

Patch releases are expected to be frequent. That is what a patch is for.

## Before you publish

```bash
npm test            # also runs automatically via prepublishOnly
npm pack --dry-run  # read the file list; tests/ and SOURCE MUST NOT be in it
```

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

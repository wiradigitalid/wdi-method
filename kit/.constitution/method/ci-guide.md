---
status: Accepted
---

# CI Guide

**Loaded when:** writing or changing a GitHub Actions workflow, or deciding whether a push may start a
cloud run

Cloud runners are **metered**, and the meter is not flat: a Windows runner bills at **2×** the minutes it
uses and macOS at **10×**, and on a private repository every one of those minutes comes out of a monthly
allowance. One real run of `wdi-autopilot` over fifteen tickets pushed often enough to start CI dozens of
times and spent most of a month's allowance in two days.

**The fix is not fewer commits.** Commits stay granular — one per ticket, plus the memlog and registry
writes — because that is what makes a run reviewable and resumable. What changes is **what a push
triggers**.

## One unit of work, one cloud run

| | Runs where | When |
|---|---|---|
| Build, typecheck, the full suite **during** the work | **Locally**, on the machine doing the work | Every ticket — `wdi-build` Phase 3 Step 2 already requires it, and it is free |
| The cloud workflow | GitHub Actions | **Once**, when the work is offered for review |

- A workflow MUST be configured so that an intermediate push — a ticket commit, a memlog rewrite, a
  registry catch-up, a spec close — starts **nothing**.
- The cloud run MUST happen before the work is merged. Green CI on the **pushed head SHA** is still the
  release evidence; what moves is how many times it is collected, not whether it is.
- Under a mandate the unit of work is the whole run, so the one cloud run belongs at `wdi-autopilot`
  § Finish. That skill owns the sequence and this guide MUST NOT restate it.
- Where the repo's workflow cannot be changed — a shared org template, a workflow another team owns —
  the run MUST keep intermediate work off the remote instead: hold the push, or make the pushed head
  commit carry `[skip ci]`, which GitHub honours for `push` and `pull_request` events.

## Trigger shape

| Event | Use it | Why |
|---|---|---|
| `workflow_dispatch` | **MUST** be present | The manual re-run. Without it, a red run can only be retried by pushing again |
| `pull_request:` `types: [ready_for_review]` | The one automatic trigger | A draft PR is work in progress; marking it ready is the moment somebody is asking for the verdict |
| `push:` `branches: [main]` | MAY | One run per merge, as the record of trunk health. Drop it where the allowance is tight |
| bare `on: push` | **MUST NOT** | Every branch, every commit, no filter. This is the setting that spends an allowance |

Two consequences worth stating, because both surprise people:

- With `types: [ready_for_review]` and no `synchronize`, a push **after** the PR is ready does not
  re-run CI. Re-run it with `workflow_dispatch`, or convert the PR back to draft and mark it ready
  again. That is the intended trade: the re-run is a decision, not a reflex.
- `concurrency` with `cancel-in-progress: true` stops two runs of the same ref from billing at once.
  Every workflow below sets it.

## What MUST NOT start a build

A change that touches only prose or only the corpus cannot break the code, so it MUST NOT start the
product's build. `paths-ignore` carries that: `**.md`, `.scratch/**`, and the method's own layers —
`.control/**`, `.what/**`, `.how/**`, `.constitution/**`, `_bmad-output/**`, `.work/**`.

The corpus workflow is the **mirror image** of that list and MUST stay a separate workflow: it runs the
validators, on Ubuntu, only when the corpus changed. Keeping the two apart is what lets the expensive one
be ignored while the cheap one still guards the registry.

## Template — `.github/workflows/ci.yml`

The product's build and test. This is the expensive one; the `runs-on` and the two `run:` lines are the
product's, and they come from `.constitution/project/codebase-stack-guide.md`.

```yaml
name: ci

on:
  workflow_dispatch:
  pull_request:
    types: [ready_for_review]
    paths-ignore:
      - '**.md'
      - '.scratch/**'
      - '.control/**'
      - '.what/**'
      - '.how/**'
      - '.constitution/**'
      - '_bmad-output/**'
      - '.work/**'
  # One run per merge, as the record of trunk health. Delete this block where the allowance is tight.
  push:
    branches: [main]
    paths-ignore:
      - '**.md'
      - '.scratch/**'
      - '.control/**'
      - '.what/**'
      - '.how/**'
      - '.constitution/**'
      - '_bmad-output/**'
      - '.work/**'

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    # A Windows runner bills 2× and macOS 10×. Name only the platforms the product actually ships on.
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Replace both lines with this product's build and test commands.
      - run: echo "build command from codebase-stack-guide.md"
      - run: echo "test command from codebase-stack-guide.md"
```

## Template — `.github/workflows/korpus.yml`

The corpus validators. Cheap, Ubuntu, and it runs only when the corpus moved — so it MAY keep the
default `pull_request` trigger, which gives a verdict on the registry while the expensive workflow stays
quiet. `korpus.yml` validates the corpus and **not** the code: a green run here is never build evidence.

```yaml
name: korpus

on:
  workflow_dispatch:
  pull_request:
    paths:
      - '.control/**'
      - '.what/**'
      - '.how/**'
      - '.constitution/**'

concurrency:
  group: korpus-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # The three scripts declare their dependencies inline (PEP 723); uv is what runs them.
      - uses: astral-sh/setup-uv@v5
      - run: uv run .constitution/method/scripts/validate.py
```

## Red flags

- `on: push` with no branch filter, in a repo whose runners are metered
- The product's build and the corpus validators in one workflow — the cheap half then cannot run alone
- A cloud run started to find out whether the code compiles, when the local suite answers that for free
- CI watched per ticket under a mandate, instead of once at § Finish
- A green `korpus.yml` read as a passing build

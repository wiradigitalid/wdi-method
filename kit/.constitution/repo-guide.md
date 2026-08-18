---
status: Accepted
---

# Repo Guide

**Loaded when:** adding a file that is neither code nor corpus, or unsure whether something may be
kept in this repo

Every other guide answers *where in the corpus does this go*. This one answers the question that
comes before it: **does it belong in this repository at all?**

## What this repository is

One product, built for one owner. It holds what is needed to build and run that product, and
nothing that merely relates to it commercially or organisationally.

| MAY be here | MUST NOT be here |
|---|---|
| Application code, configuration, migrations, tests | Proposals, contracts, meeting notes with the client |
| The corpus — `.constitution/` `.control/` `.what/` `.how/` | Contract values, pricing strategy, margins, rate cards |
| Technical documentation, ADR, diagrams | Real customer data, production credentials, tokens |
| Synthetic seed data | Anything whose leak would harm a bargaining position |
| Built deliverables | An archive of commercial documents |

The test is not "is it secret". It is **what changes when this file changes** — a commitment, or how
the thing is built. Only the second belongs here.

## Two failure modes, and why the second is worse

The obvious one is a credential in a commit. It is loud, it is caught, and it has a known remedy.

The quiet one is a **commercial fact restated as a technical one** — a limit that exists because of
what was negotiated, written into an ADR as though it were an engineering constraint. It survives
every scan, it is never noticed as a leak, and it teaches the next reader that the boundary is
soft.

When a technical decision genuinely follows from a commercial one, the ADR MUST state the technical
fact and MUST NOT state the commercial one. *"Retention is 90 days"* is a technical fact.
*"Retention is 90 days because the client would not pay for more"* is a commercial one wearing a
technical coat.

## `.work/` — scratch that is committed

`.work/` holds work in progress that has no home yet: notes while reading an unfamiliar system,
drafts, exploratory output, a working paper for a change spanning several sessions.

It is **committed**, so that a session picked up on another machine finds it, and so a reviewer can
see what a change was actually reasoning about.

It is **ephemeral**, and the two together are what make its rules matter:

- Any durable outcome MUST be moved out before the task closes — to the corpus if it is truth, to
  `_bmad-output/` if it is a run's byproduct.
- Obsolete scratch MUST be deleted when its task closes. `.work/` that only grows stops being
  scratch and becomes a second, unindexed corpus that nobody trusts and nobody deletes.
- Secrets and commercial figures MUST NOT be written here. Being scratch is not an exemption; it is
  the reason people assume it is one.
- Nothing MUST be read from `.work/` as authority. If something there is right, it belongs
  somewhere with an owner.

`.work/` MUST NOT be confused with `_bmad-output/`. That folder holds the output of skill runs, is
never curated, and is cited by path. `.work/` holds what a human or agent wrote by hand while
working, and is meant to empty out.

## Referring to things outside this repository

Engagement context — who the client is, what was agreed, what is due — lives elsewhere. This repo
MUST work without it. An agent MUST be able to act on the rules stated here without opening any
other repository.

When an artifact genuinely needs external context:

- MUST state the technical fact locally, in full.
- MAY name the external source by **repository and path**, as provenance.
- MUST NOT paste the external content in, and MUST NOT replace a technical statement with a pointer
  to a commercial document.

A pointer where a specification should be is the failure this rule exists to stop: the reader who
cannot open that path is left with nothing, and the reader who can is reading the wrong kind of
document.

## How the method arrives

Method files in `.constitution/` (except this product's Articles 1, 2, and 5, `codebase/*-guide.md`
once `Accepted`, and any extra file this repo added), the `wdi-*` skills, and `_bmad/custom/*.toml`
arrive from the public WDI Method package via `npx wdi-method install` / `update`.

At **read time** this repo is self-contained: every file the rules need is here, readable with the
repo alone. At **change time** the method has one published writer — the WDI Method package. Two
rules follow:

- A method file MUST NOT be invented or patched here to improve the method. If a rule is wrong, it
  is fixed in the WDI Method package, then brought here with `update`.
- A rule particular to this repo MUST be written out in full, and MUST NOT be replaced by a pointer
  into another repository.


# Issue tracker

Where issues live for this repo, and what `to-spec`, `to-tickets`, and `triage` read and write.

This file is seeded by `wdi-method`. It is the product's from here on: change the tracker whenever you
like, but keep the three invariants below, because `wdi-build` and the validators read them.

## One root, and the registry is what tells the two apart

Everything lives under `.scratch/`, one directory per effort:

| | Owned by | Lives at |
|---|---|---|
| **A spec** — the work behind an `FR` | `wdi-build`, at G5 | `.scratch/<spec-id>-<slug>/SPEC.md` and `.scratch/<spec-id>-<slug>/issues/<NN>-<slug>.md`, with `spec_folder` in `.control/registry/specs.yaml` naming that directory |
| **Ad hoc work** — a quick bug report, a small idea, engineering-skill scratch | this file's convention | `.scratch/<slug>/` |

**The path no longer says which is which — the registry does.** An effort with a row in `specs.yaml`
is a spec and answers to G5; an effort with no row is ad hoc. That is deliberate: one root means the
engines need no case analysis and `to-tickets` publishes to the same place every time, and it puts the
distinction where something can actually check it.

`<spec-id>` is the id from `specs.yaml` — `.scratch/spec-3-checkout/`, never a bare slug. Left free,
that leaf gets written four different ways in four repos, and one repo managed all four inside itself:
a bare wave number, a `spec-` prefix with no number, a prefix with one, and a slug alone. Every one of
them was allowed, and none could be traced back to the row that owns it. The id in front is what makes
the folder answer to `specs.yaml`.

Ad hoc work that turns out to touch an `FR` **stops and becomes a spec** through `wdi-build` — the Fast
Path rule in `delivery-flow-guide.md` owns that boundary. It gains a row and a rename, not a second home.

## The three invariants

Whatever tracker this repo uses — local markdown, GitHub, GitLab, Jira — these MUST hold:

1. **One parent per spec, one issue per ticket.** A ticket is an issue, never a sub-task: only an issue
   carries native blocking edges, and the frontier is read from them.
2. **Status lives on the ticket itself and nowhere else.** A `**Status:**` line near the top of the
   ticket file, or `status:` in its frontmatter. `ticket-status-one-home` reads it there, and copying it
   into `specs.yaml` is what that validator exists to refuse.
3. **Every ticket names what it `satisfies`** — the `UC` or `FR` behind it. Without it the chain
   `FR → UC → ticket → test` breaks and the RTM cannot say which promise went green.

## Conventions — local markdown

- One effort per directory: `.scratch/<spec-id>-<slug>/` for a spec, `.scratch/<slug>/` for ad hoc work
- The spec, where the size calls for one, is `SPEC.md` in that directory
- One file per ticket at `<effort>/issues/<NN>-<slug>.md`, numbered from `01`, never a single
  combined file
- Blocking edges as a `Blocked by: NN, NN` line near the top
- Comments append at the bottom under a `## Comments` heading

## Switching to a real tracker

Re-run `/setup-matt-pocock-skills` and pick it, then keep the three invariants above. The mapping WDI
Method expects is in `delivery-flow-guide.md` § *Mapping to a tracker*: parent issue is the spec, issue is
the ticket, Fix Version is the release, and the `CAP`/`FR` travel as labels.

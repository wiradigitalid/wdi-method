# Issue tracker

Where issues live for this repo, and what `to-spec`, `to-tickets`, and `triage` read and write.

This file is seeded by `wdi-method`. It is the product's from here on: change the tracker whenever you
like, but keep the three invariants below, because `wdi-build` and the validators read them.

## Two places, and they are not the same place

| | Owned by | Lives at |
|---|---|---|
| **A spec's tickets** — the work behind an `FR` | `wdi-build`, at G5 | `{spec_folder}/issues/<NN>-<slug>.md`, `spec_folder` from `.control/registry/specs.yaml` |
| **Ad hoc work** — a quick bug report, a small idea, engineering-skill scratch | this file's convention | `.scratch/<slug>/` |

`.scratch/` MUST NOT become a second place to plan a feature that already has an `FR`. The moment ad hoc
work turns out to touch an `FR`, it stops and becomes a spec through `wdi-build` — the Fast Path rule in
`delivery-flow-guide.md` owns that boundary.

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

- One effort per directory: `.scratch/<slug>/`
- One file per ticket at `.scratch/<slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single
  combined file
- Blocking edges as a `Blocked by: NN, NN` line near the top
- Comments append at the bottom under a `## Comments` heading

## Switching to a real tracker

Re-run `/setup-matt-pocock-skills` and pick it, then keep the three invariants above. The mapping WDI
Method expects is in `delivery-flow-guide.md` § *Mapping to a tracker*: parent issue is the spec, issue is
the ticket, Fix Version is the release, and the `CAP`/`FR` travel as labels.

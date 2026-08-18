---
type: design-system
scope: _platform
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
updated: '{YYYY-MM-DD}'
---

# Design System — {product}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Home: .how/_platform/design-system.md. Written by wdi-ux, and it is the ONE file in _platform/
     that wdi-blueprint does not own. Optional, like the rest of UX: it exists when the interface is
     a substantial part of what the PRD promises.

     WHY IT IS NOT IN A COMPONENT: tokens and base elements cross Product Components by definition. A
     colour scale living in one component's 01-ux/ is a colour scale the other six will each redefine.

     WHY ux.md DOES NOT SERVE IT: ux.md is the shape of DESIGN.md and EXPERIENCE.md, which are per
     component. This is the third file, at product level, and it had no template at all.

     THE CODE IS THE SSOT FOR VALUES. Where this repo's web side states a token in tokens.css, this
     file MUST reference it rather than repeat the value. Two homes for one hex code is two hex codes
     within a month. Read web/README.md before writing anything here — it is the authority for the
     web side, and it MUST NOT be contradicted from this file.

     Token and element NAMES are English: they are machine-facing keys, per language-guide.md. -->

## Where the values actually live

<!-- One line per source of truth — the stylesheet, the config, the generated file — with its path.
     This section is what stops the rest of the document becoming a stale copy. -->

## Tokens

<!-- One table per scale. Name, what it is for, and where it resolves. NOT the raw value, unless this
     file is genuinely the only place it exists. -->

| Token | For | Resolves in |
| --- | --- | --- |

## Base elements

<!-- The LC type `ui-element`, registered in components.yaml. One row each: what it is, its states,
     and where its implementation lives. A composite reused across screens is `ui-composite` and
     belongs in .how/<pc>/01-ux/, not here. -->

| Element | States it MUST support | Implementation |
| --- | --- | --- |

<!-- Every element MUST state its empty, loading, error, and disabled states where they apply. The
     populated state is the one that always gets designed; the others are the ones that ship broken. -->

## Rules that bind every screen

<!-- Only what a screen cannot legitimately override. Each MUST state what it prevents — a rule with
     no failure behind it is a preference, and preferences go to ../../../project/codebase-conventions-guide.md.

     A rule here that also holds for non-UI code is an AD-N and belongs in the spine instead. -->

| Rule | Prevents |
| --- | --- |

## What this system deliberately does not cover

<!-- Where a component is free to choose for itself. Absent, every local choice reads as a violation. -->

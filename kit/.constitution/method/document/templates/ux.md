---
type: ux
component: '{pc}'
document: design             # design (.how/<pc>/01-ux/) · experience (.what/<pc>/04-usecases/)
created: '{YYYY-MM-DD}'
---

# {DESIGN | EXPERIENCE} — {Product Component}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     bmad-ux produces TWO documents, and they fall in two different layers. This template covers
     both; set `document` and keep only that half.

       DESIGN.md      → .how/<pc>/01-ux/          visual: tokens, components, layout
       EXPERIENCE.md  → .what/<pc>/04-usecases/   behaviour: IA, states, journeys, accessibility

     Keeping them in one file — as most projects do — makes a button-colour change and a flow change
     look equally weighty. They are not.

     Neither lands by itself. bmad-ux writes to _bmad-output/ux/ and wdi-ux lands it. Base
     tokens and shared elements do NOT stay per-component; they go to
     .how/_platform/design-system.md. -->

## DESIGN — visual

<!-- Keep only when document: design. -->

### Tokens

<!-- What is component-specific. Anything reusable MUST be promoted to design-system.md instead —
     a token defined twice is a token that will diverge. -->

### Screens

<!-- One row per screen. Each MUST be registered as an LC of type ui-screen in components.yaml —
     wdi-ux does this in the same act as landing the screen, and `lc-registered` checks it at spec close. -->

| Screen | LC | Purpose |
| --- | --- | --- |

### Layout and states

<!-- Per screen: the states it can be in — empty, loading, error, populated. The empty and error
     states are the ones that get skipped and the ones users hit first. -->

---

## EXPERIENCE — behaviour

<!-- Keep only when document: experience. This half is WHAT, not HOW: it says what the user can do
     and what the system answers, in human language, with no visual detail. -->

### Information architecture

<!-- Top-level surfaces and how someone moves between them. -->

### Journeys

<!-- Reference UJ-N from the PRD rather than restating them; add only what the PRD left implicit —
     screen order, entry state, what tells the user the value landed. -->

### Behaviour per surface

| Surface | User can | System answers |
| --- | --- | --- |

### Accessibility

<!-- What MUST hold: contrast, focus order, target size, screen-reader labelling, motion. State the
     standard being met, not the intention to meet one. -->

### Edge cases

<!-- Real failure moments and what the user does next. One per row; the ones worth writing are the
     ones a designer would rather not think about. -->

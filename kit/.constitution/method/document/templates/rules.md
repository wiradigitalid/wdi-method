---
type: rules
scope: global            # global · component — decides the home and the id prefix
component: '{pc}'        # omit entirely when scope: global
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
---

# Business Rules — {the product | Product Component}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     ONE template, two scopes, and the scope decides everything about where this file lives:

       scope: global     -> .what/business-rules.md          born at G3, by wdi-blueprint
       scope: component  -> .what/<pc>/02-rules/rules-<pc>.md born at G4, from mode: outline up

     THE TEST IS REACH, NOT IMPORTANCE. A rule binding more than one Product Component is global; a
     rule binding only one is that component's. A rule written locally that turns out to bind a
     second component MUST be PROMOTED to the global file, never copied. Two copies of one rule is
     how components start disagreeing about the same policy.

     A rule MUST be checkable. If a reviewer cannot tell whether the behaviour obeys it, it is not a
     rule yet — it is an intention, and it belongs in the SRS prose.

     A rule MUST NOT state a mechanism. "The turn is not consumed until commitment" is a rule; "a
     row is written to the queue table" is a mechanism and belongs to .how/.

     Ids are allocated GLOBALLY and never restart. A retired rule keeps its id and is marked retired
     with what replaced it — never deleted, because documents still cite it. -->

## Rules

| id | Rule | Binds | Source | Status |
| --- | --- | --- | --- | --- |
| BR-{n} | {one checkable sentence, present tense} | {which components, or `all`} | {FR-n · DEC-n · UC-n · a person and a date} | active |

<!-- `Source` MUST name where the rule came from. A rule with no source is an assumption in
     disguise, and it goes through wdi-question instead.

     `Status`: active · retired. A retired row states what replaced it in the Rule column. -->

## Retired

<!-- Rows moved here keep their ids. Each MUST name what replaced it and the date it stopped
     holding. This section MAY be absent until the first rule retires. -->

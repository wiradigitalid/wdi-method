---
type: questions
list: blocking           # blocking · assumptions · external · answered
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
---

# {Blocking Questions | Assumptions | Waiting on an Outside Party | Answered}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     ONE template, four lists, all in .control/questions/. `list:` decides which row shape below
     survives; delete the other three.

     THE SPLIT IS BY WHAT THE READER HAS TO DO — not by subject and not by severity. That is the whole
     design, and it is what the single old list could not express: it reached OQ-146 and the majority
     of its weight was answered entries.

       blocking     holds a gate. Read at every gate. Target <=3 per Product Component
       assumptions  the DEFAULT class. Swept once per gate; MAY be skipped. Holds nothing
       external     waiting on a file, an action, or a credential from outside. Holds GO-LIVE ONLY,
                    never a design gate. Owner and `Sebelum` required on every row
       answered     archive. Closed in place, never deleted

     WHY oq.md IS NOT THIS: oq.md is the shape of ONE question whose discussion outgrew a line, and it
     lives beside these four as OQ-NNN-<slug>.md with a one-line pointer from the list. This is the
     shape of the four LISTS.

     A ROW MOVES BETWEEN FILES WHEN ITS CLASS CHANGES, and it MUST NOT be copied into a second one.

     Ids stay OQ-, allocated from the highest ever used including closed ones. An id MUST NOT be
     reused. The prose inside the tables follows the product's `doc_language`; a machine-facing
     marker such as `[NEEDS CONFIRMATION]` stays English wherever it appears — `language-guide.md`
     owns that split. -->

## The class test

<!-- Keep this block in blocking.md and assumptions.md; delete it from the other two.

     A question is filed in `assumptions` unless it passes one of three tests. One is enough:

       1. It touches money, personal data, or a legal obligation.
       2. It changes the wording of an FR's promise.
       3. Answering it wrong forces a rewrite of more than one Product Component.

     Failing all three, the agent takes the answer itself — and then THE RECORDING THRESHOLD decides
     whether it becomes a row at all. Read `Cost if wrong` first: if it is *one setting changes*, *one
     default changes*, or *a shortcut is added later*, with no rework and nothing built on it, then
     there is NO ROW. The shipping default is the record, and the code says it more reliably than a
     line here. wdi-question owns the rule.

     The threshold never applies to the three tests above. Those always win.

     A question MUST NOT be filed as blocking "to be safe". That habit is what produced 146 ids. -->

## Open

<!-- list: blocking · external -->

| id | Question | Blocks | Whose | Owner | Before |
|---|---|---|---|---|---|

<!-- external.md drops `Whose`: sitting in that file already says who acts. Its shape is
     | id | Question | Waiting on | Since | -->

<!-- list: assumptions — keep this shape instead
| id | Assumption | Cost if wrong | Whose | Taken | By |
|---|---|---|---|---|---|
-->

<!-- `Whose` says who acts, and whether anyone may act yet. Three values, and no others:

       owner            a judgement only the owner can make, and it can be made NOW
       run: <what>      the answer comes from running or measuring something — the AGENT's, not the
                        owner's. It MUST name what to run; "needs testing" is not a value
       frozen: DEC-NNN  an applied decision forbids answering it yet, planning included. When that
                        DEC- lifts or is superseded, the row becomes `owner` with no re-triage

     Without this column the four files still hand the owner one flat pile: in one real corpus, 25 open
     lines of which only 6 were the owner's and answerable. wdi-question MUST report only `owner` rows
     to the owner, and the rest as counts. -->

<!-- An empty list is a legitimate state and MUST be written as one, with the date and one line
     saying why. An empty table with no sentence reads as an unfinished file. -->

## Answered

<!-- list: answered only.

     | id | Question | Answer | Date | By |

     The answer is written beside the question, not in place of it. The record of what was once
     uncertain is what stops the same question being asked again in three months.

     An answer amounting to a decision that is expensive to reverse MUST also go to wdi-decision. This
     list records that an answer arrived; a DEC- records what was chosen and what it cost.

     A FOSSIL IS CLOSED, NOT ANSWERED. A row questioning a rule, a layer, or a validator that has since
     been repealed cannot bite again — it moves here with the repeal as its answer, and it MUST NOT be
     put to the owner as a decision. Check for these FIRST when a list has grown long; they are free. -->

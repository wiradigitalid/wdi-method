---
type: integration
component: '{pc}'
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
updated: '{YYYY-MM-DD}'
provider: '{who owns it outside the team}'
---

# Integration — {third-party name}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Home: .how/<pc>/03-integrations/<name>.md. Written at G4, from mode: guarded up, and only when
     the component actually consumes a third party.

     WHY THIS IS NOT contract.md: contract.md is the shape of an endpoint WE publish, and we can
     change it. This is something SOMEBODY ELSE owns. Two things have no column in contract.md and
     are the whole reason this template exists — who owns it outside the team, and what happens when
     they change it without telling anyone.

     COMMERCIAL FACTS MUST NOT APPEAR HERE. A rate limit that exists because of what was negotiated
     is written as the technical fact — "300 requests per minute" — and never as the negotiation.
     repo-guide.md owns that boundary, and this file is the most common place it leaks. -->

## Who owns it

| | |
| --- | --- |
| Provider | {the organisation} |
| Our contact | {a role, and where the person's name is recorded — not the name} |
| Where credentials live | {the devops repo and path. NEVER the credential} |
| Notice we get before a breaking change | {a period, or `none` — and `none` is the answer that changes the design} |

## What we use it for

<!-- Which FR or UC depends on it, by id. An integration no promise depends on is one we are
     carrying for free. -->

## What we send and receive

<!-- Only the surface we actually touch. A full API description belongs to their documentation, cited
     by URL, and copying it here creates a second version that goes stale silently. -->

| Direction | Operation | Carries | Contains personal data |
| --- | --- | --- | --- |

## When it changes without telling us

<!-- The section that earns this file. For each: how we would notice, how long we would run wrong
     before noticing, and what happens meanwhile. "We would see errors" is not an answer unless
     something is actually watching. -->

| Change | How we notice | Blast radius | What we do |
| --- | --- | --- | --- |

## When it is slow, absent, or lying

<!-- The same three failures the SDD's Failure Behaviour asks about, for this boundary. State the
     timeout, the retry policy, what the user sees, and what gets logged. A retry policy with no cap
     is an outage amplifier. -->

| Failure | Timeout | Retry | What the user sees | What is logged |
| --- | --- | --- | --- | --- |

## What we would do without them

<!-- One paragraph. Not a migration plan — the honest answer, which is sometimes "the feature stops".
     Writing it is what makes the dependency visible before it has to be replaced in a hurry. -->

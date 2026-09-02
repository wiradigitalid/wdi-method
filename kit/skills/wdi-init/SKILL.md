---
name: wdi-init
description: Use for anything that must exist before work can start or continue — scaffolding the registries at install, birthing Product Components after G2, setting or changing a component's mode, setting or reviewing its risk_accepted, refreshing the two structure maps, and writing this product's inventory readers. Six intents. Never writes .what/ or .how/ content beyond a skeleton.
---

# WDI Init

Six intents, one skill, because all six answer the same question: **what has to exist before the
next piece of work makes sense?** A registry row, a folder pair, a depth setting, a risk note, a map
of where things are, a reader that can see this product's code.

| Intent | Does | Precondition | How often |
|---|---|---|---|
| `setup` | Guide the global `mode` setting · scaffold the registries that are still empty · **report** the documents already present, read-only · derive the two structure maps | before G1 | once per project |
| `component` | Propose the slicing from the brief plus every PRD · birth what is accepted: registry row plus `SRS`/`SDD` skeletons · propose `mode`, `risk_accepted`, `risk_note`, `owns` | **G2 passed** | each time a component is born |
| `mode` | Change `mode` — global in `index.yaml`, or one component in `components.yaml`. Guided | — | any time |
| `risk` | Set or review one component's `risk_accepted`, with disclosure of what it touches | the component exists | any time, usually before G4 |
| `structure` | Re-derive `.control/structure-codebase.md` and `structure-document.md` from the tree on disk | — | when folders change, and at spec close |
| `readers` | Write `.constitution/project/inventory-readers.py` for **this** repo's stack, then prove it by running the engine | code exists | once, and again when the code's shape moves |

## Two boundaries

- It **does not sort, move, or delete** an existing document. Intent `setup` reports what is there and
  stops. A file that predates the method enters the corpus only through the skill owning its slot —
  `corpus-guide.md` owns that rule.
- Retiring or renaming a Product Component that already carries an SRS **is not its authority**. That
  goes through `wdi-decision`. Birthing is cheap; retiring is not.

## Intent `setup`

1. Read the tree. Report every document already present, by path, with one line on what it looks like.
   **Read-only.** You MUST NOT move one.
2. Scaffold the registry files that carry no rows yet. A file that already has rows MUST NOT be
   rewritten.
3. Put the global `mode` to the owner. The default is `catalog`; the four values and what each buys are
   in `delivery-flow-guide.md`, and MUST NOT be restated here.
4. Run intent `structure`.

## Intent `component`

1. Read the brief and **every** PRD. A slicing proposed from one PRD is a slicing of one PRD.
2. Propose the list. The naming rule and the presentation rule live in `corpus-guide.md` — a name that
   states a layer, a service, or a pattern MUST be rejected at proposal time, and additions, changes,
   and removals MUST be presented separately with the `FR` behind each.
3. The owner decides. You MUST NOT register a component the owner has not accepted.
4. For each accepted birth, write in one act:
   - the `product_components` row in `.control/registry/components.yaml`, carrying `owns:`
   - `.what/<pc>/SRS-<pc>.md` from `templates/srs.md`
   - `.how/<pc>/SDD-<pc>.md` from `templates/sdd.md`
   - the empty slots each kernel's guide names
5. Run the disclosure below, then propose `mode` and `risk_accepted` per component.

Content SHOULD stay in the kernel until it grows past roughly 400 lines — a suggestion, not a threshold.
The first slot to be split out SHOULD be `04-usecases/`; it is always the largest.

**Logical Components are not born here.** An `LC` is born by the skill that draws it — `wdi-component`
intent `design`, or `wdi-ux` for a screen — and `components.yaml` states the entry shape and the `type`
→ prose-home mapping in its own header. You MAY report an `LC` that looks wrong; you MUST NOT create
one.

**Neither is `platform_owns`.** An entity that no component's promise explains belongs to `_platform`,
and `wdi-blueprint` intent `platform` registers it. You MUST name the candidate and the reason, and you
MUST NOT claim it — and before naming one, you MUST apply the test in `corpus-guide.md`: ask which `FR`
would have to be withdrawn for the entity to stop being needed. If that `FR` exists, the entity belongs
to its component, however platform-shaped the table looks.

## Intents `mode` and `risk` — disclose, then propose

`mode` controls **document depth** and nothing else. `risk_accepted` controls **review intensity** and
nothing else. Their definitions live in `delivery-flow-guide.md`, and what the two chosen together cost is
laid out cell by cell in `.constitution/method/why/mode-risk-map.md` — show it when the owner asks what a
combination buys. What this skill owns is the conversation around changing them.

**You do not judge. You disclose, then propose.** Read the `FR` that fall to the component, then name
what it touches:

- money moving
- personal data
- an irreversible action
- a contractual promise to an outside party
- a third-party integration that cannot be rolled back

Only after that do you propose `mode` and `risk_accepted`.

**Land whatever UX is waiting, in this same act.** A UX run at G2 leaves `EXPERIENCE.md` and `DESIGN.md`
in `_bmad-output/ux/` because their paths contain `<pc>` and there was no `<pc>` yet. Birthing the
components is the moment that ends. Landing goes through `wdi-ux` — it owns those two paths and no other
skill MAY write them — but it is dispatched from here rather than left for the owner to remember. It is
the only deferral left in the flow, and this is where it closes.

**Containers MAY be registered here when they are genuinely already known** — an app, an API, a database
the product plainly has. Then a screen `LC` gets its container the moment it is born and there is no debt
at all. They MUST NOT be guessed to achieve that: `wdi-blueprint` intent `platform` owns the real answer
at G3, and a container invented here is data C4 then has to unpick. Where you are unsure, leave them and
let G3 fill both the containers and the empty `LC` rows in one act.

Raising or lowering `mode` is **free and needs no justification** — it is a preference, and a preference
does not have to be defended. Setting `mode: catalog` on a sensitive component requires nothing, as long
as its review stays hard; that combination is the one the split exists to make sayable.

Two things are not free:

- **`risk_accepted: high` on a component that touches any of the five** requires a named acceptance in
  `risk_accepted_by` — **a person and a date is enough**, written here in `components.yaml` beside the
  risk itself rather than as a separate file. A `DEC-` id is still accepted and still has to resolve.
  `high-risk-named` checks this. On a component that touches none of them, `high` is free.
- **An outside party who will demand the artifacts as a deliverable** — a regulator, an auditor, a
  client through a contract — puts the touched component at `mode: deep` and `risk_accepted: low`,
  whatever the global setting says. That floor MUST NOT be traded against a preference: the risk there
  is not the owner's alone to accept.

> The control is not a veto, it is disclosure. The owner MAY choose fast anywhere, but never without
> knowing what is being staked.

**Lowering `mode` does not delete anything.** A file already written stops being required, and that is
all. Deleting it throws away knowledge already paid for, and a lowered `mode` is a preference — not a
statement that the content was wrong.

**Raising `mode` on a component whose code already runs** produces an **as-built record**, not a design.
`wdi-component` writes it, under the evidence labels `sdd-guide.md` owns.

## Intent `structure`

The rules for what belongs in a map live in `.constitution/method/structure-guide.md`. This intent applies
them; it MUST NOT restate them.

1. **Derive from the tree on disk**, honouring `.gitignore`. A map assembled from what the caller says
   is there is the failure this intent exists to prevent.
2. Classify each base folder. For the codebase map the only test is deployability — a **container** runs
   its own code or stores its own data, a **library** is imported by something else, anything else stays
   a line in the top-level tree or in a non-unit section. Size and importance MUST NOT decide it.
   Container headings MUST be **exactly the `built: true` containers** in `components.yaml`: every
   heading is a registered container, and a `built: false` one MUST NOT get a heading because no code of
   ours lives in it. The match is one-directional, and reading it both ways makes it unsatisfiable.
3. Draw the convention, not the contents. A shape that repeats MUST be written once with a placeholder.
4. Mark key files `★` by the four tests in the guide. Borderline files are left out.
5. Write from `templates/structure-codebase.md` and `templates/structure-document.md`. Template comments
   and the skeleton block MUST be deleted from the finished file.
6. Stamp `Verified` with the date and the commit SHA the tree was read at.
7. Report drift, unclaimed folders, and one-sided Product Components separately. This intent MUST NOT
   fix them.

It MAY be run **read-only** — derive, report the drift, write nothing. That is the right mode when the
caller is unsure: a map is cheap to check and expensive to get wrong.

A hand-edited map MUST be treated as drift: re-derive, then say what the hand edit claimed that the tree
does not support.

## Intent `readers`

`inventory.py` is two halves. Comparing what was derived against the plan, reporting the gap, keeping
the numbers stable — that is the same in every stack and belongs to the method. **Reading the code is
not**, so the package ships a skeleton and no example: an example is a guess about somebody else's
stack, and the whole point of deriving rather than assembling is that nothing is guessed.

The file is `.constitution/project/inventory-readers.py`. All of it is the product's — `update` never
writes over it and `promote` never publishes it — so there is no protected region inside it and
nothing to merge.

1. **Read the repo before writing a line.** Where does the schema live, how are routes registered,
   how are screens declared. A stack you have not confirmed on disk MUST NOT be assumed from a
   filename or a dependency list.
2. Fill `derive_db`, `derive_api`, and `derive_screen`. The contract, the injected names, and the
   column order per kind are in the skeleton's own docstring and MUST NOT be restated here.
3. **Delete the `SKELETON = True` line.** While it stands the engine refuses to run, and that is
   deliberate: a skeleton returning nothing and a product owning nothing read identically.
4. **Prove it, and this step is not optional.** Run `uv run .constitution/method/scripts/inventory.py`,
   then open at least one file each reader claims to have read and confirm the rows match what is
   actually written there. A regex that returns plausible rows from the wrong place is the failure
   mode this intent invites, and running the engine is the only thing that catches it.
5. Whatever a pattern cannot read goes to `unread`. You MUST NOT widen a pattern until it stops
   reporting; an honest `unread` is worth more than a row nobody checked.
6. Report what each reader reads, in one line per kind, and what it deliberately does not.

A kind this product genuinely does not have returns `Derived()` — a real answer. You MUST NOT return
it to make the output quiet.

The rows themselves are **not** yours to land. This intent produces the reader; `wdi-blueprint` intent
`platform` owns the three inventories, and a plan-versus-code gap is its finding to route.

## Rules

- You MUST NOT write `.what/` or `.how/` content beyond a skeleton and its frontmatter. Behaviour is
  `wdi-blueprint` and `wdi-component`; mechanism is `wdi-component`.
- You MUST NOT write into `.constitution/method/`. Intent `readers` writes exactly one file in
  `.constitution/project/`, and nothing else there.
- You MUST NOT fill `mode` or `risk_accepted` with a value the owner has not confirmed. Both are the
  owner's, and a proposal recorded as a decision is the one failure disclosure cannot survive.
- You MUST NOT create a Product Component because a folder would look tidy. A PC no `FR` points at is a
  folder with nothing inside it.
- You MUST NOT put database column types in `03-domain/`. That slot holds the conceptual domain model.

## Output

Intent taken · what was scaffolded, proposed, or refreshed · for `component`, the slicing with the `FR`
behind each row and what the owner accepted · for `mode` and `risk`, what was disclosed before the
proposal · for `structure`, the drift found and what was left unfixed.

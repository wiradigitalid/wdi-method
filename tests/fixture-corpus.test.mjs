// The fixture corpus is what lets a method change be PROVEN in this package.
//
// Before it existed, `validate.py` could not run here at all — there is no .control/, no .what/, no
// .how/ — so the only way to test a validator was to edit a product repo and promote. That is why
// CONTRIBUTING.md used to send you to a product repo first. This file removes that reason.
//
// The fixture is small but COMPLETE on purpose: a validator that skips proves nothing, so it carries
// one Product Component, two FR, two UC, one applied decision, one built container and one that is
// not, a platform-owned entity, and a code map. Building it immediately surfaced two real defects in
// validate.py — the entity-one-writer heading was Indonesian while language-guide.md says a script-matched key is
// English, and a `sha:` of all digits was read by YAML as the integer 0 and reported as absent.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..");
const FIXTURE = path.join(ROOT, "tests", "fixture");
const SCRIPTS = path.join(ROOT, "kit", ".constitution", "method", "scripts");

// `uv` runs the scripts' inline PEP 723 dependencies. If it is missing the checks below cannot run,
// and that MUST be loud: a suite that quietly skips its only Python coverage is how a validator
// change ships untested. CI installs uv, so this only bites a local run.
const HAVE_UV = spawnSync("uv", ["--version"], { stdio: "ignore" }).status === 0;
function requireUv(t) {
  if (HAVE_UV) return false;
  console.error("\n!!  uv is NOT installed — the three registry scripts were NOT exercised.\n" +
                "!!  Install it (https://docs.astral.sh/uv/) or read CI, which does.\n");
  t.skip("uv is not installed — see the message above");
  return true;
}

// PYTHONDONTWRITEBYTECODE is not tidiness. Running a script from kit/ writes
// kit/.constitution/method/scripts/__pycache__/*.pyc, and a .pyc embeds the ABSOLUTE PATH it was
// compiled from — so the act of testing would plant a machine path inside the published surface.
// check-clean caught it the first time these tests ran, which is the whole reason that check exists.
const PY_ENV = { ...process.env, PYTHONDONTWRITEBYTECODE: "1" };

function runScript(name, args = []) {
  return execFileSync("uv", ["run", path.join(SCRIPTS, name), "--root", ".", ...args],
                      { cwd: FIXTURE, encoding: "utf8", env: PY_ENV,
                        stdio: ["ignore", "pipe", "pipe"] });
}

test("the fixture corpus is GREEN — so any new finding is a regression, not noise", (t) => {
  if (requireUv(t)) return;
  let out;
  try {
    out = runScript("validate.py");
  } catch (e) {
    // exit 1 means findings; the output still matters, so read it rather than only failing
    out = `${e.stdout || ""}${e.stderr || ""}`;
  }
  assert.doesNotMatch(out, /Traceback/, `validate.py crashed:\n${out}`);
  assert.match(out, /GREEN — no findings/,
    `the fixture MUST stay green, or it stops being a baseline. Output:\n${out}`);
});

test("a defect planted in the fixture IS caught — the baseline can actually fail", (t) => {
  if (requireUv(t)) return;
  // A green fixture proves nothing on its own: it could be green because every validator is broken.
  // So plant one defect in a COPY and require the matching validator to name it.
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-fixture-"));
  fs.cpSync(FIXTURE, tmp, { recursive: true });
  const nfr = path.join(tmp, ".control", "registry", "requirements-checkout-v1.yaml");
  // `\r?\n`, not `.*\n`: in JavaScript `.` excludes \r as well as \n, so on a CRLF checkout the
  // pattern `.*\n` never matches a whole line. Python's `.` excludes only \n, which is why the same
  // pattern worked when I tried it there first and silently removed nothing here.
  fs.writeFileSync(nfr, fs.readFileSync(nfr, "utf8").replace(/^[ \t]*enforced_by:.*\r?\n/m, ""));
  try {
    let out;
    try {
      out = execFileSync("uv", ["run", path.join(SCRIPTS, "validate.py"), "--root", "."],
                         { cwd: tmp, encoding: "utf8", env: PY_ENV,
                           stdio: ["ignore", "pipe", "pipe"] });
    } catch (e) {
      out = `${e.stdout || ""}${e.stderr || ""}`;
    }
    assert.match(out, /nfr-has-enforcer\s+NFR-1/,
      `nfr-has-enforcer did not catch an NFR with no enforcer, so the green run above proves nothing:\n${out}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("timeline.py and inventory.py run against the fixture without crashing", (t) => {
  if (requireUv(t)) return;
  for (const name of ["timeline.py", "inventory.py"]) {
    let out;
    try {
      out = runScript(name);
    } catch (e) {
      out = `${e.stdout || ""}${e.stderr || ""}`;
    }
    assert.doesNotMatch(out, /Traceback/, `${name} crashed:\n${out}`);
  }
});

test("a validator walks the corpus, not somebody's build output", (t) => {
  if (requireUv(t)) return;
  // Found the first time bima ran as a consumer: cites-resolve used rglob plus an after-the-fact filter, so it
  // had already walked into web/node_modules/ inside an abandoned git worktree, hit a dangling npm
  // workspace symlink, and took the whole run down with FileNotFoundError. A validator that crashes on
  // build output reports nothing about the corpus at all — and `node_modules/` matched only at the
  // root, so a monorepo's real one was never skipped anyway.
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-prune-"));
  fs.cpSync(FIXTURE, tmp, { recursive: true });
  const nested = path.join(tmp, "web", "node_modules", "@scope", "pkg");
  fs.mkdirSync(nested, { recursive: true });
  // a .md that would produce findings if it were read at all
  fs.writeFileSync(path.join(nested, "README.md"), "See `.constitution/does-not-exist.md`\n");
  // and a link to nowhere, which is what actually crashed the run
  try {
    fs.symlinkSync(path.join(tmp, "web", "node_modules", "gone"),
                   path.join(tmp, "web", "node_modules", "@scope", "dangling"), "junction");
  } catch { /* a machine that refuses links still proves the pruning half */ }
  try {
    let out;
    try {
      out = execFileSync("uv", ["run", path.join(SCRIPTS, "validate.py"), "--root", "."],
                         { cwd: tmp, encoding: "utf8", env: PY_ENV,
                           stdio: ["ignore", "pipe", "pipe"] });
    } catch (e) {
      out = `${e.stdout || ""}${e.stderr || ""}`;
    }
    assert.doesNotMatch(out, /Traceback|FileNotFoundError/,
      `validate.py crashed on build output instead of pruning it:\n${out}`);
    assert.doesNotMatch(out, /does-not-exist\.md/,
      `a file inside node_modules was read and reported on:\n${out}`);
    assert.match(out, /GREEN — no findings/, `the corpus itself should still be green:\n${out}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

// ---------------------------------------------------------------------------------------------
// The fixture above is a product corpus with NO .constitution/ — which is why it stayed green
// through a defect that made cites-resolve unsatisfiable for every real consumer. A real install has the
// method tree sitting inside it, and cites-resolve was walking it: the guides cite `.control/...` and
// `.what/...` to teach where a thing GOES, and cites-resolve read every one as this product's claim to
// already have it. Against this small fixture the pre-fix validator produced 25 findings; a
// consumer saw 3 only because a mature corpus happens to own most of the cited files.
//
// So the tree under test here is the one that ships: fixture + kit/.constitution/ + a BMad
// template under `.agents/`, the host that `.claude/skills/bmad-` never covered.
function installedTree() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-installed-"));
  fs.cpSync(FIXTURE, tmp, { recursive: true });
  fs.cpSync(path.join(ROOT, "kit", ".constitution"), path.join(tmp, ".constitution"),
            { recursive: true });
  // Verbatim from BMad's own template — not ours to fork, which is why the skip is by tree.
  const refs = path.join(tmp, ".agents", "skills", "bmad-project-context", "references");
  fs.mkdirSync(refs, { recursive: true });
  fs.writeFileSync(path.join(refs, "template.md"),
                   "Money lives in `src/lib/money.ts` and `src/routes/webhooks.ts`.\n");
  return tmp;
}

/** Run the GENERATING pass and hand back .control/generated/status.yaml. */
function statusAfterGenerate(cwd) {
  try {
    execFileSync("uv", ["run", path.join(SCRIPTS, "validate.py"), "--root", ".", "--generate"],
                 { cwd, encoding: "utf8", env: PY_ENV, stdio: ["ignore", "pipe", "pipe"] });
  } catch { /* findings exit non-zero; the generated files are written either way */ }
  return fs.readFileSync(path.join(cwd, ".control", "generated", "status.yaml"), "utf8");
}

function validateIn(cwd) {
  try {
    return execFileSync("uv", ["run", path.join(SCRIPTS, "validate.py"), "--root", "."],
                        { cwd, encoding: "utf8", env: PY_ENV, stdio: ["ignore", "pipe", "pipe"] });
  } catch (e) {
    return `${e.stdout || ""}${e.stderr || ""}`;
  }
}

test("a corpus with the method tree INSTALLED in it is green — the shape every consumer runs", (t) => {
  if (requireUv(t)) return;
  const tmp = installedTree();
  try {
    const out = validateIn(tmp);
    assert.doesNotMatch(out, /Traceback/, `validate.py crashed:\n${out}`);
    // Named individually rather than by a count: these three are the exact lines a consumer
    // reported, and a count would go green again the moment a different guide grew a bad cite.
    for (const cite of ["pool.go", "money.ts", "webhooks.ts"]) {
      assert.doesNotMatch(out, new RegExp(`cites-resolve.*${cite.replace(".", "\\.")}`),
        `cites-resolve still fails on ${cite}, which no product is able to fix:\n${out}`);
    }
    assert.match(out, /GREEN — no findings/,
      `a healthy install MUST be able to go green. A validator that cannot is lying:\n${out}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("the live-cite net survives that skip — a dangling cite in the product still fails", (t) => {
  if (requireUv(t)) return;
  // The absence-guard rule: this is worthless until it has been SEEN to fail. `.control/` is
  // scanned, so a dangling cite planted there MUST come back RED. If widening the skip ever
  // swallows `.control/`, `.how/`, or `.constitution/project/`, this is what says so.
  const tmp = installedTree();
  try {
    const map = path.join(tmp, ".control", "structure-codebase.md");
    fs.appendFileSync(map, "\nRouting note: see `.what/does-not-exist.md`.\n");
    const out = validateIn(tmp);
    assert.match(out, /cites-resolve\s+\.control\/structure-codebase\.md.*does-not-exist\.md/,
      `cites-resolve stopped catching a dangling cite in a live product file:\n${out}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

// ---------------------------------------------------------------------------------------------
// The delivery half of the registry — one spec, two tickets — was rewritten wholesale when `wave`
// became `spec` and `story` became `ticket`. Eight validators walk it, and until the fixture
// carried real rows every one of them was passing over an empty list, which is not the same thing
// as passing. These are the mutations that were run by hand during that rewrite, kept so the next
// change to any of them has to be seen failing too.

/** Run validate.py over a throwaway copy of the fixture, after `mutate(dir)` has broken something. */
function afterMutation(mutate) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-mutate-"));
  fs.cpSync(FIXTURE, tmp, { recursive: true });
  try {
    mutate(tmp);
    return validateIn(tmp);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

const SPECS = (dir) => path.join(dir, ".control", "registry", "specs.yaml");
const editSpecs = (dir, from, to) =>
  fs.writeFileSync(SPECS(dir), fs.readFileSync(SPECS(dir), "utf8").replace(from, to));

test("ticket-status-one-home fails when a ticket's status is copied into specs.yaml — the one thing it exists for", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) =>
    editSpecs(dir, "      - id: SPEC-1-01", "      - id: SPEC-1-01\n        status: done"));
  assert.match(out, /ticket-status-one-home\s+SPEC-1-01.*status.*specs\.yaml/,
    `a status in the registry beside a status in the ticket file is two homes for one fact:\n${out}`);
});

test("ticket-status-one-home fails when the ticket file is missing, and when it states no status at all", (t) => {
  if (requireUv(t)) return;
  // The file is found by the NUMBER at the tail of the id: SPEC-1-02 -> issues/02-*.md. If that
  // derivation ever breaks, every ticket reports as missing and this is what says so.
  const gone = afterMutation((dir) =>
    fs.rmSync(path.join(dir, "_bmad-output", "specs", "spec-1-checkout", "issues",
                        "02-reopen-an-order.md")));
  assert.match(gone, /ticket-status-one-home\s+SPEC-1-02.*no ticket file/,
    `ticket-status-one-home did not notice a ticket with no file:\n${gone}`);

  // `**Status:**` is a BODY line, not frontmatter — a ticket file is a tracker payload, and
  // trackers do not read YAML. Reading only frontmatter would make every engine-written ticket
  // report as statusless.
  const silent = afterMutation((dir) => {
    const f = path.join(dir, "_bmad-output", "specs", "spec-1-checkout", "issues",
                        "01-place-an-order.md");
    fs.writeFileSync(f, fs.readFileSync(f, "utf8").replace(/^\*\*Status:\*\*.*\r?\n/m, ""));
  });
  assert.match(silent, /ticket-status-one-home\s+SPEC-1-01.*states no status/,
    `ticket-status-one-home accepted a ticket file that states no status anywhere:\n${silent}`);
});

test("no-cycles fails on a blocked_by cycle — a frontier that is empty from the first tick", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) => editSpecs(dir, "        blocked_by: []", "        blocked_by: [SPEC-1-02]"));
  assert.match(out, /no-cycles\s+SPEC-1-0[12].*blocked_by.*cycle/,
    `two tickets blocking each other were accepted; no work can ever start:\n${out}`);
});

test("parallel-tickets-blocked fails when two tickets share a `touches` with no blocking edge between them", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) => editSpecs(dir, "        blocked_by: [SPEC-1-01]", "        blocked_by: []"));
  assert.match(out, /parallel-tickets-blocked\s+SPEC-1-01 \+ SPEC-1-02.*money/,
    `parallel-tickets-blocked reads the ticket-level edge as \`blocked_by\` now, not \`depends_on\`:\n${out}`);
});

test("spec-after-g4 fails when a spec touches a component whose G4 has not passed", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) => {
    const f = path.join(dir, ".control", "registry", "components.yaml");
    fs.writeFileSync(f, fs.readFileSync(f, "utf8").replace(/g4_passed: .*/, "g4_passed: false"));
  });
  assert.match(out, /spec-after-g4\s+SPEC-1 \/ checkout.*g4_passed/,
    `work was allowed to start on a component that has not been through its gate:\n${out}`);
});

test("uc-scheduled fails when a UC of an already-touched component is scheduled to no ticket", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) => editSpecs(dir, "        satisfies: [UC-2]", "        satisfies: []"));
  assert.match(out, /uc-scheduled\s+UC-2.*not scheduled to any ticket/,
    `a promise was left behind by a spec that had already opened its component:\n${out}`);
});

test("open questions are counted by WHOSE they are, not as one flat number", (t) => {
  if (requireUv(t)) return;
  // A flat "25 open" is what made a six-item list read as twenty-five items of homework. The owner
  // can only act on the `owner` rows; the rest are waiting on a measurement the agent owes, or
  // frozen by an applied DEC-. The split has to be MECHANICAL — a rule in a skill that nothing
  // checks is a rule that holds until the first busy session.
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-whose-"));
  fs.cpSync(FIXTURE, tmp, { recursive: true });
  try {
    const status = statusAfterGenerate(tmp);
    assert.match(status, /open_by_whose:/,
      `the question count is still flat — the owner cannot tell their two rows from the other three:\n${status}`);
    // The fixture carries exactly one row of each kind, on purpose. Asserting the numbers rather
    // than the key means a parser that silently stops recognising `run:` or `frozen:` is caught.
    for (const [key, n] of [["owner", 2], ["run", 1], ["frozen", 1], ["unstated", 1]]) {
      assert.match(status, new RegExp(`${key}:\\s*${n}\\b`),
        `open_by_whose.${key} should be ${n} — the fixture holds exactly that many:\n${status}`);
    }
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("a `frozen:` row is not counted as the owner's, even sitting in the same file", (t) => {
  if (requireUv(t)) return;
  // The failure this guards: a row nobody may answer yet, put in front of the owner as a decision.
  // One real corpus froze six lines under one applied DEC- and listed all six as open homework.
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-frozen-"));
  fs.cpSync(FIXTURE, tmp, { recursive: true });
  const f = path.join(tmp, ".control", "questions", "assumptions.md");
  fs.writeFileSync(f, fs.readFileSync(f, "utf8").replace("frozen: DEC-001", "owner"));
  try {
    const status = statusAfterGenerate(tmp);
    assert.match(status, /owner:\s*3\b/,
      `flipping one row to \`owner\` MUST move the count — otherwise \`Whose\` is being ignored:\n${status}`);
    assert.match(status, /frozen:\s*0\b/,
      `the frozen count did not drop, so the two classes are not actually separated:\n${status}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

// high-risk-named is a DISCLOSURE control, not a filing requirement. It exists so an owner cannot accept a risk on
// a component that touches money or personal data without saying, on the record, that they accepted it.
// It used to demand that record be a separate `DEC-` file — which made accepting a risk cost a document,
// and put the fact in a second place when `components.yaml` already has the field for it.
//
// What MUST survive the change: `high` on a sensitive component with NOTHING in `risk_accepted_by` is
// still red. What MUST become legal: a person and a date, written where the risk is set.
function componentsWith(dir, replacements) {
  const f = path.join(dir, ".control", "registry", "components.yaml");
  let text = fs.readFileSync(f, "utf8");
  for (const [from, to] of replacements) text = text.replace(from, to);
  fs.writeFileSync(f, text);
}

test("high-risk-named still fails when a sensitive component accepts high risk and names nobody", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) =>
    componentsWith(dir, [["risk_accepted: low", "risk_accepted: high"]]));
  assert.match(out, /high-risk-named\s+checkout.*risk_accepted_by/,
    `an owner accepted a money risk with no record of who accepted it, and nothing said so:\n${out}`);
});

test("high-risk-named accepts a person and a date — the record does not have to be a DEC- file", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) =>
    componentsWith(dir, [[
      "risk_accepted: low",
      "risk_accepted: high\n    risk_accepted_by: \"Wira, 2026-09-01\"",
    ]]));
  assert.doesNotMatch(out, /high-risk-named/,
    `naming a person and a date in components.yaml IS the disclosure. Demanding a separate DEC- file `
    + `makes accepting a risk cost a document, and puts the fact in a second home:\n${out}`);
});

test("high-risk-named still resolves a DEC- reference when one is given", (t) => {
  if (requireUv(t)) return;
  // The looser rule MUST NOT become "anything non-empty passes". A repo that points at a decision is
  // making a checkable claim, and a pointer to a decision that does not exist is worse than no pointer.
  const out = afterMutation((dir) =>
    componentsWith(dir, [[
      "risk_accepted: low",
      "risk_accepted: high\n    risk_accepted_by: DEC-404",
    ]]));
  assert.match(out, /high-risk-named\s+checkout.*DEC-404/,
    `a dangling DEC- reference was accepted because it was merely non-empty:\n${out}`);
});

// An `LC` born before its container exists is the price of running UX at G2, where UX belongs: the
// screens are known as soon as DESIGN.md is written, and containers are not born until G3.
//
// container-built already tolerated an empty `container` — it guards `if ctr and ...` — so the LC could always be
// registered early. What was missing was the DEADLINE. An empty container with nothing ever demanding
// it is invisible debt: a screen with no deployable home, and no pass that notices.
//
// The deadline is derived rather than scheduled: the moment the LC's own PC has containers, the
// information exists, so the answer is owed. Silent before G3, automatic after, and no ceremony.
const LC_NO_CONTAINER = `
  - id: LC-1
    type: ui-screen
    component: checkout
    area: checkout.ui
    container: ""
    owner: wdi-ux
`;

test("an LC with no container is SILENT while its PC has no containers either", (t) => {
  if (requireUv(t)) return;
  // The quiet period is the point. Demanding the answer at G2, when containers do not exist, is the
  // blocking precondition this replaces — it would make the new rule as expensive as the old one.
  const out = afterMutation((dir) => {
    componentsWith(dir, [
      ["logical_components: []", `logical_components:${LC_NO_CONTAINER}`],
      ["    containers: [app]", "    containers: []"],
    ]);
  });
  assert.doesNotMatch(out, /container-built\s+LC-1/,
    `an LC was asked for a container before its PC had any — that is the answer at its thinnest:\n${out}`);
});

test("once its PC has containers, an LC with none is a finding", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) =>
    componentsWith(dir, [["logical_components: []", `logical_components:${LC_NO_CONTAINER}`]]));
  assert.match(out, /container-built\s+LC-1.*container/,
    `checkout already lists a container, so LC-1's empty one is answerable and owed. Without this the `
    + `screen has no deployable home and no pass ever notices:\n${out}`);
});

// ---------------------------------------------------------------------------------------------
// The generated brief and PRD deliverables (0.5.38): the working documents cite ids, the registry
// carries the text, and `--generate` assembles a self-contained page for a reader who should not
// need to open the registry. These tests prove the round trip — a fact written ONCE in the
// registry shows up in the rendered page, and is genuinely absent from the working document.

function briefPrdCorpus() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-brief-prd-"));
  fs.cpSync(path.join(ROOT, "scaffold"), tmp, { recursive: true });
  fs.mkdirSync(path.join(tmp, ".constitution"), { recursive: true });
  fs.cpSync(path.join(ROOT, "kit", ".constitution", "method"),
            path.join(tmp, ".constitution", "method"), { recursive: true });
  fs.mkdirSync(path.join(tmp, ".what", "_product-brief"), { recursive: true });
  fs.mkdirSync(path.join(tmp, ".what", "_prd", "checkout-v1"), { recursive: true });

  fs.writeFileSync(path.join(tmp, ".what", "_product-brief", "brief.md"), `# Product Brief: Shopfront

## Why

Shopfront lets a visitor buy without creating an account.

## The Problem

Visitors abandon at account creation.

## Who This Serves

| Role | Need | Tier |
|---|---|---|
| Visitor | Buy without friction | **primary** |

## Goals

Goals — see requirements.yaml → goals:.

## Success Criteria

40% of visitors who start checkout finish it, within three months of launch.

## Scope

### Scope In

Guest checkout.

### Scope Out

- No account system in v1.

## Constraints

- MUST NOT store card numbers directly — PCI scope forbids it.
`);

  fs.writeFileSync(path.join(tmp, ".what", "_prd", "checkout-v1", "prd.md"), `# PRD: Checkout v1

## Revision History

| Date | What changed | Why | Releases affected |
|---|---|---|---|
| 2026-01-01 | Initial version | — | v1 |

## 1. Why This Initiative

This initiative IS the product's Why; see brief.md.

## 2. Target User

### 2.1 Jobs To Be Done

- Buy one item fast without signing up.

## 3. Features

### 3.1 Guest Checkout

**Capability:** CAP-1 — serves BG-1.

**Description:** A visitor places an order without an account.

**Realizes:** FR-1

## 4. MVP Scope

### 4.1 In Scope

- Guest checkout.

### 4.2 Out of Scope for MVP

- Saved cards, deferred to v2.

## 5. Success Metrics

**Primary**
- **SM-1**: Checkout completion rate — target 40%. Validates FR-1.

## 6. Cross-Cutting NFRs

- NFR-1

## 7. Constraints and Guardrails

none beyond the brief.
`);

  fs.writeFileSync(path.join(tmp, ".control", "registry", "goals.yaml"), `goals:
  - id: BG-1
    title: "A visitor can buy without an account"
`);
  fs.writeFileSync(path.join(tmp, ".control", "registry", "requirements-checkout-v1.yaml"), `capabilities:
  - id: CAP-1
    goal: BG-1
    title: "Checkout without an account"
    priority: must
    target_release: v1
functional:
  - id: FR-1
    capability: CAP-1
    title: "A visitor can place an order without creating an account"
    proof: "An order exists and the visitor can reopen it"
nonfunctional:
  - id: NFR-1
    capability: CAP-1
    goal: BG-1
    title: "An order write MUST be atomic"
    enforced_by: ["checkout.orders"]
journeys: []
`);
  return tmp;
}

function generateIn(cwd) {
  try {
    execFileSync("uv", ["run", path.join(SCRIPTS, "validate.py"), "--root", ".", "--generate"],
                { cwd, encoding: "utf8", env: PY_ENV, stdio: ["ignore", "pipe", "pipe"] });
  } catch { /* findings exit non-zero; the generated files are written either way */ }
}

test("the generated brief renders a goal's statement from the registry, not from the working brief", (t) => {
  if (requireUv(t)) return;
  const tmp = briefPrdCorpus();
  try {
    const source = fs.readFileSync(path.join(tmp, ".what", "_product-brief", "brief.md"), "utf8");
    assert.doesNotMatch(source, /A visitor can buy without an account\./,
      "the working brief must be a pointer only — this test is void if it already carries the statement");

    generateIn(tmp);
    const rendered = fs.readFileSync(path.join(tmp, ".what-rendered", "_product-brief", "brief.md"), "utf8");
    assert.match(rendered, /^### BG-1 — A visitor can buy without an account$/m,
      `the deliverable did not render the goal as a block from goals.yaml:\n${rendered}`);
    assert.doesNotMatch(rendered, /…/, "a human page is complete — no cell may be shortened");
    assert.match(rendered, /Shopfront lets a visitor buy without creating an account\./,
      "the deliverable did not carry the brief's own Why paragraph verbatim");
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("the generated PRD renders an FR's proof of done from the registry, cited but not authored in the working PRD", (t) => {
  if (requireUv(t)) return;
  const tmp = briefPrdCorpus();
  try {
    const source = fs.readFileSync(
      path.join(tmp, ".what", "_prd", "checkout-v1", "prd.md"), "utf8");
    assert.doesNotMatch(source, /An order exists and the visitor can reopen it/,
      "the working PRD must cite FR-1 by id only — this test is void if it already carries the proof of done");

    generateIn(tmp);
    const rendered = fs.readFileSync(
      path.join(tmp, ".what-rendered", "_prd", "checkout-v1", "prd.md"), "utf8");
    assert.match(rendered, /^#### FR-1 — .*\r?\n\r?\n\*\*Proof of done:\*\* An order exists and the visitor can reopen it/m,
      `the deliverable did not render FR-1 as a block with its proof of done from the registry:\n${rendered}`);
    // the block lands under the feature whose `**Realizes:**` names it, before the § Capabilities table
    assert.ok(rendered.indexOf("### 3.1 Guest Checkout") < rendered.indexOf("#### FR-1 — ")
      && rendered.indexOf("#### FR-1 — ") < rendered.indexOf("### Capabilities"),
      "FR-1 must be expanded in place under the feature that realizes it");
    assert.doesNotMatch(rendered, /#{5,} /, "section bodies keep their own heading depth — no demotion into #####");
    assert.match(rendered, /No account system in v1/,
      "the deliverable did not assemble Non-Goals from the brief's Scope Out");
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("changing a requirement's statement in the registry changes the deliverable — it is rendered, not copied", (t) => {
  if (requireUv(t)) return;
  const tmp = briefPrdCorpus();
  try {
    const reqPath = path.join(tmp, ".control", "registry", "requirements-checkout-v1.yaml");
    fs.writeFileSync(reqPath,
      fs.readFileSync(reqPath, "utf8").replace(
        "An order exists and the visitor can reopen it", "REVISED proof of done"));
    generateIn(tmp);
    const rendered = fs.readFileSync(
      path.join(tmp, ".what-rendered", "_prd", "checkout-v1", "prd.md"), "utf8");
    assert.match(rendered, /REVISED proof of done/,
      `a registry edit did not reach the deliverable on regeneration:\n${rendered}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

// ---------------------------------------------------------------------------------------------
// The requirement registry split: `goals.yaml` for the product BG, one
// `requirements-<slug>.yaml` per PRD. It bought one writer per file and cost exactly one new
// failure mode — two initiatives both allocating `FR-12` — which is what id-allocated-once exists for.

const REG = (dir, name) => path.join(dir, ".control", "registry", name);

test("id-allocated-once fails when two requirement files declare the same id — the split's one new failure mode", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) => {
    // A second initiative, written in parallel, re-uses FR-2. Before id-allocated-once this was INVISIBLE:
    // refs-resolve builds its `defined` set as a Set, so the duplicate collapsed and every reference
    // to it still resolved.
    fs.writeFileSync(REG(dir, "requirements-orders-v1.yaml"), `functional:
  - id: FR-2
    capability: CAP-1
    title: "A different promise that stole an allocated id"
    proof: "Nothing — this row should never have been written"
`);
  });
  assert.match(out, /id-allocated-once\s+FR-2.*declared in/,
    `two files declared FR-2 and nothing said so. The global id sequence is what lets a ticket `
    + `say satisfies: [FR-2] without naming its PRD:\n${out}`);
});

test("a corpus still on ONE requirements.yaml stays green — the split is not a flag day", (t) => {
  if (requireUv(t)) return;
  // `update` seeds the product file but MUST NOT move the rows: which PRD an FR belongs to was
  // never recorded, so no tool can split them. The loader unions every requirement file it finds,
  // which is what lets a repo sit half-split for as long as its owner needs.
  const out = afterMutation((dir) => {
    const product = fs.readFileSync(REG(dir, "goals.yaml"), "utf8");
    const initiative = fs.readFileSync(REG(dir, "requirements-checkout-v1.yaml"), "utf8");
    fs.rmSync(REG(dir, "goals.yaml"));
    fs.rmSync(REG(dir, "requirements-checkout-v1.yaml"));
    fs.writeFileSync(REG(dir, "requirements.yaml"), `${product}\n${initiative}`);
  });
  assert.match(out, /GREEN — no findings/,
    `a pre-split corpus went red. An update that breaks every existing repo is not a migration:\n${out}`);
});

test("chain-links still reads a chain that now spans two files — the union is real, not cosmetic", (t) => {
  if (requireUv(t)) return;
  // FR-1 and CAP-1 both live in requirements-checkout-v1.yaml; BG-1 lives in goals.yaml.
  // If the loader read only one file, this would go red for a chain that is actually intact.
  const out = afterMutation((dir) => {
    const p = REG(dir, "requirements-checkout-v1.yaml");
    fs.writeFileSync(p, fs.readFileSync(p, "utf8").replace("    capability: CAP-1\n", "", 1));
  });
  assert.match(out, /chain-links\s+FR-1.*capability/,
    `chain-links stopped seeing FR-1 once its parent moved to another file:\n${out}`);
});

test("CAP lives in its initiative's file, and the PRD deliverable renders it from there", (t) => {
  if (requireUv(t)) return;
  // One file, one writer, one gate. Co-locating CAP with BG was tried first, and the argument for
  // it — that `depends_on` between capabilities crosses initiatives — turned out to buy nothing:
  // no-cycles reads the MERGED view and never opens a file by name. What it DID cost was the property the
  // split was bought for, because `goals.yaml` then had two writers, `wdi-problem` and
  // `wdi-product`, one per section.
  const tmp = briefPrdCorpus();
  try {
    assert.doesNotMatch(fs.readFileSync(REG(tmp, "goals.yaml"), "utf8"), /capabilities:/,
      "goals.yaml carries capabilities again — that is the two-writer shape this reverted");
    assert.match(fs.readFileSync(REG(tmp, "requirements-checkout-v1.yaml"), "utf8"), /capabilities:/,
      "this test is void unless CAP actually sits in the initiative's own file");

    generateIn(tmp);
    const rendered = fs.readFileSync(
      path.join(tmp, ".what-rendered", "_prd", "checkout-v1", "prd.md"), "utf8");
    assert.match(rendered, /### Capabilities/,
      `the deliverable does not render the capability table, so a reader still has to open the `
      + `registry for the one row that carries priority and target release:\n${rendered}`);
    assert.match(rendered, /`CAP-1`.*`BG-1`.*Checkout without an account/,
      `CAP-1 rendered without its goal or its statement:\n${rendered}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("no-cycles still sees a depends_on that crosses two initiative files", (t) => {
  if (requireUv(t)) return;
  // The claim that made co-location look necessary, tested directly: a cycle between capabilities
  // in DIFFERENT files must still be caught. If it were not, moving CAP per-PRD would have broken
  // the one edge the method uses to say "this initiative waits on that one".
  const out = afterMutation((dir) => {
    const p = REG(dir, "requirements-checkout-v1.yaml");
    fs.writeFileSync(p, fs.readFileSync(p, "utf8")
      .replace("    target_release: v1\n", "    target_release: v1\n    depends_on: [CAP-2]\n"));
    fs.writeFileSync(REG(dir, "requirements-orders-v1.yaml"), `capabilities:
  - id: CAP-2
    goal: BG-1
    title: "A capability in another initiative that waits on the first"
    depends_on: [CAP-1]
`);
  });
  assert.match(out, /no-cycles\s+CAP-[12].*cycle among CAPs/,
    `no-cycles stopped seeing a depends_on cycle once the two capabilities sat in different files. That `
    + `edge is how an initiative says it waits on another one:\n${out}`);
});

// A migrated PRD may keep the numbers its kit gave it — `## 4. Features`, `## 8. MVP Scope`. The renderer
// keyed on "3. Features" and went blind: on a real 0.5.12 corpus the rendered PRD lost Features, MVP
// Scope, Success Metrics, Cross-Cutting NFRs, and Constraints, and every FR fell into the fallback list.
test("the rendered PRD finds its sections by NAME — a PRD numbered by an older kit still renders whole", (t) => {
  if (requireUv(t)) return;
  const tmp = briefPrdCorpus();
  try {
    const prd = path.join(tmp, ".what", "_prd", "checkout-v1", "prd.md");
    const renumbered = fs.readFileSync(prd, "utf8")
      .replace("## 3. Features", "## 4. Features")
      .replace("### 3.1 Guest Checkout", "### 4.1 Guest Checkout")
      .replace("## 4. MVP Scope", "## 8. MVP Scope")
      .replace("### 4.1 In Scope", "### 8.1 In Scope")
      .replace("### 4.2 Out of Scope for MVP", "### 8.2 Out of Scope for MVP")
      .replace("## 5. Success Metrics", "## 9. Success Metrics");
    assert.notEqual(renumbered, fs.readFileSync(prd, "utf8"), "the fixture PRD did not carry the headings this test renumbers");
    fs.writeFileSync(prd, renumbered);
    generateIn(tmp);
    const rendered = fs.readFileSync(path.join(tmp, ".what-rendered", "_prd", "checkout-v1", "prd.md"), "utf8");
    for (const h of ["## Features", "## MVP Scope", "## Success Metrics"]) {
      assert.ok(rendered.includes(h), `${h} is missing from the rendered PRD — the renderer keyed on a section number:\n${rendered}`);
    }
    assert.ok(rendered.indexOf("### 4.1 Guest Checkout") < rendered.indexOf("#### FR-1 — ")
      && rendered.indexOf("#### FR-1 — ") < rendered.indexOf("### Capabilities"),
      "FR-1 fell into the fallback list instead of landing under its feature");
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

// Older registries carry `text:` where newer ones carry `title:`. Both are the short label; `statement:`
// is the sentence. Ranking the sentence above `text` made a migrated row render its paragraph as the
// heading — and an upgrade run then copied `text` into `title` on 23 rows to get a readable page.
test("a row labelled with `text:` renders that label as its heading, and its `statement:` below — no copy into `title:` needed", (t) => {
  if (requireUv(t)) return;
  const tmp = briefPrdCorpus();
  try {
    const reg = path.join(tmp, ".control", "registry", "requirements-checkout-v1.yaml");
    const before = fs.readFileSync(reg, "utf8");
    const after = before.replace(
      '    title: "A visitor can place an order without creating an account"',
      '    text: "A visitor can place an order without creating an account"\n'
      + '    statement: "A visitor who has no account, and wants none, can still place an order and reopen it later."');
    assert.notEqual(after, before, "the fixture FR-1 row did not carry the title this test relabels");
    fs.writeFileSync(reg, after);
    generateIn(tmp);
    const rendered = fs.readFileSync(path.join(tmp, ".what-rendered", "_prd", "checkout-v1", "prd.md"), "utf8");
    assert.match(rendered, /^#### FR-1 — A visitor can place an order without creating an account$/m,
      `the heading is not the row's label — \`statement\` outranked \`text\`:\n${rendered}`);
    assert.match(rendered, /A visitor who has no account, and wants none, can still place an order/,
      "the statement must still render, below the heading");
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

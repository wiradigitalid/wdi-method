// The fixture corpus is what lets a method change be PROVEN in this package.
//
// Before it existed, `validate.py` could not run here at all — there is no .control/, no .what/, no
// .how/ — so the only way to test a validator was to edit a product repo and promote. That is why
// CONTRIBUTING.md used to send you to a product repo first. This file removes that reason.
//
// The fixture is small but COMPLETE on purpose: a validator that skips proves nothing, so it carries
// one Product Component, two FR, two UC, one applied decision, one built container and one that is
// not, a platform-owned entity, and a code map. Building it immediately surfaced two real defects in
// validate.py — the V21 heading was Indonesian while language-guide.md says a script-matched key is
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
  const nfr = path.join(tmp, ".control", "registry", "requirements.yaml");
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
    assert.match(out, /V5\s+NFR-1/,
      `V5 did not catch an NFR with no enforcer, so the green run above proves nothing:\n${out}`);
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
  // Found the first time bima ran as a consumer: V24 used rglob plus an after-the-fact filter, so it
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
// through a defect that made V24 unsatisfiable for every real consumer. A real install has the
// method tree sitting inside it, and V24 was walking it: the guides cite `.control/...` and
// `.what/...` to teach where a thing GOES, and V24 read every one as this product's claim to
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
      assert.doesNotMatch(out, new RegExp(`V24.*${cite.replace(".", "\\.")}`),
        `V24 still fails on ${cite}, which no product is able to fix:\n${out}`);
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
    assert.match(out, /V24\s+\.control\/structure-codebase\.md.*does-not-exist\.md/,
      `V24 stopped catching a dangling cite in a live product file:\n${out}`);
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

test("V18 fails when a ticket's status is copied into specs.yaml — the one thing it exists for", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) =>
    editSpecs(dir, "      - id: SPEC-1-01", "      - id: SPEC-1-01\n        status: done"));
  assert.match(out, /V18\s+SPEC-1-01.*status.*specs\.yaml/,
    `a status in the registry beside a status in the ticket file is two homes for one fact:\n${out}`);
});

test("V18 fails when the ticket file is missing, and when it states no status at all", (t) => {
  if (requireUv(t)) return;
  // The file is found by the NUMBER at the tail of the id: SPEC-1-02 -> issues/02-*.md. If that
  // derivation ever breaks, every ticket reports as missing and this is what says so.
  const gone = afterMutation((dir) =>
    fs.rmSync(path.join(dir, "_bmad-output", "specs", "spec-1-checkout", "issues",
                        "02-reopen-an-order.md")));
  assert.match(gone, /V18\s+SPEC-1-02.*no ticket file/,
    `V18 did not notice a ticket with no file:\n${gone}`);

  // `**Status:**` is a BODY line, not frontmatter — a ticket file is a tracker payload, and
  // trackers do not read YAML. Reading only frontmatter would make every engine-written ticket
  // report as statusless.
  const silent = afterMutation((dir) => {
    const f = path.join(dir, "_bmad-output", "specs", "spec-1-checkout", "issues",
                        "01-place-an-order.md");
    fs.writeFileSync(f, fs.readFileSync(f, "utf8").replace(/^\*\*Status:\*\*.*\r?\n/m, ""));
  });
  assert.match(silent, /V18\s+SPEC-1-01.*states no status/,
    `V18 accepted a ticket file that states no status anywhere:\n${silent}`);
});

test("V7 fails on a blocked_by cycle — a frontier that is empty from the first tick", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) => editSpecs(dir, "        blocked_by: []", "        blocked_by: [SPEC-1-02]"));
  assert.match(out, /V7\s+SPEC-1-0[12].*blocked_by.*cycle/,
    `two tickets blocking each other were accepted; no work can ever start:\n${out}`);
});

test("V11 fails when two tickets share a `touches` with no blocking edge between them", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) => editSpecs(dir, "        blocked_by: [SPEC-1-01]", "        blocked_by: []"));
  assert.match(out, /V11\s+SPEC-1-01 \+ SPEC-1-02.*money/,
    `V11 reads the ticket-level edge as \`blocked_by\` now, not \`depends_on\`:\n${out}`);
});

test("V22 fails when a spec touches a component whose G4 has not passed", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) => {
    const f = path.join(dir, ".control", "registry", "components.yaml");
    fs.writeFileSync(f, fs.readFileSync(f, "utf8").replace(/g4_passed: .*/, "g4_passed: false"));
  });
  assert.match(out, /V22\s+SPEC-1 \/ checkout.*g4_passed/,
    `work was allowed to start on a component that has not been through its gate:\n${out}`);
});

test("V3 fails when a UC of an already-touched component is scheduled to no ticket", (t) => {
  if (requireUv(t)) return;
  const out = afterMutation((dir) => editSpecs(dir, "        satisfies: [UC-2]", "        satisfies: []"));
  assert.match(out, /V3\s+UC-2.*not scheduled to any ticket/,
    `a promise was left behind by a spec that had already opened its component:\n${out}`);
});

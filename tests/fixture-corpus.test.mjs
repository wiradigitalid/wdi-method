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

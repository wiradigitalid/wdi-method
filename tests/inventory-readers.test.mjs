// The inventory engine is generic; reading a stack is not. This is the seam that separates them.
//
// Before the split, inventory.py itself parsed SQL migrations, a Gin router, and react-router — so
// the method worked for exactly one stack while claiming to be a generic workflow. The readers now
// live in `.constitution/project/inventory-readers.py`, the room `update` never overwrites and
// `promote` never publishes, and the engine loads them at run time.
//
// Two things have to hold, and neither is obvious from reading the code:
//   1. no reader at all is REPORTED, never guessed around — that is the whole reason the script
//      exists rather than an agent reading the codebase
//   2. a product's own reader is actually used, and the injection works — a reader neither imports
//      Row/Derived/decisions nor redeclares them, which is exactly the kind of arrangement that
//      breaks silently
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..");
const FIXTURE = path.join(ROOT, "tests", "fixture");
const ENGINE = path.join(ROOT, "kit", ".constitution", "method", "scripts", "inventory.py");
const PY_ENV = { ...process.env, PYTHONDONTWRITEBYTECODE: "1" };

const HAVE_UV = spawnSync("uv", ["--version"], { stdio: "ignore" }).status === 0;
function requireUv(t) {
  if (HAVE_UV) return false;
  t.skip("uv is not installed — see the fixture-corpus suite for why that is loud");
  return true;
}

function runIn(cwd) {
  try {
    return { out: execFileSync("uv", ["run", ENGINE, "--root", "."],
                               { cwd, encoding: "utf8", env: PY_ENV,
                                 stdio: ["ignore", "pipe", "pipe"] }), code: 0 };
  } catch (e) {
    return { out: `${e.stdout || ""}${e.stderr || ""}`, code: e.status };
  }
}

function fixtureCopy() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-readers-"));
  fs.cpSync(FIXTURE, tmp, { recursive: true });
  return tmp;
}

test("a product with no reader is TOLD so — the engine never guesses at a stack", (t) => {
  if (requireUv(t)) return;
  const tmp = fixtureCopy();
  try {
    const { out, code } = runIn(tmp);
    assert.doesNotMatch(out, /Traceback/, `the engine crashed instead of reporting:\n${out}`);
    assert.match(out, /inventory-readers\.py/,
      `the message must name the file to write, or it is not actionable:\n${out}`);
    assert.equal(code, 2, "no reader is a refusal to derive, not a clean run and not a finding");
    assert.doesNotMatch(out, /rows read from code/,
      `something was derived without a reader, which means it was invented:\n${out}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

// Deliberately NOT the seeded reader: this one is four lines of a stack that does not exist, which
// is the point — if it works, the engine has no opinion about the language its product is written
// in. It also uses Row and Derived without importing them, which is the injection under test.
const TOY_READER = [
  '"""A toy reader for one imaginary stack."""',
  "",
  "def _one(kind, key, cells):",
  "    return Derived(rows=[Row(key=key, cells=cells, source=f'toy/{kind}')], unread=[])",
  "",
  "def derive_db(root):",
  "    return _one('db', 'widgets', ['1', 'widgets', 'checkout', 'toy rows', 'id', 'live'])",
  "",
  "def derive_api(root):",
  "    return Derived()",
  "",
  "def derive_screen(root):",
  "    return Derived()",
  "",
].join("\n");

test("the SEEDED skeleton is refused too — silence would read as a finished reader", (t) => {
  if (requireUv(t)) return;
  // The dangerous state is not the missing file, which is obvious. It is the seeded skeleton: it
  // loads, it defines all three functions, and it returns nothing — indistinguishable in the output
  // from a product that genuinely stores no tables and serves no endpoints. Only one of those is
  // true, so the skeleton declares itself and the engine refuses on the declaration.
  const tmp = fixtureCopy();
  try {
    const room = path.join(tmp, ".constitution", "project");
    fs.mkdirSync(room, { recursive: true });
    fs.copyFileSync(path.join(ROOT, "kit", ".constitution", "project", "inventory-readers.py"),
                    path.join(room, "inventory-readers.py"));
    const { out, code } = runIn(tmp);
    assert.equal(code, 2, "the seeded skeleton ran as if it were a written reader");
    assert.match(out, /skeleton/i, `the message does not say WHY nothing was derived:\n${out}`);
    assert.match(out, /wdi-init/,
      `the message does not name the skill that writes it, so it is not actionable:\n${out}`);
    assert.doesNotMatch(out, /rows read from code/,
      `the skeleton produced a row count, which is the lie this flag exists to prevent:\n${out}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("the seeded skeleton is valid Python defining all three readers", () => {
  // `wdi-init` intent `readers` fills this file in; it MUST start from something that parses and
  // already has the right shape, or the skill's first act is repairing the package's seed.
  const seed = fs.readFileSync(
    path.join(ROOT, "kit", ".constitution", "project", "inventory-readers.py"), "utf8");
  for (const fn of ["derive_db", "derive_api", "derive_screen"]) {
    assert.match(seed, new RegExp(`^def ${fn}\\(`, "m"), `the seed defines no ${fn}`);
  }
  assert.match(seed, /^SKELETON\s*=\s*True\b/m,
    "the seed does not declare itself a skeleton, so the engine would run it as a real reader");
  assert.match(seed, /wdi-init/,
    "the seed does not say what writes it — a reader who opens it is left to invent the patterns");
});

test("a product's OWN reader is loaded and used, with Row and Derived injected", (t) => {
  if (requireUv(t)) return;
  const tmp = fixtureCopy();
  try {
    const room = path.join(tmp, ".constitution", "project");
    fs.mkdirSync(room, { recursive: true });
    fs.writeFileSync(path.join(room, "inventory-readers.py"), TOY_READER);
    const { out } = runIn(tmp);
    assert.doesNotMatch(out, /Traceback|NameError/,
      `the injection failed — a reader had to import what the engine promised to supply:\n${out}`);
    assert.match(out, /1 rows read from code/,
      `the product's reader was not used:\n${out}`);
    assert.match(out, /present in code but not recorded in the plan: widgets/,
      `the row was read but never compared against the plan, so the engine half is not running:\n${out}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("a reader missing a kind is refused by name, not by a stack trace", (t) => {
  if (requireUv(t)) return;
  const tmp = fixtureCopy();
  try {
    const room = path.join(tmp, ".constitution", "project");
    fs.mkdirSync(room, { recursive: true });
    // derive_screen deliberately absent. Returning an empty Derived is a real answer; not defining
    // the function at all is an unfinished file, and the two MUST NOT read the same.
    fs.writeFileSync(path.join(room, "inventory-readers.py"),
                     TOY_READER.replace("def derive_screen(root):\n    return Derived()\n", ""));
    const { out } = runIn(tmp);
    assert.match(out, /derive_screen/,
      `the missing function was not named, so nobody can act on the message:\n${out}`);
    assert.doesNotMatch(out, /Traceback/, `refused with a stack trace instead of a sentence:\n${out}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

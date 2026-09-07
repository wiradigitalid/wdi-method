// The engines are installed IN the repo now, and three of them arrive with
// `disable-model-invocation: true` — the author's flag, and a deliberate one: `to-spec` and
// `to-tickets` publish to a tracker, and `implement` writes code. Nothing in Claude Code lifts that
// flag from outside the file: the gate reads the frontmatter and consults no setting, and
// `skillOverrides` only ever tightens (`on` → `name-only` → `user-invocable-only` → `off`). Owning
// the file is the only route, which is why the local install is mandatory rather than preferred.
//
// So the installer strips the flag from the repo's own copies and writes one guard line in its
// place. Two failures are what these tests exist for: the strip silently not happening (G5 is then
// human-only again, and `wdi-autopilot` cannot run a single iteration unattended), and the flag
// coming BACK — `npx skills update` restores the author's file byte for byte, and nothing would say
// so until a run stalled.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..");
const strip = (s) => s.replace(/\x1b\[[0-9;]*m/g, "");
const FLAGGED = ["to-spec", "to-tickets", "implement"];
const UNFLAGGED = ["tdd", "code-review", "domain-modeling"];

const HAVE_UV = spawnSync("uv", ["--version"], { stdio: "ignore" }).status === 0;
const PY_ENV = { ...process.env, PYTHONDONTWRITEBYTECODE: "1" };

function tmp(name) {
  return fs.mkdtempSync(path.join(os.tmpdir(), `wdi-${name}-`));
}

/** What `npx skills@latest add mattpocock/skills` leaves in a repo: the author's files, verbatim. */
function seedEngines(target, { dir = ".claude" } = {}) {
  for (const name of [...FLAGGED, ...UNFLAGGED]) {
    const d = path.join(target, dir, "skills", name);
    fs.mkdirSync(d, { recursive: true });
    const flag = FLAGGED.includes(name) ? "disable-model-invocation: true\n" : "";
    fs.writeFileSync(path.join(d, "SKILL.md"),
      `---\nname: ${name}\ndescription: "${name}, as the author ships it."\n${flag}---\n\n`
      + `# ${name}\n\nThe author's body, which MUST survive untouched.\n`);
  }
  fs.writeFileSync(path.join(target, "skills-lock.json"),
    JSON.stringify({ version: 1, skills: {} }, null, 2) + "\n");
}

function install(target, extra = []) {
  const cfg = tmp("cfg");
  try {
    return strip(execFileSync(process.execPath,
      [path.join(ROOT, "bin", "wdi-method.js"), "install", target, "--yes", "--skip-bmad-check",
       "--agents", "claude", "--product", "Shopfront", ...extra],
      { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"],
        env: { ...process.env, CLAUDE_CONFIG_DIR: cfg } }));
  } finally {
    fs.rmSync(cfg, { recursive: true, force: true });
  }
}

const skillFile = (target, name, dir = ".claude") =>
  path.join(target, dir, "skills", name, "SKILL.md");

/** The frontmatter only. The harness reads the key there and nowhere else, and asserting against
 * the whole file would pass or fail on prose — the first version of this test did exactly that,
 * and what tripped it was the guard line mentioning the key it had just removed. */
const frontmatter = (text) => (text.match(/^---\r?\n([\s\S]*?)\r?\n---/) || ["", ""])[1];
const locked = (text) => /^disable-model-invocation\s*:\s*true/m.test(frontmatter(text));

test("install STRIPS disable-model-invocation from the repo's own engine copies, and leaves the body alone", () => {
  const target = tmp("inv");
  try {
    seedEngines(target);
    const out = install(target);
    for (const name of FLAGGED) {
      const text = fs.readFileSync(skillFile(target, name), "utf8");
      assert.ok(!locked(text),
        `${name} still carries the flag, so no skill can invoke it and G5 is human-only again:\n${out}`);
      assert.match(text, /The author's body, which MUST survive untouched\./,
        `${name} lost the author's body — the patch is one frontmatter line, never a rewrite`);
      assert.match(text, /wdi-build|wdi-autopilot/,
        `${name} carries no guard line. The flag was the only thing stopping a stray session from `
        + `publishing tickets, and removing it without saying who may drive the engine trades a hard `
        + `gate for nothing at all`);
    }
    for (const name of UNFLAGGED) {
      assert.ok(!locked(fs.readFileSync(skillFile(target, name), "utf8")),
        `${name} never carried the flag and MUST NOT have gained one`);
    }
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("the strip is idempotent — a second install neither re-patches nor stacks a second guard line", () => {
  const target = tmp("inv-twice");
  try {
    seedEngines(target);
    install(target);
    const once = fs.readFileSync(skillFile(target, "to-spec"), "utf8");
    install(target);
    const twice = fs.readFileSync(skillFile(target, "to-spec"), "utf8");
    assert.equal(twice, once, "a second run changed the file again — the patch must be a no-op once applied");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("engines symlinked across platform folders are patched ONCE, at the file they point to", () => {
  const target = tmp("inv-link");
  try {
    seedEngines(target);
    // `npx skills add` offers "symlink — single source of truth" when several agents are selected.
    // Patching per directory would then write the same file repeatedly, and on a link into
    // node_modules it would edit a dependency. The canonical file is the only thing to patch.
    const link = path.join(target, ".agents", "skills");
    fs.mkdirSync(path.dirname(link), { recursive: true });
    try {
      fs.symlinkSync(path.join(target, ".claude", "skills"), link, "junction");
    } catch {
      return; // no symlink privilege on this machine; the assertion below would test nothing
    }
    install(target);
    const text = fs.readFileSync(skillFile(target, "to-spec"), "utf8");
    assert.ok(!locked(text), "the canonical copy was not patched");
    const guards = text.match(/wdi-build/g) || [];
    assert.equal(guards.length, 1,
      `the guard line was written ${guards.length} times — the symlinked folder was walked as if it `
      + `were a second copy`);
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("the register records the engines, so a later run can tell a patched copy from a restored one", () => {
  const target = tmp("inv-stamp");
  try {
    seedEngines(target);
    install(target);
    const stamp = fs.readFileSync(path.join(target, ".control", "wdi-method.yaml"), "utf8");
    assert.match(stamp, /engines:/, "the stamp carries no engines block");
    assert.match(stamp, /source: local/, "the register must say the engines are the repo's own copies");
    assert.match(stamp, /model_invocation: enabled/,
      "the register must record that the flag was stripped — that is the fact the validator checks");
    for (const name of FLAGGED) {
      assert.match(stamp, new RegExp(name), `the register does not name ${name}`);
    }
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("`engines --fix` replaces upstream's tracker answer and keeps the old text beside it", () => {
  const target = tmp("inv-fix");
  try {
    seedEngines(target);
    install(target);
    // What `/setup-matt-pocock-skills` writes, and what two of four live repos still carried: every
    // effort in `.scratch/` with no registry behind it, and `specs.yaml` never mentioned. The
    // engines then publish wherever they guess, which is the whole complaint this repair answers.
    const tracker = path.join(target, "docs", "agents", "issue-tracker.md");
    const upstream = "# Issue tracker: Local Markdown\n\nIssues live in `.scratch/`.\n";
    fs.writeFileSync(tracker, upstream);

    const out = strip(execFileSync(process.execPath,
      [path.join(ROOT, "bin", "wdi-method.js"), "engines", target, "--fix"],
      { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }));

    const now = fs.readFileSync(tracker, "utf8");
    assert.match(now, /seeded by `wdi-method`/,
      `the repair left upstream's answer in place:\n${out}`);
    assert.match(now, /\.scratch\/<spec-id>-<slug>\//,
      "the repaired file must name the predefined path, or the engines are still guessing");
    assert.equal(fs.readFileSync(`${tracker}.bak`, "utf8"), upstream,
      "the previous text was deleted rather than kept. Somebody may have meant it, and a repair that "
      + "cannot be read afterwards is indistinguishable from a mistake");

    // And the installer itself MUST still keep its hands off: that rule protects every other
    // product-owned file, and `engines --fix` exists precisely so this one is repaired knowingly.
    fs.writeFileSync(tracker, upstream);
    install(target);
    assert.equal(fs.readFileSync(tracker, "utf8"), upstream,
      "`update` overwrote a product-owned file. The repair belongs to the skill somebody runs on "
      + "purpose, not to every install");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

// A migration path nobody is told about is not a migration path. `wdi-upgrade` gained the two items
// that move a repo onto the predefined paths, and `update` said nothing about either — so the four
// repos this was written for would run `update`, see a clean summary, and carry on writing tickets
// wherever the engine guessed. `pendingUpgrades()` is what puts the `upgrade` line on the summary and
// `wdi-upgrade` in the next steps, so the probes belong there.
test("update REPORTS a stale tracker config and a spec folder outside `.scratch/` as pending", () => {
  const target = tmp("pend");
  try {
    seedEngines(target);
    install(target);

    // Upstream's answer, as `/setup-matt-pocock-skills` writes it: no `specs.yaml`, no predefined
    // path. Two of four live repos still carried this, and it is why their tickets scattered.
    fs.writeFileSync(path.join(target, "docs", "agents", "issue-tracker.md"),
      "# Issue tracker: Local Markdown\n\nIssues live in `.scratch/`.\n");
    // And a spec folder where every repo used to put it.
    fs.writeFileSync(path.join(target, ".control", "registry", "specs.yaml"),
      "specs:\n  - id: SPEC-1\n    release: v1\n    status: open\n"
      + "    spec_folder: _bmad-output/specs/w1-settings/\n    tickets: []\n");

    const out = strip(execFileSync(process.execPath,
      [path.join(ROOT, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check"],
      { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"],
        env: { ...process.env, CLAUDE_CONFIG_DIR: tmp("cfg2") } }));

    assert.match(out, /issue-tracker\.md/,
      `update said nothing about a tracker config that sends the engines to the wrong place:\n${out}`);
    assert.match(out, /spec_folder/,
      `update said nothing about spec folders still outside \`.scratch/\`:\n${out}`);
    assert.match(out, /wdi-upgrade/,
      `the summary named neither, so the next steps never named the skill that fixes them:\n${out}`);
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("a CLOSED spec's folder is left where it is — the convention binds work, not finished history", () => {
  const target = tmp("pend-closed");
  try {
    seedEngines(target);
    install(target);
    // The repo this was measured on carries ten closed specs and not one open. Reporting all ten as
    // pending would ask somebody to move ten folders of finished work, repoint every cite into them,
    // and gain nothing: `spec_folder` still resolves, and 0.6.7 already made a closed spec's missing
    // ticket file legitimate. The same exemption `ticket-status-one-home` grants, for the same reason.
    fs.writeFileSync(path.join(target, ".control", "registry", "specs.yaml"),
      "specs:\n"
      + "  - id: SPEC-1\n    release: v1\n    status: closed\n"
      + "    spec_folder: _bmad-output/specs/spec-1-checkout/\n    tickets: []\n"
      + "  - id: SPEC-2\n    release: v1\n    status: open\n"
      + "    spec_folder: _bmad-output/specs/spec-2-refunds/\n    tickets: []\n");

    const out = strip(execFileSync(process.execPath,
      [path.join(ROOT, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check"],
      { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"],
        env: { ...process.env, CLAUDE_CONFIG_DIR: tmp("cfg3") } }));

    assert.match(out, /spec_folder/, `the OPEN spec was not reported:\n${out}`);
    assert.match(out, /SPEC-2/,
      `the report must NAME the spec that needs moving — "a spec_folder outside .scratch/" over ten `
      + `closed rows is how a summary gets skipped:\n${out}`);
    assert.doesNotMatch(out, /SPEC-1/,
      `a closed spec was reported as pending. Its folder is a record; moving it churns finished work `
      + `and the cites into it:\n${out}`);
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("engines-invocable goes RED when the flag comes back — what `npx skills update` does", (t) => {
  if (!HAVE_UV) {
    t.skip("uv is not installed, so validate.py cannot run here");
    return;
  }
  const target = tmp("inv-red");
  try {
    seedEngines(target);
    install(target);
    const validate = path.join(target, ".constitution", "method", "scripts", "validate.py");
    const run = () => {
      try {
        return execFileSync("uv", ["run", validate, "--root", ".", "--check"],
          { cwd: target, encoding: "utf8", env: PY_ENV, stdio: ["ignore", "pipe", "pipe"] });
      } catch (e) {
        return `${e.stdout || ""}${e.stderr || ""}`;
      }
    };

    const before = run();
    assert.doesNotMatch(before, /engines-invocable/,
      `the check fired on a correctly patched repo — a validator that is red when nothing is wrong `
      + `is a validator that gets ignored:\n${before}`);

    // The author's file, restored. This is not hypothetical: `npx skills update` writes it back.
    const f = skillFile(target, "to-tickets");
    fs.writeFileSync(f, fs.readFileSync(f, "utf8")
      .replace(/^---\n/, "---\ndisable-model-invocation: true\n"));
    const after = run();
    assert.match(after, /engines-invocable\s+to-tickets/,
      `the flag came back and nothing said so. The next unattended run would stall at Phase 2 with no `
      + `explanation:\n${after}`);
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

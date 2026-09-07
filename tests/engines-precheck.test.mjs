// G5 runs on six engines this package does not ship. They MUST be installed into the repo itself
// (`npx skills@latest add mattpocock/skills`), and a user-level plugin is no longer an answer: the
// method strips `disable-model-invocation` from its own copies so `wdi-build` can invoke them, and a
// plugin's files are not the repo's to edit. For three releases the installer checked BMad and said
// nothing about the engines, so the first time anyone learned they were missing was inside wdi-build,
// with a spec already open.
//
// The check BLOCKS, and `--skip-engines-check` is the escape. It used to warn and let the install
// through, on the reasoning that G1–G4 run without the engines and a first install has no G5 yet. Both
// halves are still true; the reasoning stopped being enough. `wdi-autopilot` needs all three from its
// first iteration, and a warning inside a forty-line summary is read as often as it is skipped — so the
// failure it was meant to prevent, learning they are missing inside wdi-build with a spec already open,
// kept happening. The escape keeps the two real cases working: CI, and a repo that will never reach G5.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..");
const strip = (s) => s.replace(/\x1b\[[0-9;]*m/g, "");

function tmp(name) {
  return fs.mkdtempSync(path.join(os.tmpdir(), `wdi-${name}-`));
}

const ENGINES = ["to-spec", "to-tickets", "implement", "tdd", "code-review", "domain-modeling"];

/** What `npx skills add` leaves behind: the author's six files, in the repo. */
function seedEngines(target, only = ENGINES) {
  for (const name of only) {
    const dir = path.join(target, ".claude", "skills", name);
    fs.mkdirSync(dir, { recursive: true });
    const flag = ["to-spec", "to-tickets", "implement"].includes(name)
      ? "disable-model-invocation: true\n" : "";
    fs.writeFileSync(path.join(dir, "SKILL.md"), `---\nname: ${name}\n${flag}---\n\n# ${name}\n`);
  }
}

/** A user-level plugin registry that DOES carry the plugin. The gate must not care. */
function withPlugin(configDir) {
  fs.mkdirSync(path.join(configDir, "plugins"), { recursive: true });
  fs.writeFileSync(path.join(configDir, "plugins", "installed_plugins.json"), JSON.stringify({
    version: 2,
    plugins: { "mattpocock-skills@claude-plugins-official": [{ scope: "user", version: "1.2.3" }] },
  }));
  return configDir;
}

function install(target, configDir, extra = ["--skip-engines-check"]) {
  return strip(execFileSync(process.execPath,
    [path.join(ROOT, "bin", "wdi-method.js"), "install", target, "--yes", "--skip-bmad-check",
     "--agents", "claude", "--product", "Shopfront", ...extra],
    { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env, CLAUDE_CONFIG_DIR: configDir } }));
}

/** The same install with NO escape, returning whatever it printed whether it succeeded or died. */
function installUnescaped(target, configDir) {
  try {
    return { ok: true, out: install(target, configDir, []) };
  } catch (e) {
    return { ok: false, out: strip(`${e.stdout || ""}${e.stderr || ""}`) };
  }
}

test("install on a machine WITHOUT the ticket engines REFUSES, and says exactly how to get them", () => {
  const target = tmp("noeng");
  const cfg = tmp("cfg-empty");
  try {
    const { ok, out } = installUnescaped(target, cfg);
    assert.equal(ok, false, `the install went through without the engines:\n${out}`);
    assert.match(out, /npx skills@latest add mattpocock\/skills/,
      "the refusal must carry the exact install command — a reader should not have to look it up");
    assert.match(out, /to-spec/, "the refusal must name WHICH engines are missing, not just that some are");
    assert.match(out, /domain-modeling/,
      "domain-modeling is one of the six — `wdi-blueprint` invokes it at G3, and it used to be reached "
      + "by a plugin-namespaced name that now resolves to nothing");
    assert.match(out, /github\.com\/mattpocock\/skills/, "the refusal must name the source");
    assert.match(out, /setup-matt-pocock-skills/,
      "the refusal must name the setup step too — the engines alone are not enough, they need a tracker");
    assert.match(out, /--skip-engines-check/,
      "a refusal with no escape is a wall. CI and a repo that never reaches G5 are both real");
    assert.ok(!fs.existsSync(path.join(target, ".control", "wdi-method.yaml")),
      "the install refused but still wrote to the target — a refusal must leave nothing behind");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});

test("--skip-engines-check installs anyway, and the summary still names what is missing", () => {
  const target = tmp("noeng-esc");
  const cfg = tmp("cfg-empty-esc");
  try {
    const out = install(target, cfg);
    assert.ok(fs.existsSync(path.join(target, ".control", "wdi-method.yaml")),
      `the escape did not let the install through:\n${out}`);
    assert.match(out, /engines\s+NOT found: to-spec · to-tickets · implement/,
      `the escape silenced the summary too — it must still say what is missing:\n${out}`);
    assert.match(out, /G1–G4 run without them/, "the summary must say the install is still usable");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});
// The old gate accepted the user-level plugin, and that is exactly what made this suite pass here
// and fail in CI: the answer depended on whose laptop ran it. It also could not be repaired — the
// three flagged engines can only be unlocked in a file the repo owns. So the plugin is now a
// warning and nothing more, and this is the test that keeps it that way.
test("the user-level plugin does NOT satisfy the gate — the answer must not depend on whose machine ran it", () => {
  const target = tmp("eng-plugin");
  const cfg = withPlugin(tmp("cfg-plugin"));
  try {
    const { ok, out } = installUnescaped(target, cfg);
    assert.equal(ok, false,
      `the plugin was registered for this user and the install went through on that basis. On a `
      + `runner without it the same install refuses — which is how twenty-eight tests once died `
      + `after a tag was pushed:\n${out}`);
    assert.match(out, /npx skills@latest add/, "the refusal must point at the in-repo install");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});

test("all six engines in the repo satisfy the gate, and the plugin alongside them is called out", () => {
  const target = tmp("repoeng");
  const cfg = withPlugin(tmp("cfg-both"));
  try {
    seedEngines(target);
    const out = install(target, cfg, []);
    assert.match(out, /engines\s+to-spec/, `the repo's own copies were not seen:\n${out}`);
    assert.match(out, /found \(in this repo\)/, `the summary must say WHERE they were found:\n${out}`);
    // Upstream's own warning: "installing both leaves you with every skill twice." Survivable, but
    // `/to-spec` in the UI stops being one thing, so it is said rather than left to be discovered.
    assert.match(out, /plugin is ALSO installed/,
      `both copies are present and nothing said so:\n${out}`);
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});

test("five of six is still a refusal, and it names the one that is missing", () => {
  const target = tmp("repoeng-five");
  const cfg = tmp("cfg-five");
  try {
    seedEngines(target, ENGINES.filter((n) => n !== "code-review"));
    const { ok, out } = installUnescaped(target, cfg);
    assert.equal(ok, false, `a repo missing code-review installed anyway:\n${out}`);
    assert.match(out, /Missing: code-review/,
      `the refusal must name the missing engine and only it — "engines not installed" sends a reader `
      + `to reinstall five they already have:\n${out}`);
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});

// `/setup-matt-pocock-skills` writes docs/agents/. Two of its answers are wrong for a WDI repo, and BOTH
// real repos that ran it hand-corrected the SAME file afterwards — domain.md, which sends every
// engineering skill looking for a root CONTEXT.md and docs/adr/, the two things Article 3 says this method
// has no layer for and wdi-reconcile reports as findings. Seeding them is what stops the third repo paying
// for it. Seeded ONCE: after that the file is the product's, like everything else under a path it owns.

test("install SEEDS docs/agents/ pre-answered, so the engines are aligned before anyone runs the interview", () => {
  const target = tmp("agentdocs");
  const cfg = tmp("cfg-seed");
  try {
    install(target, cfg);
    const domain = path.join(target, "docs", "agents", "domain.md");
    const tracker = path.join(target, "docs", "agents", "issue-tracker.md");
    assert.ok(fs.existsSync(domain), "docs/agents/domain.md was not seeded");
    assert.ok(fs.existsSync(tracker), "docs/agents/issue-tracker.md was not seeded");

    const d = fs.readFileSync(domain, "utf8");
    assert.match(d, /does not use `CONTEXT\.md`/,
      "the seeded domain.md must say outright that a root CONTEXT.md is not used — saying nothing is how "
      + "the default gets restored by the next person who runs the setup skill");
    assert.match(d, /product-glossary\.md/,
      "it must name where the vocabulary actually lives, or 'do not use CONTEXT.md' leaves a hole");

    const t = fs.readFileSync(tracker, "utf8");
    assert.match(t, /\.scratch\/<spec-id>-<slug>\/issues\//,
      "the seeded issue-tracker.md must give the engines ONE predefined place for a spec's tickets");
    assert.match(t, /specs\.yaml/,
      "it must say the registry is what tells a spec from ad hoc work — one root means the path no "
      + "longer does");
    assert.match(t, /ticket-status-one-home/,
      "it must name the validator that reads ticket status, since that is the invariant a tracker swap breaks");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});

test("a docs/agents file the product already wrote is NEVER overwritten", () => {
  const target = tmp("agentdocs-own");
  const cfg = tmp("cfg-own");
  try {
    fs.mkdirSync(path.join(target, "docs", "agents"), { recursive: true });
    const mine = "# Our own tracker\n\nJira, and we mean it.\n";
    fs.writeFileSync(path.join(target, "docs", "agents", "issue-tracker.md"), mine);
    install(target, cfg);
    assert.equal(fs.readFileSync(path.join(target, "docs", "agents", "issue-tracker.md"), "utf8"), mine,
      "the installer overwrote a tracker config the product already chose — the same rule that protects "
      + "every other product-owned file protects this one");
    assert.ok(fs.existsSync(path.join(target, "docs", "agents", "domain.md")),
      "the file that WAS missing should still have been seeded — one existing file must not skip the rest");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});

test("a repo that ran the setup skill FIRST is warned that its domain.md contradicts Article 3", () => {
  const target = tmp("agentdocs-stale");
  const cfg = tmp("cfg-stale");
  try {
    fs.mkdirSync(path.join(target, "docs", "agents"), { recursive: true });
    // The setup skill's own default, near enough: it sends skills to a root CONTEXT.md and docs/adr/.
    fs.writeFileSync(path.join(target, "docs", "agents", "domain.md"),
      "# Domain Docs\n\n- **`CONTEXT.md`** at the repo root\n- **`docs/adr/`**: read ADRs\n");
    const out = install(target, cfg);
    assert.match(out, /domain\.md still points agents at a root CONTEXT\.md/,
      `the stale default was left in place with nothing said about it:\n${out}`);
    assert.match(out, /product-glossary\.md/,
      "the warning must say where the vocabulary actually lives, not only what is wrong");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});

test("a domain.md somebody already corrected is NOT warned about again", () => {
  const target = tmp("agentdocs-fixed");
  const cfg = tmp("cfg-fixed");
  try {
    fs.mkdirSync(path.join(target, "docs", "agents"), { recursive: true });
    // What both real repos wrote by hand. A warning that fires forever on a fixed file is noise.
    fs.writeFileSync(path.join(target, "docs", "agents", "domain.md"),
      "# Domain Docs\n\nThis repo does not use `CONTEXT.md` or `docs/adr/` — WDI Method owns those homes.\n");
    const out = install(target, cfg);
    assert.doesNotMatch(out, /domain\.md still points agents/,
      `a file that already carries the correction was warned about anyway:\n${out}`);
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});

// This suite went green locally and red in CI, and the gap was the developer's own machine: the
// mattpocock plugin is installed here, so the old `enginesPresent()` said yes for every test that ran
// an install without the escape. On a runner it said no, and twenty-eight tests died at once — after
// the tag was already pushed.
//
// The old fix was a rule about test files: every non-gate install passes `--skip-engines-check`. That
// rule is now redundant where a test seeds the engines itself, and the hazard it guarded is gone at
// the root: the gate no longer reads the plugin registry at all. This asserts the root, against the
// installer's own source, the same way project-room does — a rule about test files could only ever
// catch the tests somebody remembered to write.
test("the engines gate reads the REPO, and the plugin registry only to warn", () => {
  const src = fs.readFileSync(path.join(ROOT, "bin", "wdi-method.js"), "utf8");
  const gate = src.slice(src.indexOf("function enginesReport"), src.indexOf("function pluginEnginesRegistered"));
  assert.doesNotMatch(gate, /installed_plugins\.json/,
    "the gate consults the user-level plugin registry again. Whether an install succeeds then depends "
    + "on whose machine ran it, and the three flagged engines still cannot be unlocked — a plugin's "
    + "files are not the repo's to edit");
  assert.match(src, /function pluginEnginesRegistered/,
    "the plugin check itself MUST survive: two copies of every engine is worth one warning line");
  // Minus the declaration, which the same pattern matches.
  const uses = src.match(/(?<!function )pluginEnginesRegistered\(\)/g) || [];
  assert.equal(uses.length, 1,
    `pluginEnginesRegistered() is called ${uses.length} times. It belongs in the summary and nowhere `
    + `else — any second caller is a decision being made on it`);
});

// G5 runs on two engines this package does not ship: `to-spec` and `to-tickets` (the mattpocock-skills
// plugin, installed per user). For three releases the installer checked BMad and said nothing about them,
// so the first time anyone learned they were missing was inside wdi-build, with a spec already open.
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
    assert.match(out, /\/plugin install mattpocock-skills/,
      "the refusal must carry the exact install command — a reader should not have to look it up");
    assert.match(out, /npx skills@latest add mattpocock\/skills/,
      "the refusal must also carry the path for agents that are not Claude Code — the installer supports them");
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
    assert.match(out, /engines\s+to-spec · to-tickets · implement — NOT found/,
      `the escape silenced the summary too — it must still say what is missing:\n${out}`);
    assert.match(out, /G1–G4 run without them/, "the summary must say the install is still usable");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});
test("install on a machine WITH the plugin registered reports the engines as found", () => {
  const target = tmp("eng");
  const cfg = tmp("cfg-plugin");
  try {
    fs.mkdirSync(path.join(cfg, "plugins"), { recursive: true });
    fs.writeFileSync(path.join(cfg, "plugins", "installed_plugins.json"), JSON.stringify({
      version: 2,
      plugins: { "mattpocock-skills@claude-plugins-official": [{ scope: "user", version: "1.2.3" }] },
    }));
    const out = install(target, cfg);
    assert.match(out, /engines\s+to-spec · to-tickets · implement — found/,
      `the plugin is registered but the summary did not see it:\n${out}`);
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
    fs.rmSync(cfg, { recursive: true, force: true });
  }
});

test("engines copied into the repo itself (.claude/skills/to-tickets) also count", () => {
  const target = tmp("repoeng");
  const cfg = tmp("cfg-empty2");
  try {
    fs.mkdirSync(path.join(target, ".claude", "skills", "to-tickets"), { recursive: true });
    fs.writeFileSync(path.join(target, ".claude", "skills", "to-tickets", "SKILL.md"), "---\nname: to-tickets\n---\n");
    const out = install(target, cfg);
    assert.match(out, /engines\s+to-spec · to-tickets · implement — found/, out);
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
    assert.match(t, /\{spec_folder\}\/issues\//,
      "the seeded issue-tracker.md must point a spec's tickets at spec_folder, not at .scratch/");
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

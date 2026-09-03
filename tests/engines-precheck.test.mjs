// G5 runs on two engines this package does not ship: `to-spec` and `to-tickets` (the mattpocock-skills
// plugin, installed per user). For three releases the installer checked BMad and said nothing about them,
// so the first time anyone learned they were missing was inside wdi-build, with a spec already open.
//
// The check WARNS and never blocks: G1–G4 run without the engines, and a first install has no G5 yet.
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

function install(target, configDir) {
  return strip(execFileSync(process.execPath,
    [path.join(ROOT, "bin", "wdi-method.js"), "install", target, "--yes", "--skip-bmad-check",
     "--agents", "claude", "--product", "Shopfront"],
    { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env, CLAUDE_CONFIG_DIR: configDir } }));
}

test("install on a machine WITHOUT the ticket engines names them, names the gate that needs them, and does not block", () => {
  const target = tmp("noeng");
  const cfg = tmp("cfg-empty");
  try {
    const out = install(target, cfg);
    assert.match(out, /engines\s+to-spec · to-tickets · implement — NOT found/,
      `the summary did not warn about the missing engines:\n${out}`);
    assert.match(out, /\/plugin install mattpocock-skills/,
      "the warning must carry the exact install command — a reader should not have to look it up");
    assert.match(out, /npx skills@latest add mattpocock\/skills/,
      "the warning must also carry the path for agents that are not Claude Code — the installer supports them");
    assert.match(out, /github\.com\/mattpocock\/skills/, "the warning must name the source");
    assert.match(out, /G1–G4 run without them/, "the warning must say the install is still usable");
    assert.ok(fs.existsSync(path.join(target, ".control", "wdi-method.yaml")),
      "a missing engine blocked the install — it is needed at G5 only");
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

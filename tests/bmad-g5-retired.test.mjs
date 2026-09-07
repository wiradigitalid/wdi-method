// `bmad-skill-register.md` has said `bmad-spec` and `bmad-build` MUST NOT be used since 0.5.x, and
// repos kept using them anyway. Not because the rule was unclear — because the harness rewarded the
// other answer. `bmad-build` sits in the repo's own `.claude/skills/`, model-invocable, describing
// itself as implementing "any user intent, requirement, story, bug fix or change request"; the
// engines that replace it sat in a user-level plugin the model could not call at all. A sentence in
// a guide does not win that.
//
// So the ban is enforced twice, in the two places the harness actually reads: the wrapper's own
// frontmatter, and `permissions.deny`. Both are re-applied on every update, because BMad's installer
// rewrites its wrappers whenever it runs.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..");
const strip = (s) => s.replace(/\x1b\[[0-9;]*m/g, "");

/** The names, read from the installer itself. A second copy of this list in the test would be a
 * second home for the same fact — and the register/code drift test below exists to refuse exactly
 * that. */
const SRC = fs.readFileSync(path.join(ROOT, "bin", "wdi-method.js"), "utf8");
const RETIRED = JSON.parse(
  SRC.slice(SRC.indexOf("const BMAD_RETIRED_G5 = ["), SRC.indexOf("];", SRC.indexOf("const BMAD_RETIRED_G5 = [")) + 1)
    .replace("const BMAD_RETIRED_G5 = ", "")
    .replace(/,(\s*])/, "$1")
    .replace(/'/g, '"'),
);

function tmp(name) {
  return fs.mkdtempSync(path.join(os.tmpdir(), `wdi-${name}-`));
}

function install(target, extra = ["--skip-engines-check"]) {
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

/** BMad's own wrappers, near enough: a model-invocable skill with an inviting description. */
function seedBmadSkills(target, names = RETIRED) {
  for (const name of names) {
    const dir = path.join(target, ".claude", "skills", name);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, "SKILL.md"),
      `---\nname: ${name}\ndescription: 'Implements any user intent, requirement, story or change request.'\n---\n\n`
      + `# ${name}\n\nBMad's body.\n`);
  }
}

const fm = (text) => (text.match(/^---\r?\n([\s\S]*?)\r?\n---/) || ["", ""])[1];
const locked = (text) => /^disable-model-invocation\s*:\s*true/m.test(fm(text));
const read = (target, name) =>
  fs.readFileSync(path.join(target, ".claude", "skills", name, "SKILL.md"), "utf8");

test("install locks every retired BMad G5 wrapper out of model invocation, and leaves the body alone", () => {
  const target = tmp("bmad-lock");
  try {
    seedBmadSkills(target);
    const out = install(target);
    for (const name of RETIRED) {
      const text = read(target, name);
      assert.ok(locked(text),
        `${name} can still be model-invoked. It is the most inviting description in the repo's skill `
        + `index, and the engine that replaces it is narrower by design — the model will keep `
        + `choosing this one:\n${out}`);
      assert.match(text, /BMad's body\./, `${name} lost BMad's body — the patch is one frontmatter line`);
    }
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("a person can still run one by name — the lock refuses the Skill tool, not the human", () => {
  const target = tmp("bmad-human");
  try {
    seedBmadSkills(target, ["bmad-build"]);
    install(target);
    const text = read(target, "bmad-build");
    // Claude Code's gate is `disableModelInvocation && !userTypedThisTurn`. Keeping `user-invocable`
    // untouched is what leaves `/bmad-build` working for somebody who means it — a retired default
    // is not the same as a forbidden action, and taking the human route away would be a third rule
    // nobody agreed to.
    assert.doesNotMatch(fm(text), /^user-invocable\s*:\s*false/m,
      "the patch also hid the slash command. The method retires a default; it does not confiscate a "
      + "tool from the owner");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("deny rules are MERGED into .claude/settings.json, never replacing what the product wrote", () => {
  const target = tmp("bmad-deny");
  try {
    fs.mkdirSync(path.join(target, ".claude"), { recursive: true });
    const mine = {
      permissions: { allow: ["Bash(npm test)"], deny: ["Bash(rm -rf /)"] },
      env: { EDITOR: "vim" },
    };
    fs.writeFileSync(path.join(target, ".claude", "settings.json"), JSON.stringify(mine, null, 2));
    install(target);
    const after = JSON.parse(fs.readFileSync(path.join(target, ".claude", "settings.json"), "utf8"));
    assert.deepEqual(after.permissions.allow, ["Bash(npm test)"],
      "an allow list the product wrote was touched — permissions are the product's, and this adds to "
      + "them rather than deciding them");
    assert.deepEqual(after.env, { EDITOR: "vim" }, "an unrelated settings key was rewritten");
    assert.ok(after.permissions.deny.includes("Bash(rm -rf /)"),
      "the product's own deny rule was dropped while adding ours");
    for (const name of RETIRED) {
      assert.ok(after.permissions.deny.includes(`Skill(${name})`),
        `Skill(${name}) is not denied. The frontmatter lock holds until BMad's installer rewrites its `
        + `wrappers, which it does whenever it runs — this is the layer that survives that`);
    }
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("a settings.json nobody can parse is REPORTED, not repaired", () => {
  const target = tmp("bmad-badjson");
  try {
    fs.mkdirSync(path.join(target, ".claude"), { recursive: true });
    const broken = "{ \"permissions\": { \"deny\": [ }\n";
    fs.writeFileSync(path.join(target, ".claude", "settings.json"), broken);
    const out = install(target);
    assert.match(out, /settings\.json is not valid JSON/,
      `the installer said nothing about a settings file it could not read:\n${out}`);
    assert.equal(fs.readFileSync(path.join(target, ".claude", "settings.json"), "utf8"), broken,
      "the installer rewrote a file it could not parse — that is how a repo loses its allowlist");
  } finally {
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("the register and the code name the SAME retired skills — one fact, one home", () => {
  const doc = fs.readFileSync(
    path.join(ROOT, "kit", ".constitution", "method", "document", "bmad-skill-register.md"), "utf8");
  // The ENFORCED sub-section only. The one after it lists shims and aliases that nothing locks,
  // and reading those as claimed retirements made this test fail on a register that was correct.
  const from = doc.indexOf("### Retired at G5");
  const next = doc.indexOf("\n### ", from + 1);
  const table = doc.slice(from, next === -1 ? undefined : next);
  assert.ok(table, "the register no longer has a `What is NOT USED` section for this to check against");

  const missing = RETIRED.filter((name) => !table.includes(`\`${name}\``));
  assert.deepEqual(missing, [],
    "the installer locks these out of model invocation and the register does not name them. A reader "
    + "who finds a skill mysteriously uninvocable has nowhere to learn why:\n  " + missing.join("\n  "));

  // And the other direction: a name in the register's retired table that the code does not enforce
  // is a rule that exists only as prose — which is the exact failure this whole change is about.
  const claimed = [...table.matchAll(/`(bmad-[a-z0-9-]+)`/g)].map((m) => m[1]);
  const unenforced = [...new Set(claimed)].filter((name) => !RETIRED.includes(name));
  assert.deepEqual(unenforced, [],
    "the register retires these and nothing stops a model reaching for them:\n  " + unenforced.join("\n  "));
});

test("the two skills with no replacement here are NOT retired — the criterion, not a mood", () => {
  // `bmad-qa-generate-e2e-tests` generates tests for features that already exist; `tdd` is
  // test-first for work being built. `bmad-checkpoint-preview` is a human reading aid, the same
  // class as `bmad-advanced-elicitation`, which the register deliberately keeps. Banning a
  // capability with nothing in its place is how a method gets worked around instead of followed.
  for (const name of ["bmad-qa-generate-e2e-tests", "bmad-checkpoint-preview", "bmad-review",
                      "bmad-correct-course", "bmad-prd", "bmad-architecture", "bmad-help"]) {
    assert.ok(!RETIRED.includes(name),
      `${name} is on the retired list. Every name there MUST have a named replacement in this method, `
      + `and this one does not — or, worse, it is a wrapper G1–G4 still routes through`);
  }
});

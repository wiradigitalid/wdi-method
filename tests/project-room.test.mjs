// The custom room `.constitution/project/` has three properties, and the most expensive one to
// lose is the second: a client's own rules reaching the public repo.
//
// This test MUST NOT run promote against the real kit. Node runs test files in parallel, and
// promote deletes the kit before copying it back — the first version of this test did exactly
// that and made another test file fail to read the kit mid-run. So the package is copied to a
// temporary folder first, and every mutation happens on that copy.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..");

function tmp(name) {
  return fs.mkdtempSync(path.join(os.tmpdir(), `wdi-${name}-`));
}

/** A copy of the package that may be mutated freely. */
function isolatedPackage() {
  const dir = tmp("pkg");
  for (const part of ["bin", "lib", "kit", "kit-overlay", "scaffold"]) {
    const src = path.join(ROOT, part);
    if (fs.existsSync(src)) fs.cpSync(src, path.join(dir, part), { recursive: true });
  }
  fs.copyFileSync(path.join(ROOT, "package.json"), path.join(dir, "package.json"));
  // @clack/prompts MUST resolve from this copy. A junction, not a symlink: on Windows a
  // directory symlink needs admin rights and a junction does not.
  const deps = path.join(ROOT, "node_modules");
  if (fs.existsSync(deps)) {
    try {
      fs.symlinkSync(deps, path.join(dir, "node_modules"), "junction");
    } catch {
      fs.cpSync(deps, path.join(dir, "node_modules"), { recursive: true });
    }
  }
  return dir;
}

/** A mock product repo: one generic file, and a product's own rule in its room. */
function fakeLiveRepo(pkg) {
  const live = tmp("live");
  fs.mkdirSync(path.join(live, ".constitution", "project"), { recursive: true });
  fs.writeFileSync(path.join(live, ".constitution", "generic-guide.md"), "# generic\n");
  fs.writeFileSync(path.join(live, ".constitution", "project", "secret-client.md"),
    "---\nscope: project\npurpose: \"a rule that MUST NOT be published\"\n---\nSecret Client Name\n");
  fs.writeFileSync(path.join(live, ".constitution", "project", "README.md"), "EDITED IN THE PRODUCT\n");
  for (const name of fs.readdirSync(path.join(pkg, "kit", "skills"))) {
    const dst = path.join(live, ".claude", "skills", name);
    fs.mkdirSync(dst, { recursive: true });
    fs.writeFileSync(path.join(dst, "SKILL.md"), "# stub\n");
  }
  return live;
}

test("the kit carries the room's README, and it is the only package file inside it", () => {
  const room = path.join(ROOT, "kit", ".constitution", "project");
  assert.ok(fs.existsSync(path.join(room, "README.md")), "kit/.constitution/project/README.md is missing");
  assert.deepEqual(fs.readdirSync(room), ["README.md"],
    "the room in the kit MUST hold README.md only — any other file means a product's own rule got published");
});

test("promote SKIPS the room: a product's own rule is not published, and the package README survives", () => {
  const pkg = isolatedPackage();
  const live = fakeLiveRepo(pkg);
  const room = path.join(pkg, "kit", ".constitution", "project");
  const before = fs.readFileSync(path.join(room, "README.md"), "utf8");
  try {
    execFileSync(process.execPath, [path.join(pkg, "bin", "wdi-method.js"), "promote", live],
                 { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    assert.ok(!fs.existsSync(path.join(room, "secret-client.md")),
      "a product's own rule reached the kit — the leak this test exists to catch");
    assert.equal(fs.readFileSync(path.join(room, "README.md"), "utf8"), before,
      "the room's README was overwritten by the product's copy; it MUST stay owned by the package");
    assert.ok(fs.existsSync(path.join(pkg, "kit", ".constitution", "generic-guide.md")),
      "a generic file failed to land — the filter is too wide");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(live, { recursive: true, force: true });
  }
});

test("update SEEDS the room once and never overwrites it again", () => {
  const pkg = isolatedPackage();
  const target = tmp("target");
  const mine = path.join(target, ".constitution", "project", "my-rule.md");
  fs.mkdirSync(path.dirname(mine), { recursive: true });
  fs.writeFileSync(mine, "belongs to the product\n");
  fs.writeFileSync(path.join(target, ".constitution", "project", "README.md"), "EDITED\n");
  try {
    execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check"],
      { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    assert.equal(fs.readFileSync(mine, "utf8"), "belongs to the product\n",
      "update overwrote a product rule in its own room — that is exactly what this room exists to prevent");
    assert.equal(fs.readFileSync(path.join(target, ".constitution", "project", "README.md"), "utf8"),
      "EDITED\n", "update overwrote an existing room file; it MUST seed only when empty");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("walkFiles refuses build output — a .pyc carries an absolute path naming the product", () => {
  const src = fs.readFileSync(path.join(ROOT, "bin", "wdi-method.js"), "utf8");
  const skipDirs = /const SKIP_DIRS = new Set\(\[([^\]]*)\]/s.exec(src);
  const skipFile = /const SKIP_FILE = (\/.*\/i);/.exec(src);
  assert.ok(skipDirs, "SKIP_DIRS is missing from bin/wdi-method.js");
  assert.ok(skipDirs[1].includes('"__pycache__"'), "__pycache__ is not filtered");
  assert.ok(skipFile, "SKIP_FILE is missing");
  const re = eval(skipFile[1]);
  assert.match("inventory.cpython-314.pyc", re);
  assert.doesNotMatch("keep.md", re);
});

test("update REMOVES a retired wrapper, and leaves alone what is not ours", () => {
  const pkg = isolatedPackage();
  const target = tmp("target");
  const skills = path.join(target, ".claude", "skills");
  // retired: an old name that still carries a SKILL.md
  fs.mkdirSync(path.join(skills, "wdi-apply"), { recursive: true });
  fs.writeFileSync(path.join(skills, "wdi-apply", "SKILL.md"), "# old wrapper");
  // not ours: starts with wdi- but carries no SKILL.md
  fs.mkdirSync(path.join(skills, "wdi-my-own"), { recursive: true });
  fs.writeFileSync(path.join(skills, "wdi-my-own", "notes.md"), "belongs to the user");
  try {
    execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check",
       "--agents", "claude"],
      { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    assert.ok(!fs.existsSync(path.join(skills, "wdi-apply")),
      "the retired wrapper is still there — an agent will call it and its guide no longer exists");
    assert.ok(fs.existsSync(path.join(skills, "wdi-my-own", "notes.md")),
      "a wdi-* folder with no SKILL.md was deleted; it belongs to the user, not to the method");
    assert.ok(fs.existsSync(path.join(skills, "wdi-decision", "SKILL.md")),
      "a wrapper that is still current was not installed");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("update keeps the product's initiative slug — promote scrubs it, update MUST NOT write it back", () => {
  // Found on the first real install: promote replaces the slug with FILL-initiative-slug before publishing
  // (right), and update then wrote that placeholder into the product repo (wrong). The slug lives in TWO
  // places in bmad-prd.toml and the file itself says both MUST change together, so restoring only one
  // produced exactly the inconsistency it forbids.
  const pkg = isolatedPackage();
  const target = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-slug-"));
  const kitToml = path.join(pkg, "kit", "assets", "bmad-custom", "bmad-prd.toml");
  const mine = path.join(target, "_bmad", "custom", "bmad-prd.toml");
  fs.mkdirSync(path.dirname(mine), { recursive: true });

  // what the package publishes: scrubbed in both spots, and one bare mention inside a comment
  fs.mkdirSync(path.dirname(kitToml), { recursive: true });
  fs.writeFileSync(kitToml, [
    '# a PRD landing in the folder named FILL-initiative-slug',
    'run_folder_pattern = "FILL-initiative-slug"',
    'facts = ["--path {project-root}/.control/memlog/prd-FILL-initiative-slug.md"]',
    '',
  ].join("\n"));
  // what the product actually has
  fs.writeFileSync(mine, [
    '# a PRD landing in the folder named FILL-initiative-slug',
    'run_folder_pattern = "shop-without-account"',
    'facts = ["--path {project-root}/.control/memlog/prd-shop-without-account.md"]',
    '',
  ].join("\n"));

  try {
    const out = execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check",
       "--agents", "claude"],
      { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    const after = fs.readFileSync(mine, "utf8");
    assert.match(after, /run_folder_pattern = "shop-without-account"/,
      "the placeholder overwrote a live run_folder_pattern");
    assert.match(after, /prd-shop-without-account\.md/,
      "the memlog path was left on the placeholder while the setting was restored — the two MUST agree");
    assert.match(after, /folder named FILL-initiative-slug/,
      "a bare mention in a comment was rewritten; that sentence explains the pattern");
    assert.match(out, /kept run_folder_pattern in bmad-prd\.toml/, "keeping it silently is not enough");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

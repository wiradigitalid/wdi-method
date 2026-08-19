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
  fs.writeFileSync(path.join(live, ".constitution", "project", "codebase-stack-guide.md"),
    "---\nstatus: Accepted\n---\n# stack\n\nThis product runs on Elixir and a secret client's own conventions.\n");
  for (const name of fs.readdirSync(path.join(pkg, "kit", "skills"))) {
    const dst = path.join(live, ".claude", "skills", name);
    fs.mkdirSync(dst, { recursive: true });
    fs.writeFileSync(path.join(dst, "SKILL.md"), "# stub\n");
  }
  return live;
}

test("the kit's room holds exactly the five files the package authors, and nothing a product wrote", () => {
  // 0.5.0 moved two more things into the room: the product's Articles 1-2-5, and the three codebase
  // guides that used to sit in their own folder. All five are authored HERE and seeded once; anything
  // else appearing means a product's own rule was published.
  const room = path.join(ROOT, "kit", ".constitution", "project");
  assert.deepEqual(fs.readdirSync(room).sort(), [
    "README.md",
    "codebase-brownfield-guide.md",
    "codebase-conventions-guide.md",
    "codebase-stack-guide.md",
    "constitution.md",
  ], "the room in the kit MUST hold exactly the package's own five files");
});

test("promote SKIPS the room: a product's own rule is not published, and the package README survives", () => {
  const pkg = isolatedPackage();
  const live = fakeLiveRepo(pkg);
  const room = path.join(pkg, "kit", ".constitution", "project");
  const before = fs.readFileSync(path.join(room, "README.md"), "utf8");
  try {
    execFileSync(process.execPath, [path.join(pkg, "bin", "wdi-method.js"), "promote", live, "--rescue"],
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

test("promote SKIPS the codebase guides too — they live in the room now, so one rule covers them", () => {
  // Before 0.5.0 these sat in .constitution/codebase/ and needed a promote rule of their own, which
  // they did not have: a product's Accepted stack guide would have been published. Now they are room
  // files, so the room's single skip covers them — this test is what proves that claim.
  const pkg = isolatedPackage();
  const live = fakeLiveRepo(pkg);
  const room = path.join(pkg, "kit", ".constitution", "project");
  try {
    execFileSync(process.execPath, [path.join(pkg, "bin", "wdi-method.js"), "promote", live, "--rescue"],
                 { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    for (const name of fs.readdirSync(room)) {
      assert.doesNotMatch(fs.readFileSync(path.join(room, name), "utf8"), /Elixir|Secret Client/,
        `${name} carries the product's content — the room MUST stay the package's own`);
    }
    assert.ok(fs.existsSync(path.join(room, "codebase-stack-guide.md")),
      "the package's empty codebase template did not survive promote");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(live, { recursive: true, force: true });
  }
});

test("update keeps a codebase guide that is still Draft — that is when it is being written", () => {
  // The template itself says this file stays Draft until the first wave's distillation ratifies it.
  // Gating the keep on `status: Accepted` therefore protected it in every window EXCEPT the one that
  // matters: a half-written stack guide was silently replaced by the empty template, with no note.
  const pkg = isolatedPackage();
  const target = tmp("target");
  const mine = path.join(target, ".constitution", "project", "codebase-stack-guide.md");
  const written = "---\nstatus: Draft\n---\n\n# stack\n\nHalf-written, not yet ratified.\n";
  fs.mkdirSync(path.dirname(mine), { recursive: true });
  fs.writeFileSync(mine, written);
  try {
    const out = execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check",
       "--agents", "claude"],
      { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    assert.equal(fs.readFileSync(mine, "utf8"), written,
      "a Draft codebase guide was overwritten — update destroyed work in the only window it is written in");
    assert.match(out, /keep project\/codebase-stack-guide\.md/, "keeping it silently is not enough");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
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
    // README.md is the ONE exception, and deliberately so since the room README claimed in its own
    // text to be the package's while update kept it forever — which left a real repo pointing at a
    // folder 0.5.0 had deleted. It carries no product decision, so refreshing it loses nothing.
    assert.doesNotMatch(fs.readFileSync(path.join(target, ".constitution", "project", "README.md"), "utf8"),
      /^EDITED$/m, "the room README is the package's and MUST be refreshed, not kept");
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

// ---------------------------------------------------------------- the 0.5.0 layout migration
//
// 0.5.0 moved .constitution/ to exactly two folders. An installed repo carries the OLD shape, and
// without a migration `update` would write the new paths while the old files stayed behind: two
// copies of most guides, and no way for an agent reading AGENTS.md routing to tell which one binds.

/** A repo in the pre-0.5.0 shape, with the product's own work in it. */
function fakeOldLayoutRepo() {
  const t = tmp("old");
  const c = (...p) => path.join(t, ".constitution", ...p);
  fs.mkdirSync(c("document", "templates"), { recursive: true });
  fs.mkdirSync(c("scripts"), { recursive: true });
  fs.mkdirSync(c("codebase"), { recursive: true });
  fs.mkdirSync(c("method"), { recursive: true });
  fs.mkdirSync(c("project"), { recursive: true });
  // generic, at the old locations
  for (const n of ["README", "language-guide", "method-glossary", "repo-guide", "structure-guide"]) {
    fs.writeFileSync(c(`${n}.md`), `# ${n} (old location)\n`);
  }
  for (const n of ["README", "artifact-map", "portability", "rationale"]) {
    fs.writeFileSync(c("method", `${n}.md`), `# ${n} (was method/ root)\n`);
  }
  fs.writeFileSync(c("document", "srs-guide.md"), "# srs\n");
  fs.writeFileSync(c("document", "templates", "srs.md"), "# srs template\n");
  fs.writeFileSync(c("scripts", "validate.py"), "# validate\n");
  // the product's own work — every one of these MUST survive
  // The real shape: seven articles, three of them the product's, and relative links to what used to
  // be a sibling. A single-heading stub would not exercise the split at all.
  fs.writeFileSync(c("constitution.md"), [
    "---", "status: Accepted", "---", "",
    "# Constitution — A Product", "",
    "## Article 1 — Scope", "", "See [`repo-guide.md`](repo-guide.md).", "",
    "## Article 2 — Content boundary", "", "MY OWN BOUNDARY RULE", "",
    "## Article 3 — Layers", "", "Generic.", "",
    "## Article 4 — Lifecycle", "", "Generic; `document/templates/` is exempt.", "",
    "## Article 5 — The method", "", "Protects `codebase/stack-guide.md`.", "",
    "## Article 6 — Decisions", "", "See `document/decision-guide.md`.", "",
    "## Article 7 — Non-technical facts", "", "Generic.", "",
  ].join("\n"));
  fs.writeFileSync(c("codebase", "stack-guide.md"),
    "---\nstatus: Draft\n---\n\n# stack\n\nGo 1.23 and MariaDB. HALF-WRITTEN BY THE PRODUCT.\n");
  fs.writeFileSync(c("project", "my-rule.md"),
    "---\nscope: project\npurpose: \"mine\"\n---\nPRODUCT RULE\n");
  // a file the product ADDED at the root — not the method's, and not ours to place
  fs.writeFileSync(c("our-own-extra-guide.md"), "ADDED BY THE PRODUCT\n");
  return t;
}

test("update migrates a pre-0.5.0 repo: nothing of the product's is lost, nothing is left behind", () => {
  const pkg = isolatedPackage();
  const target = fakeOldLayoutRepo();
  const c = (...p) => path.join(target, ".constitution", ...p);
  try {
    const out = execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check",
       "--agents", "claude"],
      { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });

    // 1. the product's three pieces of work survive, byte for byte
    assert.match(fs.readFileSync(c("project", "constitution.md"), "utf8"), /MY OWN BOUNDARY RULE/,
      "the product's Articles were lost — constitution.md MUST move whole into the room");
    assert.match(fs.readFileSync(c("project", "codebase-stack-guide.md"), "utf8"), /HALF-WRITTEN BY THE PRODUCT/,
      "a half-written codebase guide was lost in the move");
    assert.match(fs.readFileSync(c("project", "my-rule.md"), "utf8"), /PRODUCT RULE/,
      "an existing room file was overwritten by the migration");

    // 2. nothing is left at an old location — that is what makes the repo single-layout again
    for (const stale of ["document", "scripts", "codebase", "constitution.md",
                         "README.md", "language-guide.md", "method-glossary.md",
                         "repo-guide.md", "structure-guide.md"]) {
      assert.ok(!fs.existsSync(c(stale)), `.constitution/${stale} is still there — two layouts at once`);
    }
    for (const n of ["README", "artifact-map", "portability", "rationale"]) {
      assert.ok(fs.existsSync(c("method", "why", `${n}.md`)), `${n}.md did not reach method/why/`);
    }
    assert.ok(fs.existsSync(c("method", "document", "srs-guide.md")), "document/ did not reach method/");
    assert.ok(fs.existsSync(c("method", "scripts", "validate.py")), "scripts/ did not reach method/");

    // 3. a file the PRODUCT added is not guessed at — it may be routed by its current path
    assert.ok(fs.existsSync(c("our-own-extra-guide.md")),
      "a file the product added was moved; the migration MUST NOT guess where somebody else's file goes");
    assert.match(out, /our-own-extra-guide\.md/, "leaving it silently is not enough — say so");

    // 4. the method's articles are CUT, not left duplicated. 0.5.0 moved the file whole and asked the
    //    owner to delete them, which left every migrated repo carrying them twice — one copy frozen in
    //    project/ and drifting. An external audit of 0.5.0 named this as its worst finding.
    const mine = fs.readFileSync(c("project", "constitution.md"), "utf8");
    assert.match(mine, /^## Article 2\b/m, "the product's own Article 2 was cut — only 3, 4, 6, 7 are the method's");
    assert.doesNotMatch(mine, /^## Article 4\b/m, "Article 4 is the method's and MUST NOT stay in the room");
    assert.doesNotMatch(mine, /^## Article 6\b/m, "Article 6 is the method's and MUST NOT stay in the room");
    assert.match(out, /kept Articles .*removed/, "the cut MUST be reported, not done silently");
    // and the links it left behind MUST resolve from one level deeper
    assert.match(mine, /\.\.\/method\/repo-guide\.md/,
      "a relative link to a former sibling was left pointing inside project/, where nothing is");

    // 5. derived output is named rather than silently left stale
    assert.match(out, /validate\.py --generate/, "the generated tables were not mentioned");
    assert.match(out, /wdi-init/, "the structure maps were not mentioned");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("update splits project/constitution.md even with NO migration — the 0.5.0 adopter's case", () => {
  // 0.5.2 only ran the split from inside migrateToTwoFolders, which returns early when the pre-0.5.0
  // layout is absent. So a repo that took 0.5.0 — whose constitution.md was moved WHOLE and never
  // split — could never be fixed by any later update. That is exactly the repo that needs it, which
  // makes this a reachability bug rather than a design choice. Found by an audit of a real 0.5.0 →
  // 0.5.2 update, where the run printed nothing about the seven articles still sitting in the room.
  const pkg = isolatedPackage();
  const target = tmp("already-050");
  const room = path.join(target, ".constitution", "project");
  fs.mkdirSync(room, { recursive: true });
  fs.mkdirSync(path.join(target, ".constitution", "method"), { recursive: true });
  fs.writeFileSync(path.join(room, "constitution.md"), [
    "---", "status: Accepted", "---", "",
    "# Constitution — A Product", "",
    "## Article 1 — Scope", "", "See [`repo-guide.md`](repo-guide.md).", "",
    "## Article 2 — Content boundary", "", "MY BOUNDARY RULE", "",
    "## Article 4 — Lifecycle", "", "The method's.", "",
    "## Article 5 — The method", "", "Protects `codebase/stack-guide.md`.", "",
    "## Article 6 — Decisions", "", "The method's.", "",
  ].join("\n"));
  try {
    const out = execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check",
       "--agents", "claude"],
      { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    const mine = fs.readFileSync(path.join(room, "constitution.md"), "utf8");
    assert.doesNotMatch(mine, /^## Article 4\b/m, "Article 4 is the method's and was not removed");
    assert.doesNotMatch(mine, /^## Article 6\b/m, "Article 6 is the method's and was not removed");
    assert.match(mine, /^## Article 2\b/m, "the product's own article was removed");
    assert.match(mine, /MY BOUNDARY RULE/, "the product's own text was lost");
    assert.match(mine, /\.\.\/method\/repo-guide\.md/, "a broken relative link was left in place");
    assert.match(mine, /codebase-stack-guide\.md/, "the old codebase/ path was left in place");
    assert.match(out, /still carried Articles/, "doing it silently is not enough");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("update refreshes the room's README — it is the package's, and a stale copy misinforms", () => {
  // The README claimed in its own text to be "authored in the package", yet update kept it forever.
  // worship-presenter-web's copy still pointed at .constitution/codebase/*-guide.md, a folder 0.5.0
  // deletes, and nothing would ever have corrected it. Either the package writes it or it stops
  // claiming authorship — this is the first.
  const pkg = isolatedPackage();
  const target = tmp("stale-readme");
  const room = path.join(target, ".constitution", "project");
  fs.mkdirSync(room, { recursive: true });
  fs.writeFileSync(path.join(room, "README.md"), "STALE, pointing at .constitution/codebase/\n");
  fs.writeFileSync(path.join(room, "mine.md"), "---\nscope: project\n---\nMINE\n");
  try {
    execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check",
       "--agents", "claude"],
      { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    assert.doesNotMatch(fs.readFileSync(path.join(room, "README.md"), "utf8"), /STALE/,
      "the room README was kept stale — it is the package's and MUST be refreshed");
    assert.match(fs.readFileSync(path.join(room, "mine.md"), "utf8"), /MINE/,
      "a real product rule was overwritten — only README.md is the package's in this room");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

// `waves.yaml` → `specs.yaml` is the one rename in this migration that touches a CONSUMER's data.
//
// Every other file the installer writes is the package's: it may be overwritten, because nothing of
// the product's is in it. `.control/registry/waves.yaml` is the opposite — it holds the product's own
// plan, and a repo that has been running this method for months has real rows in it. So the rename
// cannot be done by writing the new name and walking away: that leaves the product with an empty
// `specs.yaml` beside a full `waves.yaml`, and the validator then reports a corpus with no work in it.
//
// These three tests are the contract: the data moves, the move happens once, and a file the product
// already owns is never written over.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..");

function tmp(name) {
  return fs.mkdtempSync(path.join(os.tmpdir(), `wdi-${name}-`));
}

/** A copy of the package that may be mutated freely — same reason as project-room.test.mjs. */
function isolatedPackage() {
  const dir = tmp("pkg");
  for (const part of ["bin", "lib", "kit", "kit-overlay", "scaffold"]) {
    const src = path.join(ROOT, part);
    if (fs.existsSync(src)) fs.cpSync(src, path.join(dir, part), { recursive: true });
  }
  fs.copyFileSync(path.join(ROOT, "package.json"), path.join(dir, "package.json"));
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

// What a repo that has actually been delivering looks like: a closed unit, its rows, its review
// trace. Every one of these lines has to come out the other side.
const REAL_PLAN = [
  "# waves.yaml — rencana kerja.",
  "",
  "waves:",
  "  - id: W1",
  "    release: R1",
  "    prd: [checkout]",
  "    status: closed",
  "    spec_folder: _bmad-output/specs/w1-checkout/",
  "    epics:",
  "      - id: W1-E1",
  "        stories:",
  "          - id: W1-E1-S1",
  "            component: PC-1",
  "            satisfies: [UC-1]",
  "            tests: [\"checkout charges once\"]",
  "",
].join("\n");

function repoWithAPlan() {
  const t = tmp("live");
  const reg = path.join(t, ".control", "registry");
  fs.mkdirSync(reg, { recursive: true });
  fs.writeFileSync(path.join(reg, "waves.yaml"), REAL_PLAN);
  fs.writeFileSync(path.join(reg, "index.yaml"), "product:\n  name: A Product\n");
  return t;
}

function update(pkg, target) {
  return execFileSync(process.execPath,
    [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check",
     "--agents", "claude"],
    { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
}

test("update RENAMES waves.yaml to specs.yaml and the product's plan survives byte for byte", () => {
  const pkg = isolatedPackage();
  const target = repoWithAPlan();
  const reg = (n) => path.join(target, ".control", "registry", n);
  try {
    update(pkg, target);
    assert.ok(fs.existsSync(reg("specs.yaml")),
      "specs.yaml was not created — the product is left with a registry the validator no longer reads");
    assert.equal(fs.readFileSync(reg("specs.yaml"), "utf8"), REAL_PLAN,
      "the plan was altered in the move. The installer renames the FILE; rewriting what is inside "
      + "it is the product's own migration, and guessing at it destroys real work");
    assert.ok(!fs.existsSync(reg("waves.yaml")),
      "waves.yaml is still there beside specs.yaml — two homes for one plan, which is exactly the "
      + "state ticket-status-one-home exists to prevent");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("a second update is a no-op — the rename happens once and waves.yaml is never resurrected", () => {
  const pkg = isolatedPackage();
  const target = repoWithAPlan();
  const reg = (n) => path.join(target, ".control", "registry", n);
  try {
    update(pkg, target);
    fs.writeFileSync(reg("specs.yaml"), `${REAL_PLAN}# EDITED AFTER THE MIGRATION\n`);
    update(pkg, target);
    assert.match(fs.readFileSync(reg("specs.yaml"), "utf8"), /EDITED AFTER THE MIGRATION/,
      "the second update overwrote the product's plan — the registry is the product's, not ours");
    assert.ok(!fs.existsSync(reg("waves.yaml")),
      "waves.yaml came back. Seeding it again after a migration is the installer undoing its own work");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("with BOTH files present the migration refuses: specs.yaml is never written over", () => {
  // The state a half-finished hand migration leaves behind. Whichever file is the real one, the
  // installer cannot tell — so it MUST NOT choose, and it MUST NOT silently discard either.
  const pkg = isolatedPackage();
  const target = repoWithAPlan();
  const reg = (n) => path.join(target, ".control", "registry", n);
  fs.writeFileSync(reg("specs.yaml"), "specs:\n  - id: SPEC-1\n    release: R1  # WRITTEN BY HAND\n");
  try {
    const out = update(pkg, target);
    assert.match(fs.readFileSync(reg("specs.yaml"), "utf8"), /WRITTEN BY HAND/,
      "specs.yaml was overwritten by the old file — a hand migration was destroyed by an update");
    assert.ok(fs.existsSync(reg("waves.yaml")),
      "waves.yaml was deleted while its content had nowhere to go");
    assert.match(out, /waves\.yaml/,
      "the installer left two registries in place and said nothing — the reader finds out from a "
      + "validator finding weeks later");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

// ---------------------------------------------------------------------------------------------
// The same argument `pruneRetiredSkills` was written for, one folder over.
//
// `_bmad/custom/*.toml` are overrides this package ships to shape BMad skills. When the engine
// layer below G5 changed, five of those engines were retired — and a retired engine's override is
// worse than no override: it is still installed, still read by BMad, and still describes a world
// that ended. bmad-retrospective.toml is the clearest case; it instructs an agent to archive an
// `RTR-` file against a validator, V19, that no longer exists.
//
// Update never removed a toml it had stopped shipping, so every repo installed before this keeps
// all five forever. That is what this covers.
const RETIRED_TOMLS = [
  "bmad-spec.toml", "bmad-build.toml", "bmad-build-auto.toml",
  "bmad-code-review.toml", "bmad-retrospective.toml",
];

test("update REMOVES an override for a retired engine, and keeps what the product wrote", () => {
  const pkg = isolatedPackage();
  const target = tmp("target");
  const custom = path.join(target, "_bmad", "custom");
  fs.mkdirSync(custom, { recursive: true });
  for (const name of RETIRED_TOMLS) {
    fs.writeFileSync(path.join(custom, name), "# shipped by an older version of this package\n");
  }
  // Two files that are NOT ours and MUST survive: a product's own override, and the `.user.toml`
  // half of the pair, which is the product's side of every override by convention.
  fs.writeFileSync(path.join(custom, "bmad-build.user.toml"), "# the product's own half\n");
  fs.writeFileSync(path.join(custom, "bmad-something-we-never-shipped.toml"), "# not ours\n");
  try {
    const out = update(pkg, target);
    for (const name of RETIRED_TOMLS) {
      assert.ok(!fs.existsSync(path.join(custom, name)),
        `${name} overrides an engine this method retired, and update left it installed`);
    }
    assert.ok(fs.existsSync(path.join(custom, "bmad-build.user.toml")),
      "a .user.toml is the PRODUCT's half of an override and is never the installer's to delete");
    assert.ok(fs.existsSync(path.join(custom, "bmad-something-we-never-shipped.toml")),
      "update deleted a toml this package never shipped — _bmad/custom/ is not our namespace, "
      + "so removal MUST be by an explicit retired list, never by 'not in the kit'");
    assert.match(out, /retired override/,
      "files were deleted from someone else's repo in silence");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

// The requirement registry split has the same shape of hazard as waves→specs, and the opposite
// answer. There, a tool COULD move the data safely, so it did. Here it cannot: splitting FR rows per
// PRD needs to know which initiative each promise belongs to, and nothing in the registry ever
// recorded that. So the installer seeds the product file and leaves every row where it is — the
// loader unions whatever it finds, which is what keeps a half-split repo working.

const REAL_REQUIREMENTS = [
  "goals:",
  "  - id: BG-1",
  '    statement: "Sesuatu yang nyata"',
  "",
  "functional:",
  "  - id: FR-1",
  "    capability: CAP-1",
  '    statement: "Sebuah janji yang sudah dikirim"',
  "",
].join("\n");

function repoWithRequirements() {
  const t = tmp("req");
  const reg = path.join(t, ".control", "registry");
  fs.mkdirSync(reg, { recursive: true });
  fs.writeFileSync(path.join(reg, "requirements.yaml"), REAL_REQUIREMENTS);
  fs.writeFileSync(path.join(reg, "index.yaml"), "product:\n  name: A Product\n");
  return t;
}

test("update SEEDS goals.yaml and does not touch one row of requirements.yaml", () => {
  const pkg = isolatedPackage();
  const target = repoWithRequirements();
  const reg = (n) => path.join(target, ".control", "registry", n);
  try {
    const out = update(pkg, target);
    assert.ok(fs.existsSync(reg("goals.yaml")),
      "the product file was not seeded, so nothing tells the owner where BG and CAP now live");
    assert.equal(fs.readFileSync(reg("requirements.yaml"), "utf8"), REAL_REQUIREMENTS,
      "requirements.yaml was altered. Which PRD an FR belongs to was never recorded, so any split "
      + "an installer performs is a guess — and a promise filed under the wrong initiative is worse "
      + "than one left where it is");
    assert.match(out, /requirements-<slug>\.yaml/,
      "the run said nothing about how to finish the split, which leaves the owner with two files "
      + "and no instruction");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("a second update does not re-seed — the product file is the product's once it exists", () => {
  const pkg = isolatedPackage();
  const target = repoWithRequirements();
  const reg = (n) => path.join(target, ".control", "registry", n);
  try {
    update(pkg, target);
    fs.writeFileSync(reg("goals.yaml"),
      'goals:\n  - id: BG-1\n    statement: "Dipindahkan dengan tangan"\n');
    update(pkg, target);
    assert.match(fs.readFileSync(reg("goals.yaml"), "utf8"), /Dipindahkan dengan tangan/,
      "the second update wrote over rows the owner had already moved in — the seed happens once");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

// A repo on 0.5.14 — the last version actually published — carries every OLD shape at once. `update`
// MUST move what a tool can move, leave what needs judgment exactly where it is, and then SAY what is
// left and which skill finishes it. An upgrade that breaks the repo, or one that silently leaves it
// half-migrated, both fail the same person.
function repoOn0514() {
  const t = tmp("v0514");
  const mk = (rel, body) => {
    const f = path.join(t, rel);
    fs.mkdirSync(path.dirname(f), { recursive: true });
    fs.writeFileSync(f, body);
  };
  mk(".control/wdi-method.yaml", 'wdi_method: "0.5.14"\n');
  mk(".control/registry/index.yaml", "product:\n  name: A Product\nmode: outline\n");
  mk(".control/registry/waves.yaml", REAL_PLAN);
  mk(".control/registry/requirements.yaml", REAL_REQUIREMENTS);
  mk(".control/generated/brief.md", "# brief\n\nold human page in the machine folder\n");
  mk(".what/_product-brief/brief.md",
     "# Product Brief: X\n\n## Executive Summary\n\ntext\n\n## Goals\n\n- **BG-1** — Sesuatu yang nyata\n\n## Assumptions\n\n- a\n\n## Vision\n\nlater\n");
  mk(".what/_prd/checkout/prd.md",
     "# PRD: Checkout\n\n## 0. Document Purpose\n\nwho\n\n## 3. Glossary\n\n- **Order** — a thing\n\n## 4. Features\n\n#### FR-1: Place order\n\n**Proof of done:** an order exists\n");
  mk(".what/checkout/SRS-checkout.md",
     "# SRS\n\n## UC Catalogue · [G3]\n\n| id | Use case | Actor | Satisfies | critical |\n| --- | --- | --- | --- | --- |\n| UC-1 | Place an order | Visitor | FR-1 | no |\n");
  mk(".how/checkout/SDD-checkout.md",
     "# SDD\n\n## Inherited Constraints · [guarded]\n\n| AD | Quoted rule | How it lands here |\n| --- | --- | --- |\n| AD-1 | one writer | via owns |\n");
  mk(".how/_platform/c4-l2-containers.md",
     "# C4 L2\n\n## Product Components per container\n\n| Container | Product Components living in it |\n| --- | --- |\n| app | checkout |\n");
  return t;
}

test("update from 0.5.14 moves the mechanical half, leaves the judgment half untouched, and names it", () => {
  const pkg = isolatedPackage();
  const target = repoOn0514();
  const reg = (n) => path.join(target, ".control", "registry", n);
  try {
    // The summary colours its labels; strip the escapes so the assertions read the words.
    const out = update(pkg, target).replace(/\[[0-9;]*m/g, "");

    // mechanical half: DONE by the installer
    assert.ok(fs.existsSync(reg("specs.yaml")) && !fs.existsSync(reg("waves.yaml")), "waves.yaml was not renamed");
    assert.ok(fs.existsSync(reg("goals.yaml")), "goals.yaml was not seeded");
    assert.ok(fs.existsSync(path.join(target, ".claude", "skills", "wdi-upgrade", "SKILL.md")),
      "the wdi-upgrade skill was not installed — the owner is told to run a skill they do not have");

    // judgment half: NOT touched — moving these takes a decision the installer cannot make
    assert.equal(fs.readFileSync(reg("requirements.yaml"), "utf8"), REAL_REQUIREMENTS, "requirements.yaml rows were moved by a tool that cannot know which PRD owns them");
    assert.match(fs.readFileSync(path.join(target, ".what", "_product-brief", "brief.md"), "utf8"), /## Executive Summary/, "the installer reshaped the brief — that is wdi-upgrade's, where a human sees it");
    assert.match(fs.readFileSync(path.join(target, ".what", "checkout", "SRS-checkout.md"), "utf8"), /\| UC-1 \|/, "the installer emptied the SRS catalogue before checking usecases.yaml holds the row");

    // and the summary SAYS what is left, item by item, and which skill finishes it
    assert.match(out, /upgrade\s+\d+ items? still in the OLD shape/, `the summary did not report pending upgrade work:\n${out}`);
    for (const item of ["requirements.yaml", "brief.md in the 14-section", "prd.md in the 12-section", "UC Catalogue table", "quoting AD-N", "PC x container", ".control/generated/", ".what-rendered"]) {
      assert.ok(out.includes(item), `pending item not named in the summary: ${item}\n${out}`);
    }
    assert.match(out, /wdi-upgrade/, "the summary does not name the skill that finishes the job");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("on a repo already in the new shape, update reports nothing pending", () => {
  const pkg = isolatedPackage();
  const target = repoWithRequirements();
  try {
    // Move the rows the way wdi-upgrade would, so the probe has nothing left to find.
    const reg = (n) => path.join(target, ".control", "registry", n);
    update(pkg, target);
    fs.writeFileSync(reg("goals.yaml"), 'goals:\n  - id: BG-1\n    statement: "Sesuatu yang nyata"\n');
    fs.rmSync(reg("requirements.yaml"));
    const out = update(pkg, target).replace(/\[[0-9;]*m/g, "");
    assert.doesNotMatch(out, /still in the OLD shape/,
      `a repo with nothing left to upgrade was told to upgrade — the probe is not idempotent:\n${out}`);
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

// A first install MUST validate green before a single product word is written. It did not, for
// three releases: three scaffold files cited method guides at the path they had before the kit moved
// under `.constitution/method/`, and cites-resolve caught them on every fresh repo. The installer's
// own tests never ran the validator on what they installed, so nothing here went red.
test("a FRESH install validates GREEN — the scaffold cites nothing that the kit does not place", (t) => {
  if (spawnSync("uv", ["--version"], { stdio: "ignore" }).status !== 0) {
    console.error("\n!!  uv is NOT installed — the fresh-install validation was NOT exercised.\n");
    t.skip("uv is not installed");
    return;
  }
  const pkg = isolatedPackage();
  const target = tmp("fresh");
  try {
    execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "install", target, "--yes", "--skip-bmad-check",
       "--agents", "claude", "--product", "Shopfront"],
      { cwd: pkg, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    let out = "";
    try {
      out = execFileSync("uv", ["run", path.join(target, ".constitution", "method", "scripts", "validate.py"),
                                "--root", target, "--check"],
                         { cwd: target, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"],
                           env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" } });
    } catch (e) {
      out = String(e.stdout || "") + String(e.stderr || "");
    }
    assert.match(out, /^GREEN/m,
      `a fresh install is RED — the first thing a new product's owner sees is a finding they did not cause:\n${out}`);
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

// A 0.5.12 PRD numbers its sections differently from a 0.5.15 one — Non-Goals is §7, Open Questions §10.
// A probe keyed to "## 5. Non-Goals" is silent on it, and a skill step that says "delete §8" deletes MVP
// Scope. Both must key on the section NAME.
test("update detects the OLD PRD shape under 0.5.12 numbering, and ignores a stale page path inside history", () => {
  const pkg = isolatedPackage();
  const target = tmp("v0512");
  try {
    fs.mkdirSync(path.join(target, ".control", "registry"), { recursive: true });
    fs.writeFileSync(path.join(target, ".control", "registry", "index.yaml"), "product:\n  name: A Product\n");
    fs.mkdirSync(path.join(target, ".what", "_prd", "desk"), { recursive: true });
    fs.writeFileSync(path.join(target, ".what", "_prd", "desk", "prd.md"),
      "# PRD: Desk\n\n## 1. Vision\n\nx\n\n## 7. Non-Goals (Explicit)\n\n- none\n\n## 8. MVP Scope\n\nx\n\n## 10. Open Questions\n\n- q\n");
    fs.mkdirSync(path.join(target, ".control", "memlog"), { recursive: true });
    fs.writeFileSync(path.join(target, ".control", "memlog", "pass-1.md"),
      "---\nartifact: .what/_prd/desk/prd.md\n---\nregenerated `.control/generated/blueprint.md`\n");
    const out = update(pkg, target).replace(/\x1b\[[0-9;]*m/g, "");
    assert.match(out, /a prd\.md in the 12-section shape/,
      `Non-Goals §7 / Open Questions §10 went undetected — the probe is keyed to another kit's numbers:\n${out}`);
    assert.doesNotMatch(out, /cites \.control\/generated/,
      `a stale path inside .control/memlog/ was reported — that is history, and cites-resolve does not read it:\n${out}`);
    // The summary's `upgrade` line is one of a dozen; "After update:" is the list a reader treats as
    // the to-do. When content is still in the old shape, that list MUST name the skill too.
    assert.match(out, /After update:[\s\S]*wdi-upgrade/,
      `"After update:" did not name wdi-upgrade while the summary listed pending items:\n${out}`);
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

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
import { execFileSync } from "node:child_process";

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
      + "state V18 exists to prevent");
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

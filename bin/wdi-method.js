#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const ROOT = path.resolve(__dirname, "..");
const KIT = path.join(ROOT, "kit");
const OVERLAY = path.join(ROOT, "kit-overlay");
const SCAFFOLD = path.join(ROOT, "scaffold", ".control");
const PKG = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8"));

const WDI_SKILLS = [
  "wdi-init",
  "wdi-problem",
  "wdi-product",
  "wdi-ux",
  "wdi-blueprint",
  "wdi-component",
  "wdi-build",
  "wdi-decision",
  "wdi-question",
  "wdi-log",
  "wdi-help",
  "wdi-reconcile",
  "wdi-review",
  "wdi-report",
  "wdi-systematic-debugging",
];

const PRODUCT_CONSTITUTION = "constitution.md";
const PRD_SLUG_PLACEHOLDER = "ISI-slug-inisiatif";
const GENERIC_FOLDER_PATTERNS = new Set([
  "_product-brief",
  "ux",
  "architecture",
  PRD_SLUG_PLACEHOLDER,
]);

const ALL_AGENTS = ["claude", "cursor", "codex", "antigravity"];

const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const DIM = "\x1b[2m";
const RESET = "\x1b[0m";

function die(msg) {
  console.error(`${RED}error:${RESET} ${msg}`);
  process.exit(1);
}

function ok(msg) {
  console.log(`${GREEN}ok${RESET}  ${msg}`);
}

function note(msg) {
  console.log(`${DIM}·${RESET}   ${msg}`);
}

function usage() {
  console.log(`wdi-method ${PKG.version}

  install [dir] [--agents a,b] [--skip-bmad-check]
  update  [dir] [--agents a,b] [--skip-bmad-check]
  verify  [dir] [--agents a,b]
  promote <live-dir>

BMad first, then this package. See README.md.
`);
}

function parseArgs(argv) {
  const args = { cmd: null, dir: null, agents: ALL_AGENTS.slice(), skipBmad: false };
  const rest = argv.slice(2);
  if (rest.length === 0 || rest[0] === "-h" || rest[0] === "--help") {
    usage();
    process.exit(0);
  }
  args.cmd = rest.shift();
  while (rest.length) {
    const t = rest.shift();
    if (t === "--skip-bmad-check") args.skipBmad = true;
    else if (t === "--agents") {
      const raw = rest.shift();
      if (!raw) die("--agents needs a comma-separated list");
      args.agents = raw.split(",").map((s) => s.trim()).filter(Boolean);
      for (const a of args.agents) {
        if (!ALL_AGENTS.includes(a)) die(`unknown agent: ${a}`);
      }
    } else if (t.startsWith("-")) die(`unknown flag: ${t}`);
    else if (!args.dir) args.dir = t;
    else die(`unexpected argument: ${t}`);
  }
  return args;
}

function walkFiles(dir) {
  const out = [];
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walkFiles(p));
    else if (entry.isFile()) out.push(p);
  }
  return out;
}

function copyFile(src, dest) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
}

function copyTree(src, dest) {
  let n = 0;
  for (const p of walkFiles(src)) {
    copyFile(p, path.join(dest, path.relative(src, p)));
    n += 1;
  }
  return n;
}

function posixRel(from, to) {
  return path.relative(from, to).split(path.sep).join("/");
}

function acceptedCodebase(file) {
  try {
    const head = fs.readFileSync(file, "utf8").slice(0, 400);
    return /status:\s*Accepted/i.test(head);
  } catch {
    return false;
  }
}

function bmadPresent(target) {
  const markers = [
    path.join(target, ".claude", "skills", "bmad-help", "SKILL.md"),
    path.join(target, "_bmad", "core", "config.yaml"),
    path.join(target, "_bmad", "_config", "manifest.yaml"),
  ];
  return markers.some((p) => fs.existsSync(p));
}

function readBmadVersion(target) {
  const manifest = path.join(target, "_bmad", "_config", "manifest.yaml");
  if (!fs.existsSync(manifest)) return "";
  const text = fs.readFileSync(manifest, "utf8");
  const m = text.match(/installation:\s*\n\s*version:\s*(\S+)/);
  return m ? m[1] : "";
}

function gitHead(repo) {
  const r = spawnSync("git", ["-C", repo, "rev-parse", "--short", "HEAD"], {
    encoding: "utf8",
  });
  if (r.status !== 0) return "unknown";
  return r.stdout.trim();
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function requireKit() {
  if (!fs.existsSync(path.join(KIT, ".constitution"))) {
    die(`kit missing at ${KIT}`);
  }
}

function requireTarget(dir) {
  const target = path.resolve(dir || process.cwd());
  if (!fs.existsSync(target) || !fs.statSync(target).isDirectory()) {
    die(`target is not a directory: ${target}`);
  }
  return target;
}

function skillDests(target, agents) {
  const dests = [];
  if (agents.includes("claude")) dests.push(path.join(target, ".claude", "skills"));
  if (agents.includes("cursor") || agents.includes("antigravity")) {
    dests.push(path.join(target, ".agents", "skills"));
  }
  return dests;
}

function syncConstitution(target) {
  const kitConst = path.join(KIT, ".constitution");
  const destConst = path.join(target, ".constitution");
  fs.mkdirSync(destConst, { recursive: true });
  let written = 0;
  let skipped = 0;
  for (const p of walkFiles(kitConst)) {
    const rel = posixRel(kitConst, p);
    const dest = path.join(destConst, rel);
    if (rel === PRODUCT_CONSTITUTION && fs.existsSync(dest)) {
      skipped += 1;
      note(`keep ${rel} (product articles)`);
      continue;
    }
    if (rel.startsWith("codebase/") && fs.existsSync(dest) && acceptedCodebase(dest)) {
      skipped += 1;
      note(`keep ${rel} (Accepted codebase guide)`);
      continue;
    }
    copyFile(p, dest);
    written += 1;
  }
  return { written, skipped };
}

function syncSkills(target, agents) {
  let n = 0;
  const dests = skillDests(target, agents);
  if (dests.length === 0) {
    note("no skill destinations for selected agents — AGENTS.md still applies");
    return 0;
  }
  for (const name of WDI_SKILLS) {
    const src = path.join(KIT, "skills", name);
    if (!fs.existsSync(src)) die(`kit missing skill ${name}`);
    for (const root of dests) {
      const dest = path.join(root, name);
      fs.rmSync(dest, { recursive: true, force: true });
      n += copyTree(src, dest);
    }
  }
  return n;
}

function syncTomls(target) {
  const src = path.join(KIT, "assets", "bmad-custom");
  const dest = path.join(target, "_bmad", "custom");
  fs.mkdirSync(dest, { recursive: true });
  let n = 0;
  for (const p of walkFiles(src)) {
    if (!p.endsWith(".toml") || p.endsWith(".user.toml")) continue;
    copyFile(p, path.join(dest, path.basename(p)));
    n += 1;
  }
  return n;
}

function seedControlIfMissing(target) {
  const control = path.join(target, ".control");
  if (fs.existsSync(control)) {
    note(".control/ already present — left untouched");
    return;
  }
  if (!fs.existsSync(SCAFFOLD)) die(`scaffold missing: ${SCAFFOLD}`);
  const n = copyTree(SCAFFOLD, control);
  ok(`seeded empty .control/ (${n} files)`);
}

function seedEmptyLayers(target) {
  for (const rel of [".what", path.join(".how", "_platform"), ".work", path.join("_bmad-output", "prior-knowledge")]) {
    const p = path.join(target, rel);
    if (!fs.existsSync(p)) {
      fs.mkdirSync(p, { recursive: true });
      note(`created ${rel.replaceAll(path.sep, "/")}/`);
    }
  }
}

function seedAgentFiles(target, agents) {
  const agentsFile = path.join(target, "AGENTS.md");
  const template = path.join(OVERLAY, "AGENTS.md");
  if (!fs.existsSync(agentsFile) && fs.existsSync(template)) {
    copyFile(template, agentsFile);
    ok("AGENTS.md created from template — rewrite the product sections");
  } else if (fs.existsSync(agentsFile)) {
    note("AGENTS.md present — merge the method routing yourself; install will not overwrite it");
  }

  if (!fs.existsSync(agentsFile)) return;

  if (agents.includes("claude")) {
    const claude = path.join(target, "CLAUDE.md");
    if (!fs.existsSync(claude)) {
      fs.writeFileSync(claude, "@AGENTS.md\n", "utf8");
      note("CLAUDE.md created as @AGENTS.md");
    }
  }
  if (agents.includes("cursor")) {
    const cursorRules = path.join(target, ".cursorrules");
    if (!fs.existsSync(cursorRules)) {
      copyFile(agentsFile, cursorRules);
      note("created .cursorrules");
    }
  }
  if (agents.includes("antigravity") || agents.includes("cursor")) {
    const mirror = path.join(target, ".agents", "AGENTS.md");
    if (!fs.existsSync(mirror)) {
      fs.mkdirSync(path.dirname(mirror), { recursive: true });
      copyFile(agentsFile, mirror);
      note("created .agents/AGENTS.md");
    }
  }
}

function writeStamp(target) {
  const control = path.join(target, ".control");
  if (!fs.existsSync(control)) return;
  const stamp = [
    "# Written by wdi-method install/update. A trace, not a lockfile.",
    `wdi_method: ${PKG.version}`,
    `bmad_method: ${readBmadVersion(target) || '""'}`,
    `installed_at: ${today()}`,
    "",
  ].join("\n");
  fs.writeFileSync(path.join(control, "wdi-method.yaml"), stamp, "utf8");
  note("stamped .control/wdi-method.yaml");
}

function apply(target, agents, { first }) {
  requireKit();
  const { written, skipped } = syncConstitution(target);
  note(`constitution wrote ${written}, kept ${skipped}`);
  const nSkills = syncSkills(target, agents);
  note(`skills ${nSkills} files`);
  const nToml = syncTomls(target);
  note(`bmad custom ${nToml} toml → _bmad/custom/`);
  if (first) seedControlIfMissing(target);
  seedEmptyLayers(target);
  seedAgentFiles(target, agents);
  writeStamp(target);
  ok(`${first ? "installed" : "updated"} into ${target}`);
  console.log("");
  console.log("Then, in the target repo:");
  console.log("  1. Set product.name in .control/registry/index.yaml (G1 confirms it).");
  console.log("  2. Rewrite .constitution/constitution.md Articles 2 and 5 for this product.");
  console.log("  3. Merge method routing into AGENTS.md if it was already there.");
  console.log("  4. Run skill wdi-init intent setup.");
  console.log("  5. Sort existing documents. Do not move them in this step.");
}

function verify(target, agents) {
  requireKit();
  const missing = [];
  const kitConst = path.join(KIT, ".constitution");
  for (const p of walkFiles(kitConst)) {
    const rel = posixRel(kitConst, p);
    const dest = path.join(target, ".constitution", rel);
    if (!fs.existsSync(dest)) missing.push(`.constitution/${rel}`);
  }
  for (const name of WDI_SKILLS) {
    for (const root of skillDests(target, agents)) {
      const dest = path.join(root, name, "SKILL.md");
      if (!fs.existsSync(dest)) missing.push(posixRel(target, dest));
    }
  }
  const custom = path.join(KIT, "assets", "bmad-custom");
  for (const p of walkFiles(custom)) {
    if (!p.endsWith(".toml")) continue;
    const dest = path.join(target, "_bmad", "custom", path.basename(p));
    if (!fs.existsSync(dest)) missing.push(`_bmad/custom/${path.basename(p)}`);
  }
  if (fs.existsSync(path.join(target, ".control"))) {
    for (const p of walkFiles(SCAFFOLD)) {
      const rel = posixRel(SCAFFOLD, p);
      const dest = path.join(target, ".control", rel);
      if (!fs.existsSync(dest)) missing.push(`.control/${rel}`);
    }
  } else {
    missing.push(".control/ (folder missing — first install should have seeded it)");
  }
  for (const required of ["AGENTS.md", path.join(".constitution", "constitution.md")]) {
    if (!fs.existsSync(path.join(target, required))) missing.push(required.replaceAll(path.sep, "/"));
  }
  if (missing.length) {
    console.error(`${RED}missing ${missing.length}${RESET}`);
    for (const m of missing) console.error(`  ${m}`);
    process.exit(1);
  }
  ok(`method files present in ${target}`);
  note("extra product files are expected and were not checked");
}

function scrubPrdToml(file) {
  let raw = fs.readFileSync(file, "utf8");
  const m = raw.match(/run_folder_pattern\s*=\s*"([^"]+)"/);
  if (!m) return;
  const slug = m[1];
  if (GENERIC_FOLDER_PATTERNS.has(slug)) return;
  fs.writeFileSync(file, raw.split(slug).join(PRD_SLUG_PLACEHOLDER), "utf8");
  note("bmad-prd.toml initiative slug scrubbed to placeholder");
}

function promote(live) {
  live = path.resolve(live);
  if (!fs.existsSync(path.join(live, ".constitution"))) {
    die(`${live} has no .constitution/ — is this a method-carrying repo?`);
  }
  fs.rmSync(KIT, { recursive: true, force: true });
  fs.mkdirSync(KIT, { recursive: true });

  const nConst = copyTree(path.join(live, ".constitution"), path.join(KIT, ".constitution"));
  note(`constitution ${nConst} files`);

  let copiedSkills = 0;
  const skillsSrc = path.join(live, ".claude", "skills");
  for (const name of WDI_SKILLS) {
    const src = path.join(skillsSrc, name);
    if (!fs.existsSync(src)) die(`skill missing in live repo: ${src}`);
    copiedSkills += copyTree(src, path.join(KIT, "skills", name));
  }
  note(`skills ${copiedSkills} files (${WDI_SKILLS.length} wrappers)`);

  const customSrc = path.join(live, "_bmad", "custom");
  const customDst = path.join(KIT, "assets", "bmad-custom");
  fs.mkdirSync(customDst, { recursive: true });
  let tomls = 0;
  if (fs.existsSync(customSrc)) {
    for (const p of walkFiles(customSrc)) {
      if (!p.endsWith(".toml") || p.endsWith(".user.toml")) continue;
      copyFile(p, path.join(customDst, path.basename(p)));
      tomls += 1;
    }
  }
  const prd = path.join(customDst, "bmad-prd.toml");
  if (fs.existsSync(prd)) scrubPrdToml(prd);
  note(`bmad custom ${tomls} toml`);

  const replacements = {
    "constitution.md": path.join(KIT, ".constitution", "constitution.md"),
    "portability.md": path.join(KIT, ".constitution", "method", "portability.md"),
    "repo-guide.md": path.join(KIT, ".constitution", "repo-guide.md"),
    "README.md": path.join(KIT, ".constitution", "README.md"),
  };
  for (const [name, dest] of Object.entries(replacements)) {
    const src = path.join(OVERLAY, name);
    if (fs.existsSync(src)) {
      copyFile(src, dest);
      note(`${name} replaced with kit overlay`);
    }
  }

  const source = [
    `date: ${today()}`,
    `commit: ${gitHead(live)}`,
    "kind: working copy that currently carries a newer method",
    "note: the repo path and product name MUST NOT be recorded here",
    "",
  ].join("\n");
  fs.writeFileSync(path.join(ROOT, "SOURCE"), source, "utf8");
  ok(`SOURCE stamped ${today()} @ ${gitHead(live)}`);
  ok(`promoted into ${KIT}`);
}

function main() {
  const args = parseArgs(process.argv);
  if (!["install", "update", "verify", "promote"].includes(args.cmd)) {
    usage();
    process.exit(2);
  }
  if (args.cmd === "promote") {
    if (!args.dir) die("promote needs a path to the working copy");
    promote(args.dir);
    return;
  }
  const target = requireTarget(args.dir);
  if (args.cmd !== "verify" && !args.skipBmad && !bmadPresent(target)) {
    die(
      "BMad is not installed in this repo. Run `npx bmad-method install` first, then retry. " +
        "Pass --skip-bmad-check only if you know why.",
    );
  }
  if (args.cmd === "install") apply(target, args.agents, { first: true });
  else if (args.cmd === "update") apply(target, args.agents, { first: false });
  else verify(target, args.agents);
}

main();

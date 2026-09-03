#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import * as p from "@clack/prompts";
import {
  fillProductTitle,
  upsertMethodBlock,
} from "../lib/agents-block.mjs";
import {
  identityIsPlaceholder,
  humaniseFolderName,
  readLanguagePolicy,
  writeLanguagePolicy,
  DEFAULT_DOC_LANGUAGE,
  readProductIdentity,
  writeProductIdentity,
} from "../lib/identity.mjs";
import {
  detectPlatforms,
  formatPlatformList,
  isKnownPlatform,
  normalizePlatformIds,
  platformSelectOptions,
  platformUsesHook,
  PREFERRED_PLATFORM_IDS,
  skillDestinations,
} from "../lib/platforms.mjs";
import { opencodeCommandsDir, syncOpencodeCommands } from "../lib/opencode-commands.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
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
  "wdi-upgrade",
];

const PRD_SLUG_PLACEHOLDER = "FILL-initiative-slug";
const GENERIC_FOLDER_PATTERNS = new Set([
  "_product-brief",
  "ux",
  "architecture",
  PRD_SLUG_PLACEHOLDER,
]);

const BMAD_INSTALL = `npx bmad-method install`;
// The ticket engines G5 runs. BMad writes the documents; these cut the work. They are a Claude Code
// plugin installed per USER, not per repo, so the check reads the plugin registry — and the check
// warns instead of blocking, because G1–G4 run without them and a first install has no G5 yet.
const ENGINES_REPO = "https://github.com/mattpocock/skills";
const ENGINES_PLUGIN = "mattpocock-skills";
const ENGINES_INSTALL = `/plugin install ${ENGINES_PLUGIN}`;
const ENGINES_INSTALL_ANY = "npx skills@latest add mattpocock/skills";
const ENGINES_SETUP = "/setup-matt-pocock-skills";
const REPO_URL = "https://github.com/wiradigitalid/wdi-method";
const HELP_SKILL = "wdi-help";
const INIT_SKILL = "wdi-init";
// The room's readers file is seeded as a skeleton and is useless until a product writes it. The
// flag is the skeleton's own declaration, so this reads the same thing the engine does rather than
// guessing from the file's size or its age.
function readersAreSkeleton(target) {
  const file = path.join(target, ".constitution", "project", "inventory-readers.py");
  if (!fs.existsSync(file)) return false;
  return /^SKELETON\s*=\s*True\b/m.test(fs.readFileSync(file, "utf8"));
}
const BMAD_REPO = "https://github.com/bmad-code-org/BMAD-METHOD";
const WDI_REPO = "https://github.com/wiradigitalid/wdi-method";

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

  (no command)              interactive TUI — detects install vs update
  install [dir]             first install (TUI unless --yes)
  update  [dir]             update      (TUI unless --yes)
  verify  [dir]
  promote <live-dir> --rescue   pull a method change back out of a consumer (not the normal flow)

  --yes                     non-interactive
  --agents a,b              platform IDs (same as BMad --tools; legacy: claude = claude-code)
  --list-agents             print supported platform IDs
  --product NAME            written to index.yaml product.name
  --client NAME             written to index.yaml product.client (optional)
  --doc-language <text>            prose of working documents; free text, default English
  --doc-filename-language <text>   slug part of document filenames; free text, default English
  --skip-bmad-check

BMad first, then this package. ${WDI_REPO}
`);
}

function parseArgs(argv) {
  const args = {
    cmd: null,
    dir: null,
    agents: null,
    skipBmad: false,
    rescue: false,
    yes: false,
    product: null,
    client: null,
    docLanguage: null,
    docFilenameLanguage: null,
  };
  const rest = argv.slice(2);
  if (rest[0] === "-h" || rest[0] === "--help") {
    usage();
    process.exit(0);
  }
  if (rest[0] === "--list-agents") {
    console.log(formatPlatformList());
    process.exit(0);
  }
  if (rest.length === 0) {
    args.cmd = "wizard";
    return args;
  }
  const first = rest[0];
  if (["install", "update", "verify", "promote"].includes(first)) {
    args.cmd = rest.shift();
  } else if (first.startsWith("-")) {
    args.cmd = "wizard";
  } else {
    args.cmd = "wizard";
    args.dir = rest.shift();
  }
  while (rest.length) {
    const t = rest.shift();
    if (t === "--skip-bmad-check") args.skipBmad = true;
    else if (t === "--rescue") args.rescue = true;
    else if (t === "--yes" || t === "-y") args.yes = true;
    else if (t === "--agents") {
      const raw = rest.shift();
      if (!raw) die("--agents needs a comma-separated list");
      args.agents = normalizePlatformIds(raw.split(",").map((s) => s.trim()).filter(Boolean));
      const unknown = raw.split(",").map((s) => s.trim()).filter(Boolean)
        .filter((a) => !isKnownPlatform(a));
      if (unknown.length) die(`unknown platform: ${unknown.join(", ")} (run --list-agents)`);
      if (!args.agents.length) die("--agents needs at least one known platform");
    } else if (t === "--product") args.product = rest.shift();
    else if (t === "--client") args.client = rest.shift();
    else if (t === "--doc-language" || t === "--doc-filename-language") {
      // Free text: "English", "Bahasa Indonesia", "id" — a model reads it, so no list to match.
      const raw = (rest.shift() || "").trim();
      if (!raw) die(`${t} needs a value, for example: English`);
      if (t === "--doc-language") args.docLanguage = raw;
      else args.docFilenameLanguage = raw;
    }
    else if (t.startsWith("-")) die(`unknown flag: ${t}`);
    else if (!args.dir) args.dir = t;
    else die(`unexpected argument: ${t}`);
  }
  return args;
}

// Build output and editor droppings MUST NOT reach the kit. This repository is public, and a
// __pycache__/*.pyc carries the ABSOLUTE PATH of the source it was compiled from — which means a
// product name and a client folder leak into a public package through a file nobody wrote.
// Found 2026-08-18 on the first real promote: inventory.cpython-314.pyc embedded the live repo path.
const SKIP_DIRS = new Set(["__pycache__", "node_modules", ".git", ".pytest_cache", ".ruff_cache",
                           ".mypy_cache", ".venv", "venv", "dist", "build", ".idea", ".vscode"]);
const SKIP_FILE = /(\.pyc|\.pyo|\.pyd|\.log|\.tmp|\.swp|\.orig|\.rej|\.bak)$|^\.DS_Store$|^Thumbs\.db$/i;

function walkFiles(dir) {
  const out = [];
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (SKIP_DIRS.has(entry.name)) continue;
      out.push(...walkFiles(p));
    } else if (entry.isFile()) {
      if (SKIP_FILE.test(entry.name)) continue;
      out.push(p);
    }
  }
  return out;
}

function copyFile(src, dest) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
}

function copyTree(src, dest, skipRel) {
  let n = 0;
  for (const p of walkFiles(src)) {
    const rel = posixRel(src, p);
    if (skipRel && skipRel(rel)) continue;
    copyFile(p, path.join(dest, path.relative(src, p)));
    n += 1;
  }
  return n;
}

function posixRel(from, to) {
  return path.relative(from, to).split(path.sep).join("/");
}

function bmadPresent(target) {
  const markers = [
    path.join(target, ".claude", "skills", "bmad-help", "SKILL.md"),
    path.join(target, "_bmad", "core", "config.yaml"),
    path.join(target, "_bmad", "_config", "manifest.yaml"),
  ];
  return markers.some((p) => fs.existsSync(p));
}

function wdiPresent(target) {
  return (
    fs.existsSync(path.join(target, ".control", "wdi-method.yaml")) ||
    fs.existsSync(path.join(target, ".constitution", "method", "README.md"))
  );
}

function dirNonEmpty(target) {
  if (!fs.existsSync(target)) return false;
  return fs.readdirSync(target).some((n) => n !== ".git" && n !== ".gitignore");
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

/** `to-spec` · `to-tickets` · `implement` — present as a user-level plugin, or copied into the repo. */
function enginesPresent(target) {
  for (const dir of [".claude", ".agents", ".agent", ".cursor", ".codex"]) {
    if (fs.existsSync(path.join(target, dir, "skills", "to-tickets", "SKILL.md"))) return true;
  }
  const cfg = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude");
  const registry = path.join(cfg, "plugins", "installed_plugins.json");
  if (!fs.existsSync(registry)) return false;
  try {
    const plugins = JSON.parse(fs.readFileSync(registry, "utf8")).plugins || {};
    return Object.keys(plugins).some((k) => k.startsWith("mattpocock-skills@"));
  } catch {
    return false;
  }
}

function bmadMissingMessage() {
  return [
    "BMad Method is not installed in this repo. Install it first, then run this installer again.",
    "",
    `  ${BMAD_INSTALL}`,
    "",
    `Source: ${BMAD_REPO}`,
    "In the BMad installer, pick the same agents (Claude Code, Cursor, …).",
  ].join("\n");
}

// The product's custom room. Three properties, and all three MUST hold together:
//   install/update  seeds its content ONLY when absent — never written again after that
//   promote         SKIPS it entirely, so a product's own rules can never reach the public repo
//   agent           loads it like any other guide, so it BINDS
// The deliberate consequence: this room's README is authored in the package and never comes home
// through promote.
const PROJECT_ROOM = "project/";

// 0.5.0 moved `.constitution/` to exactly two folders: `method/` is the method's and is overwritten,
// `project/` is the product's and is never touched. Before it, generic and product-owned files sat
// side by side at the root, `codebase/` was a third product-owned room nobody had written down, and
// `constitution.md` was ONE file holding both — which is why `update` had to keep the whole thing and
// the product never received a fixed generic Article.
//
// Without this migration an installed repo would end up carrying BOTH layouts: the kit writes the new
// paths while the old files stay behind, and an agent reading `AGENTS.md` routing would find two
// copies of most guides and no way to tell which binds.
const OLD_ROOT_GUIDES = ["README", "language-guide", "method-glossary", "repo-guide", "structure-guide"];
const OLD_WHY = ["README", "artifact-map", "portability", "rationale"];
const OLD_CODEBASE = ["stack", "conventions", "brownfield"];

function mv(from, to) {
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.renameSync(from, to);
}

/** Article numbers that belong to the method half. The product keeps 1, 2, and 5. */
const METHOD_ARTICLES = [3, 4, 6, 7];

/**
 * Cut the method's articles out of a product's constitution.md, and repoint its relative links.
 *
 * Returns {cut, kept, relinked}, or null when the file does not look like a constitution at all —
 * in which case it is left ALONE rather than guessed at.
 *
 * 0.5.0 moved the file whole and printed "delete Articles 3, 4, 6, 7 yourself", on the grounds that
 * no script can tell an edited copy from the original. That reasoning was wrong in the way that
 * matters: the split does not need to know whether a section was edited, only which article numbers
 * are the method's — and the file states them in its own headings. Leaving it whole left every
 * migrated repo carrying those articles in TWO files, one of them frozen and drifting, plus relative
 * links that no longer resolve one level down. It is all in git, so cutting is reversible; not
 * cutting is what nobody notices.
 */
function splitProductConstitution(file) {
  if (!fs.existsSync(file)) return null;
  const raw = fs.readFileSync(file, "utf8");
  const crlf = raw.includes("\r\n");
  const text = crlf ? raw.replaceAll("\r\n", "\n") : raw;
  const marks = [...text.matchAll(/^## Article (\d+)\b.*$/gm)];
  if (marks.length < 2) return null;   // not the shape we know; do not touch it

  const kept = [];
  const cut = [];
  let out = text.slice(0, marks[0].index);
  for (let i = 0; i < marks.length; i += 1) {
    const n = Number(marks[i][1]);
    const end = i + 1 < marks.length ? marks[i + 1].index : text.length;
    if (METHOD_ARTICLES.includes(n)) cut.push(n);
    else {
      kept.push(n);
      out += text.slice(marks[i].index, end);
    }
  }
  if (!cut.length) return { cut, kept, relinked: 0 };

  // The file sits one level deeper than it did, and its former siblings moved into method/. A link
  // left as `repo-guide.md` now resolves to .constitution/project/repo-guide.md, which does not exist.
  let relinked = 0;
  const bump = (re, to) => {
    out = out.replace(re, (m, ...rest) => {
      relinked += 1;
      return typeof to === "function" ? to(m, ...rest) : to + m;
    });
  };
  for (const name of ["repo-guide.md", "structure-guide.md", "language-guide.md",
                      "method-glossary.md"]) {
    bump(new RegExp(`(?<![\\w./-])${name.replace(".", "\\.")}`, "g"), "../method/");
  }
  bump(/(?<![\w./-])document\//g, "../method/");
  bump(/(?<![\w./-])codebase\/([a-z]+)-guide\.md/g, (_m, kind) => `codebase-${kind}-guide.md`);
  out = out.replaceAll("../method/../method/", "../method/");

  const banner = [
    "",
    `> **Articles ${cut.join(", ")} were removed from this file on migration to the two-folder layout.**`,
    "> They are the method's and live in [`../method/constitution.md`](../method/constitution.md), which",
    `> \`update\` replaces. Only Articles ${kept.join(", ")} are yours. The removed text is in git.`,
    "",
  ].join("\n");
  const firstArticle = out.search(/^## Article /m);
  out = firstArticle === -1
    ? out + banner
    : out.slice(0, firstArticle) + banner.trimStart() + "\n" + out.slice(firstArticle);

  fs.writeFileSync(file, crlf ? out.replaceAll("\n", "\r\n") : out, "utf8");
  return { cut, kept, relinked };
}

// `waves.yaml` holds the PRODUCT's plan, not the package's. When the method retired `wave` for
// `spec` the registry had to follow, and a rename is the only part of that a tool can safely do:
// the file MOVES, its content is left exactly as written. Rewriting the rows — `W1` to `SPEC-1`,
// `epics`/`stories` to `tickets` — is the product's own migration, run by `wdi-build` where a human
// can see it, because a guess there silently rewrites months of real work.
//
// Two refusals matter more than the move. It never writes over an existing `specs.yaml`, and it
// never deletes a `waves.yaml` whose content has nowhere to go: a half-finished hand migration
// leaves BOTH files present, and which one is real is not something an installer can know.
function migrateRegistryNames(target) {
  const reg = path.join(target, ".control", "registry");
  const from = path.join(reg, "waves.yaml");
  const to = path.join(reg, "specs.yaml");
  if (!fs.existsSync(from)) return false;
  if (fs.existsSync(to)) {
    note("BOTH .control/registry/waves.yaml and specs.yaml exist — neither was touched");
    note("  the plan is in one of them and I cannot tell which. Merge them yourself, then delete waves.yaml");
    return false;
  }
  mv(from, to);
  note("renamed .control/registry/waves.yaml → specs.yaml (content unchanged)");
  note("  the rows still say `W<N>` and `epics`/`stories`. Re-cut them through the wdi-build skill");
  return true;
}

// The requirement registry split into `goals.yaml` (the product's `BG`, written by `wdi-problem` at
// G1) plus one `requirements-<slug>.yaml` per PRD (`CAP`, `FR`, `NFR`, `UJ`, written by
// `wdi-product` at G2). One file, one writer, one gate. What a tool can do here is SEED `goals.yaml`;
// what it MUST NOT do is move the rows.
//
// Splitting the rows needs one fact the registry has never recorded: which PRD an `FR` belongs to.
// Before the split nothing wrote it down, and deriving it — FR → UC → ticket → spec → `prd:` — only
// works for FRs that already have tickets. A guess would file a promise under the wrong initiative,
// which is worse than leaving it where it is. So `requirements.yaml` is left ALONE and still read:
// `validate.py` unions every requirement file it finds, so a half-split corpus stays green while its
// owner cuts the rows through the skill that owns each one.
function seedRequirementSplit(target) {
  const reg = path.join(target, ".control", "registry");
  if (!fs.existsSync(reg)) return false;
  const product = path.join(reg, "goals.yaml");
  if (fs.existsSync(product)) return false;
  const seed = path.join(SCAFFOLD, "registry", "goals.yaml");
  if (!fs.existsSync(seed)) return false;
  copyFile(seed, product);
  note("seeded .control/registry/goals.yaml");
  if (fs.existsSync(path.join(reg, "requirements.yaml"))) {
    note("  requirements.yaml was left exactly as it is, and is still read — nothing broke");
    note("  the wdi-upgrade skill moves `goals:` into goals.yaml and cuts `capabilities:`,");
    note("  `functional:`, `nonfunctional:`, and `journeys:` into requirements-<slug>.yaml per PRD.");
    note("  <slug> is the PRD's folder name under .what/_prd/");
  }
  return true;
}

function migrateToTwoFolders(target) {
  const c = path.join(target, ".constitution");
  if (!fs.existsSync(c)) return false;          // a first install has nothing to migrate
  const at = (...p) => path.join(c, ...p);
  // The old layout is identified by `document/` at the ROOT — in the new layout that folder only ever
  // exists under `method/`. Checking a loose guide instead would misfire on a repo that added one.
  if (!fs.existsSync(at("document")) && !fs.existsSync(at("codebase"))
      && !fs.existsSync(at("constitution.md")) && !fs.existsSync(at("scripts"))) {
    return false;
  }
  note("pre-0.5.0 .constitution/ found — migrating to method/ + project/");

  // 1. The four Reference files go one level deeper. This MUST run before the kit is written, or the
  //    kit's own why/ files land while the old copies still sit at method/ root.
  for (const name of OLD_WHY) {
    const from = at("method", `${name}.md`);
    if (fs.existsSync(from)) {
      mv(from, at("method", "why", `${name}.md`));
      note(`  moved method/${name}.md → method/why/${name}.md`);
    }
  }
  // 2. and 3. whole folders
  for (const dir of ["document", "scripts"]) {
    if (fs.existsSync(at(dir)) && !fs.existsSync(at("method", dir))) {
      mv(at(dir), at("method", dir));
      note(`  moved ${dir}/ → method/${dir}/`);
    }
  }
  // 4. the loose generic guides
  for (const name of OLD_ROOT_GUIDES) {
    const from = at(`${name}.md`);
    if (fs.existsSync(from)) {
      mv(from, at("method", `${name}.md`));
      note(`  moved ${name}.md → method/${name}.md`);
    }
  }
  // 5. codebase/ was a product-owned room all along — it becomes flat files in the room that says so
  for (const name of OLD_CODEBASE) {
    const from = at("codebase", `${name}-guide.md`);
    if (fs.existsSync(from)) {
      mv(from, at("project", `codebase-${name}-guide.md`));
      note(`  moved codebase/${name}-guide.md → project/codebase-${name}-guide.md`);
    }
  }
  if (fs.existsSync(at("codebase"))) {
    const left = fs.readdirSync(at("codebase"));
    if (!left.length) fs.rmdirSync(at("codebase"));
    else note(`  codebase/ still holds ${left.join(", ")} — left in place, move them yourself`);
  }
  // 6. The product's constitution.md moves WHOLE into the room, so its Articles 1, 2, and 5 survive
  //    exactly as written. The generic half then arrives fresh at method/constitution.md.
  let split = null;
  if (fs.existsSync(at("constitution.md")) && !fs.existsSync(at("project", "constitution.md"))) {
    mv(at("constitution.md"), at("project", "constitution.md"));
    note("  moved constitution.md → project/constitution.md");
    split = splitProductConstitution(at("project", "constitution.md"));
    if (split && split.cut.length) {
      note(`    kept Articles ${split.kept.join(", ")}, removed ${split.cut.join(", ")} `
           + "(the method's — they arrive in method/constitution.md)");
      if (split.relinked) note(`    repointed ${split.relinked} relative links one level up`);
    } else if (split === null) {
      note("    it does not carry `## Article N` headings, so it was moved but NOT split — yours to check");
    }
  }
  // Anything else loose at the root is a file this product ADDED. It is NOT moved: it may be routed
  // from AGENTS.md by its current path, and guessing a destination would break that silently.
  const stray = fs.existsSync(c)
    ? fs.readdirSync(c, { withFileTypes: true })
        .filter((e) => e.isFile() && e.name.endsWith(".md"))
        .map((e) => e.name)
    : [];
  if (stray.length) {
    note(`  left at .constitution/ root, yours to place: ${stray.join(", ")}`);
    note("    a file you added belongs in project/ — but moving it would break any pointer that");
    note("    names its current path, so the choice is yours. repo-guide.md states the rule.");
  }
  return split;
}

function syncConstitution(target) {
  const kitConst = path.join(KIT, ".constitution");
  const destConst = path.join(target, ".constitution");
  fs.mkdirSync(destConst, { recursive: true });
  let written = 0;
  let skipped = 0;
  for (const file of walkFiles(kitConst)) {
    const rel = posixRel(kitConst, file);
    const dest = path.join(destConst, rel);
    // ONE rule for everything the product owns, because 0.5.0 put all of it in one folder. Before
    // that this loop had three branches — the mixed constitution.md kept whole, `codebase/` gated on
    // `status: Accepted` (which is what silently destroyed a half-written guide), and the room — and
    // the three disagreed about when a file was the product's. Seeded when absent, never written
    // again: the same rule as the language policy.
    // ONE file in the room is the package's and is refreshed like any method file: the room's own
    // README. It explains what the room is FOR and carries no product decision, so a stale copy does
    // not preserve anybody's work — it just misinforms. worship-presenter-web proved that: its copy
    // still pointed at `.constitution/codebase/*-guide.md`, a folder 0.5.0 deleted, and no update
    // would ever have corrected it while the file claimed in its own text to be "authored in the
    // package". Either the package writes it or it stops claiming authorship; this is the first.
    if (rel === `${PROJECT_ROOM}README.md`) {
      copyFile(file, dest);
      written += 1;
      continue;
    }
    if (rel.startsWith(PROJECT_ROOM) && fs.existsSync(dest)) {
      skipped += 1;
      note(`keep ${rel} (yours — the project room)`);
      continue;
    }
    copyFile(file, dest);
    written += 1;
  }
  return { written, skipped };
}

function syncSkills(target, agents) {
  let n = 0;
  const dests = skillDestinations(target, agents);
  if (dests.length === 0) {
    note("no skill destinations for selected platforms — AGENTS.md still applies");
    return { files: 0, removed: 0 };
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
  const removed = pruneRetiredSkills(dests);
  return { files: n, removed };
}

// A wrapper the method RETIRED is worse than a wrapper missing: the folder is still there, its
// SKILL.md still reads like an instruction, and an agent will invoke it — while the guide it points
// at is gone. Renaming five wrappers (wdi-apply, wdi-analysis, wdi-structure, …) left exactly that
// in every repo installed before the rename, because update only ever touched the names it knows.
//
// `wdi-` is the method's namespace, so a `wdi-*` folder carrying a SKILL.md and not in WDI_SKILLS is
// ours and retired. Each removal is PRINTED: silent deletion in someone else's repo is not a fix.
function pruneRetiredSkills(dests) {
  let removed = 0;
  const keep = new Set(WDI_SKILLS);
  for (const root of dests) {
    if (!fs.existsSync(root)) continue;
    for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
      if (!entry.isDirectory() || !entry.name.startsWith("wdi-") || keep.has(entry.name)) continue;
      const dir = path.join(root, entry.name);
      if (!fs.existsSync(path.join(dir, "SKILL.md"))) {
        note(`kept ${entry.name} (no SKILL.md — not one of ours)`);
        continue;
      }
      fs.rmSync(dir, { recursive: true, force: true });
      note(`removed retired skill ${entry.name}`);
      removed += 1;
    }
  }
  return removed;
}

// `promote` scrubs a product's initiative slug out of bmad-prd.toml before publishing, which is right.
// Writing the scrubbed PLACEHOLDER back into a product repo is not: the first real install replaced a
// live `run_folder_pattern = "some-real-slug"` with `FILL-initiative-slug`, and nothing said so. A value
// the product already chose is not the installer's to overwrite — same rule as the custom room and the
// language policy.
const PLACEHOLDER_SLUG = "FILL-initiative-slug";
const RUN_FOLDER_LINE = /^(\s*run_folder_pattern\s*=\s*)(".*?"|'.*?')/m;

// The slug appears MORE THAN ONCE — bmad-prd.toml carries it in `run_folder_pattern` and again inside a
// memlog path, and the file itself says the two lines MUST change together. The first version of this
// function restored only the first line and so produced exactly the inconsistency that file forbids.
// So: read the product's slug once, then put it back everywhere the placeholder appears.
function keepProductSlug(incoming, existing) {
  const mineNow = existing.match(RUN_FOLDER_LINE);
  if (!mineNow) return null;
  const slug = mineNow[2].slice(1, -1);
  if (!slug || slug === PLACEHOLDER_SLUG) return null;
  if (!incoming.includes(PLACEHOLDER_SLUG)) return null;
  // Only where the slug is a VALUE: the quoted setting, and the memlog path built from it. A bare
  // mention inside a comment stays the placeholder — that sentence explains the pattern, and rewriting
  // it would turn a generic explanation into a statement about one initiative.
  return incoming
    .replaceAll(`"${PLACEHOLDER_SLUG}"`, `"${slug}"`)
    .replaceAll(`prd-${PLACEHOLDER_SLUG}`, `prd-${slug}`);
}

function syncTomls(target) {
  const src = path.join(KIT, "assets", "bmad-custom");
  const dest = path.join(target, "_bmad", "custom");
  fs.mkdirSync(dest, { recursive: true });
  let n = 0;
  let slugsKept = 0;
  for (const file of walkFiles(src)) {
    if (!file.endsWith(".toml") || file.endsWith(".user.toml")) continue;
    const to = path.join(dest, path.basename(file));
    if (fs.existsSync(to)) {
      const merged = keepProductSlug(fs.readFileSync(file, "utf8"), fs.readFileSync(to, "utf8"));
      if (merged !== null) {
        fs.writeFileSync(to, merged);
        note(`kept run_folder_pattern in ${path.basename(file)}`);
        slugsKept += 1;
        n += 1;
        continue;
      }
    }
    copyFile(file, to);
    n += 1;
  }
  return { files: n, slugsKept };
}

// The same argument pruneRetiredSkills makes, one folder over — with one difference that changes
// the rule. `wdi-` is this method's namespace, so "a wdi-* folder not in WDI_SKILLS" is safely ours.
// `_bmad/custom/` is NOT: a product may put its own override there, and `.user.toml` is the
// product's half of every override by convention. So removal here is by an EXPLICIT list of files
// this package once shipped and has now withdrawn — never by "absent from the kit".
//
// Why remove them at all: an override for a retired engine is worse than no override. It is still
// installed and still read, and bmad-retrospective.toml instructs an agent to archive an `RTR-`
// against a validator, V19, that no longer exists.
const RETIRED_TOMLS = [
  "bmad-spec.toml", "bmad-build.toml", "bmad-build-auto.toml",
  "bmad-code-review.toml", "bmad-retrospective.toml",
];

function pruneRetiredTomls(target) {
  const dir = path.join(target, "_bmad", "custom");
  if (!fs.existsSync(dir)) return 0;
  let removed = 0;
  for (const name of RETIRED_TOMLS) {
    const file = path.join(dir, name);
    if (!fs.existsSync(file)) continue;
    fs.rmSync(file);
    note(`removed retired override ${name}`);
    removed += 1;
  }
  return removed;
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

// On a FIRST install these folders are the corpus taking shape. On an UPDATE their absence means
// somebody removed them on purpose — `.work/` and `_bmad-output/prior-knowledge/` are exactly the two a
// product retires once its migration is done, and one repo retired them through an applied decision.
// Recreating them then is an installer overruling a decision it cannot read. Seed once, never resurrect.
function seedEmptyLayers(target, { first }) {
  const always = [".what", path.join(".how", "_platform")];
  const firstOnly = [".work", path.join("_bmad-output", "prior-knowledge")];
  for (const rel of first ? [...always, ...firstOnly] : always) {
    const dest = path.join(target, rel);
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
      note(`created ${rel.replaceAll(path.sep, "/")}/`);
    }
  }
  if (!first) {
    for (const rel of firstOnly) {
      if (!fs.existsSync(path.join(target, rel))) {
        note(`left ${rel.replaceAll(path.sep, "/")}/ absent — a product retires it, not the installer`);
      }
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

function setProductIdentity(target, { name, client }) {
  if (!name || identityIsPlaceholder(name)) return;
  const file = path.join(target, ".control", "registry", "index.yaml");
  if (!fs.existsSync(file)) return;
  const next = writeProductIdentity(fs.readFileSync(file, "utf8"), {
    name,
    client: client ?? "",
  });
  fs.writeFileSync(file, next.endsWith("\n") ? next : `${next}\n`);
  note(`product.name = ${name}`);
}

// The document language belongs to the PRODUCT, so update MUST NOT overwrite it. It is written only
// when absent — same as the custom room, and for the same reason: a setting somebody already chose
// is not the installer's to change behind their back.
function setLanguagePolicy(target, { docLanguage, docFilenameLanguage, chosen }) {
  const file = path.join(target, ".control", "registry", "index.yaml");
  if (!fs.existsSync(file)) return;
  const text = fs.readFileSync(file, "utf8");
  const existing = readLanguagePolicy(text);
  // `chosen` means somebody actually answered — in the TUI, or through an explicit flag. Only then
  // does the answer take effect. Without it the incoming value is just a default, and a default
  // MUST NOT overwrite a choice somebody already made.
  if (!chosen && existing.docLanguage && existing.docFilenameLanguage) {
    note(`kept policy.doc_language = ${existing.docLanguage}, ` +
         `doc_filename_language = ${existing.docFilenameLanguage}`);
    return;
  }
  const next = writeLanguagePolicy(text, {
    docLanguage: docLanguage || existing.docLanguage || DEFAULT_DOC_LANGUAGE,
    docFilenameLanguage:
      docFilenameLanguage || existing.docFilenameLanguage || DEFAULT_DOC_LANGUAGE,
  });
  fs.writeFileSync(file, next.endsWith("\n") ? next : `${next}\n`);
  const after = readLanguagePolicy(next);
  note(`policy.doc_language = ${after.docLanguage}, ` +
       `doc_filename_language = ${after.docFilenameLanguage}`);
}

// After `update`, some of the corpus can still be in the OLD shape — content the installer MUST NOT
// move, because moving it takes a decision about meaning: which PRD an `FR` belongs to, whether a
// sentence was an assumption or a constraint. The `wdi-upgrade` skill does that half. This only
// DETECTS it, cheaply, so the summary can say how much is waiting and where.
function pendingUpgrades(target) {
  const has = (...p) => fs.existsSync(path.join(target, ...p));
  const read = (...p) => (has(...p) ? fs.readFileSync(path.join(target, ...p), "utf8") : "");
  const anyIn = (dir, glob, re) => {
    const d = path.join(target, dir);
    if (!fs.existsSync(d)) return false;
    return fs.readdirSync(d).some((n) => {
      const f = path.join(d, n, glob);
      return fs.existsSync(f) && re.test(fs.readFileSync(f, "utf8"));
    });
  };
  const items = [];
  if (has(".control", "registry", "requirements.yaml")) items.push("requirements.yaml → goals.yaml + requirements-<slug>.yaml");
  if (/^\s*-\s*id:\s*W\d+|^\s*(epics|stories):/m.test(read(".control", "registry", "specs.yaml"))) items.push("specs.yaml rows still W<n>/epics/stories (wdi-build re-cuts)");
  if (/^## (Executive Summary|Vision|Assumptions|Prerequisites)\s*$/m.test(read(".what", "_product-brief", "brief.md"))) items.push("brief.md in the 14-section shape");
  // Sections by NAME: the numbers moved between kits (Non-Goals was §7 in one, §5 in the next).
  if (anyIn(".what/_prd", "prd.md", /^## (\d+\.\s*)?(Document Purpose|Glossary|Non-Goals|Open Questions|Assumptions Index)\b|\*\*Proof of done:\*\*/m)) items.push("a prd.md in the 12-section shape, or with FR blocks");
  const whatDir = path.join(target, ".what");
  if (fs.existsSync(whatDir)) {
    for (const pc of fs.readdirSync(whatDir)) {
      if (pc.startsWith("_")) continue;
      const srs = read(".what", pc, `SRS-${pc}.md`);
      if (/^\|\s*UC-\d+\s*\|/m.test(srs)) { items.push("an SRS with a UC Catalogue table (now a pointer)"); break; }
    }
  }
  const howDir = path.join(target, ".how");
  if (fs.existsSync(howDir)) {
    for (const pc of fs.readdirSync(howDir)) {
      if (pc.startsWith("_")) continue;
      if (/\|\s*Quoted rule\s*\||Quoted verbatim from/.test(read(".how", pc, `SDD-${pc}.md`))) { items.push("an SDD quoting AD-N text (now ids only)"); break; }
    }
  }
  if (/\|\s*Container\s*\|\s*Product Components living in it\s*\|/.test(read(".how", "_platform", "c4-l2-containers.md"))) items.push("c4-l2 with a PC x container table (now a pointer)");
  if (has(".control", "generated", "brief.md") || has(".control", "generated", "blueprint.md")) items.push("human pages still in .control/generated/ (render clears them)");
  if (has(".what", "_product-brief", "brief.md") && !has(".what-rendered")) items.push("no .what-rendered/ yet (render creates it)");
  // Skipped: what the validator never reads (kit copies, rendered output, dependencies) and what it
  // treats as a record of the PAST — memlog, decisions, reports, _bmad-output. A stale path in a log
  // is history, not a finding, and repointing it would falsify the record.
  const SKIP = new Set([".git", "node_modules", "target", ".constitution", ".claude", ".agents", ".agent",
    ".what-rendered", ".how-rendered", "dist", "build", "memlog", "decisions", "reports", "meetings", "_bmad-output", ".work"]);
  const OLD_PAGE = /\.control\/generated\/(brief|blueprint|prd-[a-z0-9-]+)\.md/;
  const citesOldPage = (dir, depth) => {
    if (depth > 8) return false;
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.isDirectory()) { if (!SKIP.has(e.name) && citesOldPage(path.join(dir, e.name), depth + 1)) return true; continue; }
      if (e.name === "answered.md") continue;
      if (e.name.endsWith(".md") && OLD_PAGE.test(fs.readFileSync(path.join(dir, e.name), "utf8"))) return true;
    }
    return false;
  };
  if (citesOldPage(target, 0)) items.push("a document cites .control/generated/brief|blueprint|prd-*.md (pages moved to the rendered trees)");
  return items;
}

// Read BEFORE writeStamp overwrites it. Without this there is no version transition to print, and
// an "updated" with no from-to tells the reader nothing they can use.
function readStampVersion(target) {
  const file = path.join(target, ".control", "wdi-method.yaml");
  if (!fs.existsSync(file)) return "";
  const m = fs.readFileSync(file, "utf8").match(/^wdi_method:\s*"?([^"\s]+)"?/m);
  return m ? m[1] : "";
}

function readIndexPolicy(target) {
  const file = path.join(target, ".control", "registry", "index.yaml");
  if (!fs.existsSync(file)) return { docLanguage: "", docFilenameLanguage: "" };
  return readLanguagePolicy(fs.readFileSync(file, "utf8"));
}

function readIndexIdentity(target) {
  const file = path.join(target, ".control", "registry", "index.yaml");
  if (!fs.existsSync(file)) return { name: "", client: "" };
  return readProductIdentity(fs.readFileSync(file, "utf8"));
}

function upsertAgentFiles(target, platforms, productName) {
  const template = fs.readFileSync(path.join(OVERLAY, "AGENTS.md"), "utf8");
  const agentsFile = path.join(target, "AGENTS.md");
  let next;
  if (!fs.existsSync(agentsFile)) {
    next = fillProductTitle(template, productName || "{product}");
    ok("AGENTS.md created — rewrite ## Code for this product");
  } else {
    next = upsertMethodBlock(fs.readFileSync(agentsFile, "utf8"), template);
    note("AGENTS.md method block refreshed; product sections kept");
  }
  if (!next.endsWith("\n")) next += "\n";
  fs.writeFileSync(agentsFile, next);

  const mirrors = [];
  if (platformUsesHook(platforms, "cursorrules")) {
    mirrors.push(path.join(target, ".cursorrules"));
  }
  if (platformUsesHook(platforms, "agents-mirror")) {
    mirrors.push(path.join(target, ".agents", "AGENTS.md"));
  }
  for (const mirror of mirrors) {
    fs.mkdirSync(path.dirname(mirror), { recursive: true });
    if (fs.existsSync(mirror)) {
      const patched = upsertMethodBlock(fs.readFileSync(mirror, "utf8"), template);
      fs.writeFileSync(mirror, patched.endsWith("\n") ? patched : `${patched}\n`);
      note(`method block refreshed in ${posixRel(target, mirror)}`);
    } else {
      fs.writeFileSync(mirror, next);
      note(`created ${posixRel(target, mirror)}`);
    }
  }

  if (platformUsesHook(platforms, "claude-md")) {
    const claude = path.join(target, "CLAUDE.md");
    if (!fs.existsSync(claude)) {
      fs.writeFileSync(claude, "@AGENTS.md\n");
      note("CLAUDE.md created as @AGENTS.md");
    }
  }
}

// What a run MUST leave a reader able to answer: which version replaced which, what was written, what
// was KEPT, and what to do next. The third is the one usually missing, and it is the one that decides
// whether somebody trusts running this over a repo they have already put work into.
function summaryLine(label, value) {
  console.log(`  ${DIM}${label.padEnd(11)}${RESET}${value}`);
}

function printSummary(target, agents, { first, was, written, skipped, skills, tomls, opencodeCmds }) {
  const now = PKG.version;
  const version = first
    ? `${now} — first install`
    : was && was !== now
      ? `${was} ${DIM}→${RESET} ${now}`
      : `${now} ${DIM}(unchanged)${RESET}`;
  const bmad = readBmadVersion(target);

  const kept = [];
  if (skipped) kept.push(`${skipped} constitution file${skipped === 1 ? "" : "s"}`);
  if (tomls.slugsKept) kept.push(`${tomls.slugsKept} initiative slug${tomls.slugsKept === 1 ? "" : "s"}`);
  // On a first install the language was just CHOSEN, not kept — saying "kept" there reads as if the
  // installer had found something it decided to leave alone, which is the opposite of what happened.
  const policy = readIndexPolicy(target);
  if (policy.docLanguage && !first) kept.push(`language (${policy.docLanguage})`);
  if (fs.existsSync(path.join(target, ".constitution", "project"))) kept.push(".constitution/project/");

  console.log("");
  console.log(`${DIM}────${RESET} WDI Method ${DIM}${"─".repeat(46)}${RESET}`);
  summaryLine("version", version);
  if (bmad) summaryLine("bmad", bmad);
  summaryLine("target", target);
  console.log("");
  summaryLine("written", `${written} constitution · ${skills.files} skill files · ${tomls.files} bmad overrides`
    + (opencodeCmds?.written ? ` · ${opencodeCmds.written} opencode commands` : ""));
  if (kept.length) summaryLine("kept", kept.join(" · "));
  const gone = [];
  if (skills.removed) gone.push(`${skills.removed} retired wrapper${skills.removed === 1 ? "" : "s"}`);
  if (tomls.removed) gone.push(`${tomls.removed} retired override${tomls.removed === 1 ? "" : "s"}`);
  if (gone.length) summaryLine("removed", gone.join(" · "));
  if (first && policy.docLanguage) {
    summaryLine("language", `${policy.docLanguage} · filenames ${policy.docFilenameLanguage}`);
  }
  summaryLine("platforms", agents.join(", ") || "none");
  console.log("");
  // The readers are the one seeded file that does nothing until somebody writes it, and its
  // silence is expensive: inventory.py refuses to run and the reason is a folder deep. One line
  // here, only while it is still the skeleton, so it stops appearing once it is done.
  if (readersAreSkeleton(target)) {
    summaryLine("todo", `${DIM}.constitution/project/inventory-readers.py${RESET} is a skeleton — ` +
                        `run the ${INIT_SKILL} skill, intent ${DIM}readers${RESET}, ` +
                        `to write it for this repo's stack`);
  }
  summaryLine("engines", enginesPresent(target)
    ? `to-spec · to-tickets · implement — found (${ENGINES_PLUGIN})`
    : `to-spec · to-tickets · implement — NOT found. G5 (wdi-build) and the Fast Path need them; G1–G4 run without them`);
  if (!enginesPresent(target)) {
    summaryLine("", `${DIM}·${RESET} Claude Code: ${DIM}${ENGINES_INSTALL}${RESET} — other agents: ${DIM}${ENGINES_INSTALL_ANY}${RESET}`);
    summaryLine("", `${DIM}·${RESET} then ${DIM}${ENGINES_SETUP}${RESET} once, to name the tracker · ${ENGINES_REPO}`);
  }
  const pending = first ? [] : pendingUpgrades(target);
  if (pending.length) {
    summaryLine("upgrade", `${pending.length} item${pending.length === 1 ? "" : "s"} still in the OLD shape — ` +
                           `run the ${DIM}wdi-upgrade${RESET} skill; it moves content, never invents it`);
    for (const item of pending) summaryLine("", `${DIM}·${RESET} ${item}`);
  }
  summaryLine("next", pending.length
    ? `run the ${DIM}wdi-upgrade${RESET} skill first, then ${HELP_SKILL}`
    : `invoke the ${HELP_SKILL} skill and ask what to do`);
  summaryLine("", REPO_URL);
  console.log(`${DIM}${"─".repeat(62)}${RESET}`);
}

function printNextSteps({ first, productSet, upgradePending }) {
  console.log("");
  console.log(first ? "After install:" : "After update:");
  if (first) {
    if (!productSet) {
      console.log("  1. Fill product.name (and product.client if there is one) in .control/registry/index.yaml.");
    } else {
      console.log("  1. product.name is set. G1 confirms it in the brief.");
    }
    console.log("  2. Rewrite .constitution/constitution.md Articles 2 and 5 for this product.");
    console.log("     Article 1 cites index.yaml — do not become a second source for the name.");
    console.log("  3. Write ## Code in AGENTS.md (where the app lives). Leave the BEGIN:wdi-method block alone.");
    console.log("  4. Run the wdi-init skill, intent setup.");
    console.log("  5. Sort the documents you already have. Do not move any of them in this step.");
    console.log("");
    console.log("Next update:");
    console.log("  npx wdi-method");
    console.log("  (the TUI offers the update)  or:  npx wdi-method update --yes");
  } else {
    console.log("  1. The <!-- BEGIN:wdi-method --> block in AGENTS.md was replaced. Read the diff.");
    console.log("  2. constitution.md Articles 1-2-5, ## Code, and *.user.toml were not overwritten.");
    console.log("  3. If BMad has new skills, install those first, then run this update again.");
    if (upgradePending) {
      console.log("  4. The summary listed an `upgrade` line: run the wdi-upgrade skill before any other skill.");
      console.log("     It moves content into the new shape and never invents any; one commit.");
    }
  }
}

function apply(target, agents,
               { first, product, client, docLanguage, docFilenameLanguage, languageChosen }) {
  requireKit();
  const was = readStampVersion(target);
  // MUST run before the kit is written: it moves the product's files out of the way of paths the kit
  // is about to occupy. Running it after would leave two copies of most guides.
  const migrated = migrateToTwoFolders(target);
  migrateRegistryNames(target);
  seedRequirementSplit(target);
  // The split MUST also be reachable without a migration. 0.5.2 only ran it from inside
  // migrateToTwoFolders, which returns early when the old layout is absent — so a repo that took
  // 0.5.0 or 0.5.1, whose project/constitution.md was moved WHOLE and never split, could never be
  // fixed by any later update. That is precisely the repo that needs it. Running it here on every
  // update closes that, and it is idempotent: after a split there are no method articles left to cut.
  const lateSplit = splitProductConstitution(path.join(target, ".constitution", "project",
                                                       "constitution.md"));
  if (!migrated && lateSplit && lateSplit.cut.length) {
    note(`project/constitution.md still carried Articles ${lateSplit.cut.join(", ")} — removed`);
    note(`  they are the method's and live in method/constitution.md; kept ${lateSplit.kept.join(", ")}`);
    if (lateSplit.relinked) note(`  repointed ${lateSplit.relinked} relative links`);
  }
  const splitConstitution = migrated;
  const { written, skipped } = syncConstitution(target);
  note(`constitution wrote ${written}, kept ${skipped}`);
  // A migrated repo also carries derived output stamped against the OLD layout: .control/generated/*
  // still names the pre-0.5.0 script path, and the two structure maps still draw the old tree. The
  // installer MUST NOT write either — one is generated, the other is re-derived by a skill — so it
  // says so instead of leaving them to be found by whoever trusts them next.
  if (splitConstitution) {
    note("  derived output still describes the OLD layout, and neither is mine to write:");
    note("    uv run .constitution/method/scripts/validate.py --generate   → .control/generated/");
    note("    then the wdi-init skill, intent `structure`                  → the two structure maps");
  }
  const skills = syncSkills(target, agents);
  note(`skills ${skills.files} files`);
  let opencodeCmds = { written: 0, removed: 0 };
  if (platformUsesHook(agents, "opencode-commands")) {
    opencodeCmds = syncOpencodeCommands(target, WDI_SKILLS, path.join(KIT, "skills"));
    note(`opencode commands ${opencodeCmds.written} files → ${opencodeCommandsDir()}/`);
    if (opencodeCmds.removed) {
      note(`removed ${opencodeCmds.removed} retired opencode command${opencodeCmds.removed === 1 ? "" : "s"}`);
    }
  }
  const tomls = syncTomls(target);
  tomls.removed = pruneRetiredTomls(target);
  note(`bmad custom ${tomls.files} toml → _bmad/custom/`);
  if (first) seedControlIfMissing(target);
  seedEmptyLayers(target, { first });
  setProductIdentity(target, { name: product, client });
  setLanguagePolicy(target, { docLanguage, docFilenameLanguage, chosen: languageChosen });
  upsertAgentFiles(target, agents, product);
  writeStamp(target);
  printSummary(target, agents, { first, was, written, skipped, skills, tomls, opencodeCmds });
  printNextSteps({
    first,
    productSet: Boolean(product) && !identityIsPlaceholder(product),
    upgradePending: !first && pendingUpgrades(target).length > 0,
  });
}

function verify(target, agents) {
  requireKit();
  const missing = [];
  const kitConst = path.join(KIT, ".constitution");
  for (const file of walkFiles(kitConst)) {
    const rel = posixRel(kitConst, file);
    const dest = path.join(target, ".constitution", rel);
    if (!fs.existsSync(dest)) missing.push(`.constitution/${rel}`);
  }
  for (const name of WDI_SKILLS) {
    for (const root of skillDestinations(target, agents)) {
      const dest = path.join(root, name, "SKILL.md");
      if (!fs.existsSync(dest)) missing.push(posixRel(target, dest));
    }
  }
  if (platformUsesHook(agents, "opencode-commands")) {
    for (const name of WDI_SKILLS) {
      const dest = path.join(target, opencodeCommandsDir(), `${name}.md`);
      if (!fs.existsSync(dest)) missing.push(posixRel(target, dest));
    }
  }
  const custom = path.join(KIT, "assets", "bmad-custom");
  for (const file of walkFiles(custom)) {
    if (!file.endsWith(".toml")) continue;
    const dest = path.join(target, "_bmad", "custom", path.basename(file));
    if (!fs.existsSync(dest)) missing.push(`_bmad/custom/${path.basename(file)}`);
  }
  if (fs.existsSync(path.join(target, ".control"))) {
    for (const file of walkFiles(SCAFFOLD)) {
      const rel = posixRel(SCAFFOLD, file);
      const dest = path.join(target, ".control", rel);
      if (!fs.existsSync(dest)) missing.push(`.control/${rel}`);
    }
  } else {
    missing.push(".control/ (folder missing — first install should have seeded it)");
  }
  // `.constitution/constitution.md` was the pre-0.5.0 path. Demanding it here made `verify` report a
  // file MISSING that the split deliberately removed — a check telling the truth about the wrong world.
  for (const required of ["AGENTS.md", path.join(".constitution", "project", "constitution.md")]) {
    if (!fs.existsSync(path.join(target, required))) missing.push(required.replaceAll(path.sep, "/"));
  }
  if (missing.length) {
    console.error(`${RED}missing ${missing.length}${RESET}`);
    for (const m of missing) console.error(`  ${m}`);
    process.exit(1);
  }
  ok(`method files present in ${target}`);

  // Present-and-correct is not the same as consistent. These three are states `update` cannot fix on
  // its own — it MUST NOT write over the room, and it cannot know what a product meant — so `verify`
  // is where they get said out loud instead of waiting to be tripped over.
  const judgement = [];
  const room = path.join(target, ".constitution", "project", "constitution.md");
  if (fs.existsSync(room)) {
    const carried = [...fs.readFileSync(room, "utf8").matchAll(/^## Article (\d+)\b/gm)]
      .map((m) => Number(m[1])).filter((n) => METHOD_ARTICLES.includes(n));
    if (carried.length) {
      judgement.push(`project/constitution.md still carries Articles ${carried.join(", ")} — the `
        + "method's. They are duplicated in method/constitution.md and will drift. Run update again.");
    }
  }
  const constRoot = path.join(target, ".constitution");
  const loose = fs.existsSync(constRoot)
    ? fs.readdirSync(constRoot, { withFileTypes: true })
        .filter((e) => e.isFile() && e.name.endsWith(".md")).map((e) => e.name)
    : [];
  if (loose.length) {
    judgement.push(`loose at .constitution/ root: ${loose.join(", ")} — .constitution/ holds two `
      + "folders and nothing else the method knows about. Move it into project/, or name it from "
      + "Article 2 so the next reader knows why it is there. repo-guide.md states the rule.");
  }
  if (judgement.length) {
    console.log("");
    for (const j of judgement) note(j);
  }
  note("extra product files are expected and were not checked");
}

function scrubPrdToml(file) {
  const raw = fs.readFileSync(file, "utf8");
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
  // EVERY file in the room is authored in the package and MUST survive the rmSync below — the room's
  // README, the generic Articles 1-2-5, and the three empty codebase templates. Read here, not
  // after: the first version of this preserved only README.md and read it AFTER the kit was deleted,
  // so it was always null and the file vanished on every promote. Two tests cover it now.
  const roomKit = path.join(KIT, ".constitution", PROJECT_ROOM);
  const roomKept = fs.existsSync(roomKit)
    ? Object.fromEntries(walkFiles(roomKit).map((f) => [posixRel(roomKit, f), fs.readFileSync(f, "utf8")]))
    : {};

  fs.rmSync(KIT, { recursive: true, force: true });
  fs.mkdirSync(KIT, { recursive: true });

  // ONE skip, because 0.5.0 put everything the product owns in one folder. It covers the codebase
  // guides too, which used to need a rule of their own: promoting a filled-in stack guide would leak
  // one product's conventions — possibly written in its own `doc_language` — into a public package.
  const nConst = copyTree(path.join(live, ".constitution"), path.join(KIT, ".constitution"),
                          (rel) => rel.startsWith(PROJECT_ROOM));
  note(`constitution ${nConst} files (${PROJECT_ROOM} skipped — it is the product's)`);
  for (const [rel, text] of Object.entries(roomKept)) {
    const dest = path.join(roomKit, rel);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.writeFileSync(dest, text, "utf8");
  }
  if (Object.keys(roomKept).length) {
    note(`${PROJECT_ROOM} restored from the package (${Object.keys(roomKept).length} files) — `
         + "promote never carries the room home");
  }

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
    for (const file of walkFiles(customSrc)) {
      if (!file.endsWith(".toml") || file.endsWith(".user.toml")) continue;
      copyFile(file, path.join(customDst, path.basename(file)));
      tomls += 1;
    }
  }
  const prd = path.join(customDst, "bmad-prd.toml");
  if (fs.existsSync(prd)) scrubPrdToml(prd);
  note(`bmad custom ${tomls} toml`);

  const replacements = {
    "constitution.md": path.join(KIT, ".constitution", "method", "constitution.md"),
    "portability.md": path.join(KIT, ".constitution", "method", "why", "portability.md"),
    "repo-guide.md": path.join(KIT, ".constitution", "method", "repo-guide.md"),
    "README.md": path.join(KIT, ".constitution", "method", "README.md"),
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

function cancelIf(value) {
  if (p.isCancel(value)) {
    p.cancel("Cancelled.");
    process.exit(0);
  }
  return value;
}

async function runWizard(pre) {
  p.intro(`WDI Method ${PKG.version}`);

  const dirValue = cancelIf(
    await p.text({
      message: "Target repo (the product folder)",
      placeholder: process.cwd(),
      defaultValue: pre.dir || process.cwd(),
    }),
  );
  const target = path.resolve(String(dirValue).trim() || process.cwd());

  if (!fs.existsSync(target)) {
    const create = cancelIf(
      await p.confirm({ message: `${target} does not exist. Create it?`, initialValue: true }),
    );
    if (!create) {
      p.cancel("No target folder.");
      process.exit(1);
    }
    fs.mkdirSync(target, { recursive: true });
  }

  const hasBmad = bmadPresent(target);
  const hasWdi = wdiPresent(target);
  const nonempty = dirNonEmpty(target);

  const facts = [
    hasBmad
      ? `BMad Method: installed${readBmadVersion(target) ? ` (${readBmadVersion(target)})` : ""}`
      : "BMad Method: not installed",
    hasWdi ? "WDI Method: already present — the installer will offer an update" : "WDI Method: not present",
    enginesPresent(target)
      ? "Ticket engines (mattpocock-skills): installed"
      : `Ticket engines (mattpocock-skills): not found — needed at G5 only; ${ENGINES_INSTALL} (${ENGINES_REPO})`,
    nonempty ? "Folder is not empty (normal for a product repo already under way)" : "Folder is empty",
  ].join("\n");
  p.note(facts, "Detected");

  if (!hasBmad && !pre.skipBmad) {
    p.note(bmadMissingMessage(), "BMad first");
    p.outro("Install BMad, then run this again: npx wdi-method");
    process.exit(1);
  }

  let first = !hasWdi;
  if (hasWdi) {
    const update = cancelIf(
      await p.confirm({
        message: "WDI Method is already installed. Update it now?",
        initialValue: true,
      }),
    );
    first = !update;
    if (first) {
      p.cancel("Update declined.");
      process.exit(0);
    }
  } else {
    const go = cancelIf(
      await p.confirm({
        message: `Install WDI Method into ${target}?`,
        initialValue: true,
      }),
    );
    if (!go) {
      p.cancel("Install declined.");
      process.exit(0);
    }
  }

  // Every field arrives with an answer already in it, and Enter accepts it. On an update that answer is
  // what the repo already says; on a first install it is the folder name made readable. Nothing here is
  // validated as required: a prompt that refuses an empty submission when it already holds a sensible
  // default is asking the owner to retype something the installer knows.
  const existing = readIndexIdentity(target);
  const suggestedName = identityIsPlaceholder(existing.name)
    ? humaniseFolderName(path.basename(target))
    : existing.name;
  const product = cancelIf(
    await p.text({
      message: "Product name (one room: index.yaml product.name)",
      placeholder: suggestedName,
      defaultValue: suggestedName,
    }),
  ).trim() || suggestedName;
  const client = cancelIf(
    await p.text({
      message: "Client name (Enter to leave it as it is)",
      placeholder: existing.client || "(none)",
      defaultValue: existing.client || "",
    }),
  ).trim();

  // Two questions, and only two. Method terminology, document code prefixes, machine-facing
  // markers, and code identifiers are always English — MUST NOT be asked about.
  const policy = readIndexPolicy(target);
  // Free text, not a list. Write whatever a model understands — "English", "Bahasa Indonesia",
  // "id". The only value refused is empty.
  const askLanguage = async (message, current) =>
    (cancelIf(
      await p.text({
        message,
        placeholder: current || DEFAULT_DOC_LANGUAGE,
        defaultValue: current || DEFAULT_DOC_LANGUAGE,
      }),
    ) || DEFAULT_DOC_LANGUAGE).trim();
  const docLanguage = await askLanguage(
    "Language of working-document prose (.what/ .how/ .control/) — free text",
    policy.docLanguage || pre.docLanguage);
  const docFilenameLanguage = await askLanguage(
    "Language of document filename slugs — the `UC-` `DEC-` codes stay English",
    policy.docFilenameLanguage || pre.docFilenameLanguage || docLanguage);

  const detected = pre.agents
    ? normalizePlatformIds(pre.agents)
    : detectPlatforms(target, fs);
  const selected = cancelIf(
    await p.autocompleteMultiselect({
      message: "Which tools get the wdi-* skills? (⭐ = recommended)",
      options: platformSelectOptions(detected),
      initialValues: detected,
      required: true,
      maxItems: 8,
      placeholder: "Type to search…",
    }),
  );

  p.note(
    [
      "The corpus folder names are fixed — they are not an install option:",
      "  .constitution  .control  .what  .how  .work  _bmad-output",
      "",
      "What gets written for the platforms you picked:",
      "  AGENTS.md  (the BEGIN:wdi-method block — always)",
      platformUsesHook(selected, "claude-md") ? "  CLAUDE.md  →  @AGENTS.md" : "",
      platformUsesHook(selected, "cursorrules") ? "  .cursorrules  (method block mirror)" : "",
      platformUsesHook(selected, "agents-mirror") ? "  .agents/AGENTS.md  (method block mirror)" : "",
      platformUsesHook(selected, "opencode-commands")
        ? `  ${opencodeCommandsDir()}/wdi-*.md  (slash commands → skills)`
        : "",
      `  wdi-* skills  →  ${skillDestinations(target, selected).map((d) => posixRel(target, d)).join(", ") || "(none)"}`,
    ]
      .filter(Boolean)
      .join("\n"),
    "Write targets",
  );

  const okGo = cancelIf(await p.confirm({ message: first ? "Run the install?" : "Run the update?", initialValue: true }));
  if (!okGo) {
    p.cancel("Dibatalkan.");
    process.exit(0);
  }

  const spinner = p.spinner();
  spinner.start(first ? "Memasang…" : "Meng-update…");
  apply(target, selected, {
    docLanguage,
    docFilenameLanguage,
    languageChosen: true,
    first,
    product: String(product).trim(),
    client: String(client).trim(),
  });
  spinner.stop(first ? "Terpasang" : "Ter-update");
  p.outro(first ? "Done. Take the after-install steps above." : "Done. Read the method-block diff in AGENTS.md.");
}

function runNonInteractive(args) {
  const target = requireTarget(args.dir);
  const agents = args.agents || detectPlatforms(target, fs) || PREFERRED_PLATFORM_IDS.slice();
  if (args.cmd === "verify") {
    verify(target, agents);
    return;
  }
  if (!args.skipBmad && !bmadPresent(target)) {
    die(bmadMissingMessage());
  }
  const existing = readIndexIdentity(target);
  const product = args.product || existing.name;
  const client = args.client ?? existing.client;
  const first = args.cmd === "install" || (args.cmd === "wizard" && !wdiPresent(target));
  apply(target, agents, {
    first: args.cmd === "update" ? false : first,
    product,
    client,
    docLanguage: args.docLanguage,
    docFilenameLanguage: args.docFilenameLanguage,
    languageChosen: Boolean(args.docLanguage || args.docFilenameLanguage),
  });
}

async function main() {
  const args = parseArgs(process.argv);
  if (!["wizard", "install", "update", "verify", "promote"].includes(args.cmd)) {
    usage();
    process.exit(2);
  }
  if (args.cmd === "promote") {
    if (!args.dir) die("promote needs a path to the working copy");
    // `promote` used to BE the workflow: author a rule in a product repo, run it, carry it here.
    // It is now a rescue tool, and the flag is what makes that structural rather than a paragraph
    // nobody rereads. Running it by habit overwrites the whole kit with one consumer's copy —
    // silently reverting every change made here since that repo last updated.
    if (!args.rescue) {
      die([
        "promote overwrites the whole kit from a consumer's copy, and this package is now where a",
        "       method change is authored — see CONTRIBUTING.md. If a change really was made in a",
        "       product repo by mistake and needs rescuing, say so:",
        "",
        "         npx wdi-method promote <dir> --rescue",
      ].join("\n"));
    }
    note("--rescue: pulling the method back out of a consumer. Read the diff before committing.");
    promote(args.dir);
    return;
  }
  const wantTui = !args.yes && args.cmd !== "verify" && process.stdin.isTTY && process.stdout.isTTY;
  if (wantTui) {
    await runWizard(args);
    return;
  }
  if (args.cmd === "wizard" && !args.yes) {
    die("not a TTY. Use `install --yes` / `update --yes`, or run this in a terminal.");
  }
  if (args.cmd === "wizard") args.cmd = wdiPresent(requireTarget(args.dir)) ? "update" : "install";
  runNonInteractive(args);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

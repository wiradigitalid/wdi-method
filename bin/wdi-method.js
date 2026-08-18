#!/usr/bin/env node
import fs from "node:fs";
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
  readProductIdentity,
  writeProductIdentity,
} from "../lib/identity.mjs";

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
const AGENT_LABELS = {
  claude: "Claude Code  →  .claude/skills, CLAUDE.md",
  cursor: "Cursor       →  .agents/skills, .cursorrules",
  codex: "Codex        →  AGENTS.md",
  antigravity: "Antigravity  →  .agents/skills, .agents/AGENTS.md",
};

const BMAD_INSTALL = `npx bmad-method install`;
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
  promote <live-dir>

  --yes                     non-interactive
  --agents a,b              claude,cursor,codex,antigravity
  --product NAME            written to index.yaml product.name
  --client NAME             written to index.yaml product.client (optional)
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
    yes: false,
    product: null,
    client: null,
  };
  const rest = argv.slice(2);
  if (rest[0] === "-h" || rest[0] === "--help") {
    usage();
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
    else if (t === "--yes" || t === "-y") args.yes = true;
    else if (t === "--agents") {
      const raw = rest.shift();
      if (!raw) die("--agents needs a comma-separated list");
      args.agents = raw.split(",").map((s) => s.trim()).filter(Boolean);
      for (const a of args.agents) {
        if (!ALL_AGENTS.includes(a)) die(`unknown agent: ${a}`);
      }
    } else if (t === "--product") args.product = rest.shift();
    else if (t === "--client") args.client = rest.shift();
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

function detectAgents(target) {
  const found = [];
  if (
    fs.existsSync(path.join(target, ".claude", "skills", "wdi-init", "SKILL.md")) ||
    fs.existsSync(path.join(target, ".claude", "skills", "bmad-help", "SKILL.md"))
  ) {
    found.push("claude");
  }
  if (
    fs.existsSync(path.join(target, ".cursorrules")) ||
    fs.existsSync(path.join(target, ".agents", "skills", "wdi-init", "SKILL.md"))
  ) {
    found.push("cursor");
  }
  if (fs.existsSync(path.join(target, "AGENTS.md"))) found.push("codex");
  if (fs.existsSync(path.join(target, ".agents", "AGENTS.md"))) found.push("antigravity");
  return found.length ? [...new Set(found)] : ALL_AGENTS.slice();
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

function bmadMissingMessage() {
  return [
    "BMad Method belum terpasang di repo ini. Pasang dulu, lalu jalankan installer ini lagi.",
    "",
    `  ${BMAD_INSTALL}`,
    "",
    `Sumber: ${BMAD_REPO}`,
    "Di installer BMad, pilih agen yang sama (Claude Code, Cursor, …).",
  ].join("\n");
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
    copyFile(file, dest);
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
  for (const file of walkFiles(src)) {
    if (!file.endsWith(".toml") || file.endsWith(".user.toml")) continue;
    copyFile(file, path.join(dest, path.basename(file)));
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
    const dest = path.join(target, rel);
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
      note(`created ${rel.replaceAll(path.sep, "/")}/`);
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

function readIndexIdentity(target) {
  const file = path.join(target, ".control", "registry", "index.yaml");
  if (!fs.existsSync(file)) return { name: "", client: "" };
  return readProductIdentity(fs.readFileSync(file, "utf8"));
}

function upsertAgentFiles(target, agents, productName) {
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
  if (agents.includes("cursor")) mirrors.push(path.join(target, ".cursorrules"));
  if (agents.includes("cursor") || agents.includes("antigravity")) {
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

  if (agents.includes("claude")) {
    const claude = path.join(target, "CLAUDE.md");
    if (!fs.existsSync(claude)) {
      fs.writeFileSync(claude, "@AGENTS.md\n");
      note("CLAUDE.md created as @AGENTS.md");
    }
  }
}

function printNextSteps({ first, productSet }) {
  console.log("");
  console.log(first ? "Sesudah install:" : "Sesudah update:");
  if (first) {
    if (!productSet) {
      console.log("  1. Isi product.name (dan product.client bila ada) di .control/registry/index.yaml.");
    } else {
      console.log("  1. product.name sudah diisi. G1 nanti mengonfirmasinya di brief.");
    }
    console.log("  2. Tulis ulang .constitution/constitution.md Pasal 2 dan 5 untuk produk ini.");
    console.log("     Pasal 1 mengutip index.yaml — jangan jadi sumber nama kedua.");
    console.log("  3. Tulis ## Code di AGENTS.md (akar aplikasi). Blok BEGIN:wdi-method jangan diedit.");
    console.log("  4. Jalankan skill wdi-init intent setup.");
    console.log("  5. Pilah dokumen lama. Jangan dipindah di langkah ini.");
    console.log("");
    console.log("Update berikutnya:");
    console.log("  npx github:wiradigitalid/wdi-method");
    console.log("  (TUI akan menawarkan update)  atau:  npx github:wiradigitalid/wdi-method update --yes");
  } else {
    console.log("  1. Blok <!-- BEGIN:wdi-method --> di AGENTS.md sudah diganti. Cek diff-nya.");
    console.log("  2. Pasal 1–2–5 constitution.md, ## Code, dan *.user.toml tidak ditimpa.");
    console.log("  3. Kalau ada skill BMad baru, pasang dulu lewat installer BMad, lalu update ini lagi.");
  }
}

function apply(target, agents, { first, product, client }) {
  requireKit();
  const { written, skipped } = syncConstitution(target);
  note(`constitution wrote ${written}, kept ${skipped}`);
  const nSkills = syncSkills(target, agents);
  note(`skills ${nSkills} files`);
  const nToml = syncTomls(target);
  note(`bmad custom ${nToml} toml → _bmad/custom/`);
  if (first) seedControlIfMissing(target);
  seedEmptyLayers(target);
  setProductIdentity(target, { name: product, client });
  upsertAgentFiles(target, agents, product);
  writeStamp(target);
  ok(`${first ? "installed" : "updated"} into ${target}`);
  printNextSteps({
    first,
    productSet: Boolean(product) && !identityIsPlaceholder(product),
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
    for (const root of skillDests(target, agents)) {
      const dest = path.join(root, name, "SKILL.md");
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

function cancelIf(value) {
  if (p.isCancel(value)) {
    p.cancel("Dibatalkan.");
    process.exit(0);
  }
  return value;
}

async function runWizard(pre) {
  p.intro(`WDI Method ${PKG.version}`);

  const dirValue = cancelIf(
    await p.text({
      message: "Repo tujuan (folder produk)",
      placeholder: process.cwd(),
      defaultValue: pre.dir || process.cwd(),
    }),
  );
  const target = path.resolve(String(dirValue).trim() || process.cwd());

  if (!fs.existsSync(target)) {
    const create = cancelIf(
      await p.confirm({ message: `${target} belum ada. Buat folder?`, initialValue: true }),
    );
    if (!create) {
      p.cancel("Tidak ada folder tujuan.");
      process.exit(1);
    }
    fs.mkdirSync(target, { recursive: true });
  }

  const hasBmad = bmadPresent(target);
  const hasWdi = wdiPresent(target);
  const nonempty = dirNonEmpty(target);

  const facts = [
    hasBmad
      ? `BMad Method: terpasang${readBmadVersion(target) ? ` (${readBmadVersion(target)})` : ""}`
      : "BMad Method: belum terpasang",
    hasWdi ? "WDI Method: sudah ada — installer akan menawarkan update" : "WDI Method: belum ada",
    nonempty ? "Folder tidak kosong (repo produk yang sudah jalan itu biasa)" : "Folder masih kosong",
  ].join("\n");
  p.note(facts, "Deteksi");

  if (!hasBmad && !pre.skipBmad) {
    p.note(bmadMissingMessage(), "BMad dulu");
    p.outro("Pasang BMad, lalu jalankan lagi: npx github:wiradigitalid/wdi-method");
    process.exit(1);
  }

  let first = !hasWdi;
  if (hasWdi) {
    const update = cancelIf(
      await p.confirm({
        message: "WDI Method sudah terpasang. Update sekarang?",
        initialValue: true,
      }),
    );
    first = !update;
    if (first) {
      p.cancel("Tidak jadi meng-update.");
      process.exit(0);
    }
  } else {
    const go = cancelIf(
      await p.confirm({
        message: `Pasang WDI Method ke ${target}?`,
        initialValue: true,
      }),
    );
    if (!go) {
      p.cancel("Tidak jadi memasang.");
      process.exit(0);
    }
  }

  const existing = readIndexIdentity(target);
  const product = cancelIf(
    await p.text({
      message: "Nama produk (satu kamar: index.yaml product.name)",
      placeholder: existing.name && !identityIsPlaceholder(existing.name) ? existing.name : "contoh: Worship Presenter Web",
      defaultValue: existing.name && !identityIsPlaceholder(existing.name) ? existing.name : "",
      validate: (v) => (v && v.trim() && v.trim() !== "{product}" ? undefined : "Wajib. Ini diisi di G1 dan dipakai judul brief."),
    }),
  );
  const client = cancelIf(
    await p.text({
      message: "Nama klien (kosongkan kalau tidak ada)",
      placeholder: existing.client || "(opsional)",
      defaultValue: existing.client || "",
    }),
  );

  const selected = cancelIf(
    await p.multiselect({
      message: "Agen mana yang kebagian skill? (spasi untuk pilih)",
      options: ALL_AGENTS.map((id) => ({ value: id, label: AGENT_LABELS[id] })),
      initialValues: pre.agents || detectAgents(target),
      required: true,
    }),
  );

  p.note(
    [
      "Nama folder korpus tetap — bukan opsi instal:",
      "  .constitution  .control  .what  .how  .work  _bmad-output",
      "",
      "Yang ditulis untuk agen yang dipilih:",
      selected.includes("claude") ? "  .claude/skills/wdi-*  CLAUDE.md" : "",
      selected.includes("cursor") ? "  .agents/skills/wdi-*  .cursorrules" : "",
      selected.includes("codex") || selected.includes("cursor") || selected.includes("antigravity")
        ? "  AGENTS.md  (blok BEGIN:wdi-method)"
        : "",
      selected.includes("antigravity") ? "  .agents/AGENTS.md" : "",
    ]
      .filter(Boolean)
      .join("\n"),
    "Tujuan tulis",
  );

  const okGo = cancelIf(await p.confirm({ message: first ? "Jalankan install?" : "Jalankan update?", initialValue: true }));
  if (!okGo) {
    p.cancel("Dibatalkan.");
    process.exit(0);
  }

  const spinner = p.spinner();
  spinner.start(first ? "Memasang…" : "Meng-update…");
  apply(target, selected, {
    first,
    product: String(product).trim(),
    client: String(client).trim(),
  });
  spinner.stop(first ? "Terpasang" : "Ter-update");
  p.outro(first ? "Siap. Lanjut ke langkah sesudah install di atas." : "Siap. Cek diff blok metode di AGENTS.md.");
}

function runNonInteractive(args) {
  const target = requireTarget(args.dir);
  const agents = args.agents || detectAgents(target) || ALL_AGENTS.slice();
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
  apply(target, agents, { first: args.cmd === "update" ? false : first, product, client });
}

async function main() {
  const args = parseArgs(process.argv);
  if (!["wizard", "install", "update", "verify", "promote"].includes(args.cmd)) {
    usage();
    process.exit(2);
  }
  if (args.cmd === "promote") {
    if (!args.dir) die("promote needs a path to the working copy");
    promote(args.dir);
    return;
  }
  const wantTui = !args.yes && args.cmd !== "verify" && process.stdin.isTTY && process.stdout.isTTY;
  if (wantTui) {
    await runWizard(args);
    return;
  }
  if (args.cmd === "wizard" && !args.yes) {
    die("bukan TTY. Pakai `install --yes` / `update --yes`, atau jalankan di terminal.");
  }
  if (args.cmd === "wizard") args.cmd = wdiPresent(requireTarget(args.dir)) ? "update" : "install";
  runNonInteractive(args);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

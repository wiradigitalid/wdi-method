/**
 * Agent / IDE targets for install and update.
 *
 * IDs and skill directories align with BMad Method `platform-codes.yaml` so a repo's
 * `_bmad/_config/manifest.yaml` `ides:` list maps directly. Legacy WDI flags (`claude`,
 * `cursor`, …) are accepted as aliases.
 */

import path from "node:path";

/** @typedef {"claude-md" | "cursorrules" | "agents-mirror" | "opencode-commands"} PlatformHook */

/**
 * @typedef {object} Platform
 * @property {string} id
 * @property {string} name
 * @property {boolean} preferred
 * @property {string} skillDir
 * @property {PlatformHook[]} [hooks]
 */

/** @type {Record<string, string>} */
export const LEGACY_ALIASES = {
  claude: "claude-code",
  antigravity: "antigravity-cli",
};

/** @type {Platform[]} */
export const PLATFORMS = [
  { id: "adal", name: "AdaL", preferred: false, skillDir: ".adal/skills" },
  { id: "amp", name: "Sourcegraph Amp", preferred: false, skillDir: ".agents/skills" },
  { id: "antigravity", name: "Google Antigravity", preferred: false, skillDir: ".agent/skills", hooks: ["agents-mirror"] },
  { id: "antigravity-cli", name: "Antigravity CLI (AGY)", preferred: false, skillDir: ".agents/skills", hooks: ["agents-mirror"] },
  { id: "auggie", name: "Auggie", preferred: false, skillDir: ".agents/skills" },
  { id: "bob", name: "IBM Bob", preferred: false, skillDir: ".bob/skills" },
  { id: "claude-code", name: "Claude Code", preferred: true, skillDir: ".claude/skills", hooks: ["claude-md"] },
  { id: "cline", name: "Cline", preferred: false, skillDir: ".cline/skills" },
  { id: "codex", name: "Codex", preferred: true, skillDir: ".agents/skills" },
  { id: "codewhale", name: "CodeWhale", preferred: false, skillDir: ".codewhale/skills" },
  { id: "codebuddy", name: "CodeBuddy", preferred: false, skillDir: ".codebuddy/skills" },
  { id: "command-code", name: "Command Code", preferred: false, skillDir: ".agents/skills" },
  { id: "cortex", name: "Snowflake Cortex Code", preferred: false, skillDir: ".cortex/skills" },
  { id: "crush", name: "Crush", preferred: false, skillDir: ".agents/skills" },
  { id: "cursor", name: "Cursor", preferred: true, skillDir: ".agents/skills", hooks: ["cursorrules", "agents-mirror"] },
  { id: "droid", name: "Factory Droid", preferred: false, skillDir: ".factory/skills" },
  { id: "firebender", name: "Firebender", preferred: false, skillDir: ".firebender/skills" },
  { id: "gemini", name: "Gemini CLI", preferred: false, skillDir: ".agents/skills" },
  { id: "github-copilot", name: "GitHub Copilot", preferred: true, skillDir: ".agents/skills" },
  { id: "goose", name: "Block Goose", preferred: false, skillDir: ".agents/skills" },
  { id: "hermes", name: "Hermes Agent", preferred: false, skillDir: ".agents/skills" },
  { id: "iflow", name: "iFlow", preferred: false, skillDir: ".iflow/skills" },
  { id: "junie", name: "Junie", preferred: false, skillDir: ".junie/skills" },
  { id: "kilo", name: "KiloCoder", preferred: false, skillDir: ".agents/skills" },
  { id: "kimi-code", name: "Kimi Code", preferred: false, skillDir: ".agents/skills" },
  { id: "kiro", name: "Kiro", preferred: false, skillDir: ".kiro/skills" },
  { id: "kode", name: "Kode", preferred: false, skillDir: ".kode/skills" },
  { id: "mistral-vibe", name: "Mistral Vibe", preferred: false, skillDir: ".vibe/skills" },
  { id: "mux", name: "Mux", preferred: false, skillDir: ".agents/skills" },
  { id: "neovate", name: "Neovate", preferred: false, skillDir: ".neovate/skills" },
  { id: "ona", name: "Ona", preferred: false, skillDir: ".ona/skills" },
  { id: "openclaw", name: "OpenClaw", preferred: false, skillDir: ".agents/skills" },
  { id: "opencode", name: "OpenCode", preferred: false, skillDir: ".agents/skills", hooks: ["opencode-commands"] },
  { id: "openhands", name: "OpenHands", preferred: false, skillDir: ".agents/skills" },
  { id: "pi", name: "Pi", preferred: false, skillDir: ".agents/skills" },
  { id: "pochi", name: "Pochi", preferred: false, skillDir: ".agents/skills" },
  { id: "qoder", name: "Qoder", preferred: false, skillDir: ".qoder/skills" },
  { id: "qwen", name: "QwenCoder", preferred: false, skillDir: ".qwen/skills" },
  { id: "replit", name: "Replit Agent", preferred: false, skillDir: ".agents/skills" },
  { id: "roo", name: "Roo Code", preferred: false, skillDir: ".agents/skills" },
  { id: "rovo-dev", name: "Rovo Dev", preferred: false, skillDir: ".agents/skills" },
  { id: "trae", name: "Trae", preferred: false, skillDir: ".trae/skills" },
  { id: "warp", name: "Warp", preferred: false, skillDir: ".agents/skills" },
  { id: "windsurf", name: "Windsurf", preferred: false, skillDir: ".agents/skills" },
  { id: "zencoder", name: "Zencoder", preferred: false, skillDir: ".zencoder/skills" },
];

const BY_ID = new Map(PLATFORMS.map((p) => [p.id, p]));

export const ALL_PLATFORM_IDS = PLATFORMS.map((p) => p.id);

export const PREFERRED_PLATFORM_IDS = PLATFORMS.filter((p) => p.preferred).map((p) => p.id);

/** @param {string} raw */
export function normalizePlatformId(raw) {
  const id = raw.trim();
  return LEGACY_ALIASES[id] || id;
}

/** @param {string[]} rawIds */
export function normalizePlatformIds(rawIds) {
  const out = [];
  const seen = new Set();
  for (const raw of rawIds) {
    const id = normalizePlatformId(raw);
    if (!BY_ID.has(id)) continue;
    if (seen.has(id)) continue;
    seen.add(id);
    out.push(id);
  }
  return out;
}

/** @param {string} id */
export function getPlatform(id) {
  return BY_ID.get(normalizePlatformId(id));
}

/** @param {string} id */
export function isKnownPlatform(id) {
  return BY_ID.has(normalizePlatformId(id));
}

/** Preferred first, then declaration order — mirrors BMad install ordering. */
export function sortedPlatforms() {
  const preferred = PLATFORMS.filter((p) => p.preferred);
  const other = PLATFORMS.filter((p) => !p.preferred);
  return [...preferred, ...other];
}

/** @param {Platform} platform */
function hookNote(platform) {
  const bits = [platform.skillDir];
  if (platform.hooks?.includes("claude-md")) bits.push("CLAUDE.md");
  if (platform.hooks?.includes("cursorrules")) bits.push(".cursorrules");
  if (platform.hooks?.includes("agents-mirror")) bits.push(".agents/AGENTS.md");
  if (platform.hooks?.includes("opencode-commands")) bits.push(".opencode/commands");
  return bits.join(", ");
}

/** @param {string[]} selectedIds */
export function platformSelectOptions(selectedIds = []) {
  const configured = new Set(normalizePlatformIds(selectedIds));
  const sorted = sortedPlatforms();
  const head = sorted.filter((p) => configured.has(p.id));
  const tail = sorted.filter((p) => !configured.has(p.id));
  return [...head, ...tail].map((p) => {
    const tags = [];
    if (p.preferred) tags.push("⭐");
    if (configured.has(p.id)) tags.push("✅");
    const prefix = tags.length ? `${tags.join(" ")} ` : "";
    return {
      value: p.id,
      label: `${prefix}${p.name}  →  ${hookNote(p)}`,
    };
  });
}

/**
 * Minimal YAML list reader for `ides:` — no dependency on a YAML parser.
 * @param {import("node:fs")} fs
 * @param {string} filePath
 */
export function readYamlIdesList(fs, filePath) {
  if (!fs.existsSync(filePath)) return [];
  const text = fs.readFileSync(filePath, "utf8");
  const out = [];
  let inIdes = false;
  for (const line of text.split("\n")) {
    if (/^ides:\s*$/.test(line)) {
      inIdes = true;
      continue;
    }
    if (inIdes) {
      const item = line.match(/^\s+-\s+(\S+)/);
      if (item) {
        out.push(item[1]);
        continue;
      }
      if (line.trim() && !/^\s/.test(line)) inIdes = false;
    }
  }
  return out;
}

/**
 * @param {string} target
 * @param {import("node:fs")} fs
 */
export function readBmadManifestIdes(target, fs) {
  const file = path.join(target, "_bmad", "_config", "manifest.yaml");
  return readYamlIdesList(fs, file);
}

/**
 * @param {string} target
 * @param {import("node:fs")} fs
 */
export function detectPlatforms(target, fs) {
  const fromManifest = normalizePlatformIds(readBmadManifestIdes(target, fs));
  if (fromManifest.length) return fromManifest;

  const found = [];
  if (
    fs.existsSync(path.join(target, ".claude", "skills", "wdi-init", "SKILL.md")) ||
    fs.existsSync(path.join(target, ".claude", "skills", "bmad-help", "SKILL.md"))
  ) {
    found.push("claude-code");
  }
  if (
    fs.existsSync(path.join(target, ".cursorrules")) ||
    fs.existsSync(path.join(target, ".agents", "skills", "wdi-init", "SKILL.md"))
  ) {
    found.push("cursor");
  }
  if (fs.existsSync(path.join(target, "AGENTS.md"))) found.push("codex");
  if (fs.existsSync(path.join(target, ".agents", "AGENTS.md"))) found.push("antigravity-cli");
  if (fs.existsSync(path.join(target, ".agent", "skills", "wdi-init", "SKILL.md"))) {
    found.push("antigravity");
  }
  const unique = normalizePlatformIds(found);
  return unique.length ? unique : PREFERRED_PLATFORM_IDS.slice();
}

/**
 * @param {string} target
 * @param {string[]} platformIds
 */
export function skillDestinations(target, platformIds) {
  const dests = new Set();
  for (const id of normalizePlatformIds(platformIds)) {
    const platform = getPlatform(id);
    if (platform?.skillDir) dests.add(path.join(target, platform.skillDir));
  }
  return [...dests];
}

/** @param {string[]} platformIds */
export function platformUsesHook(platformIds, hook) {
  return normalizePlatformIds(platformIds).some((id) => getPlatform(id)?.hooks?.includes(hook));
}

export function formatPlatformList() {
  const idWidth = Math.max(...PLATFORMS.map((p) => p.id.length), 2);
  const nameWidth = Math.max(...PLATFORMS.map((p) => p.name.length), 4);
  const pad = (s, w) => s + " ".repeat(Math.max(0, w - s.length));
  const lines = [
    "Supported platform IDs (pass via --agents <id>[,<id>...]):",
    "",
    `  ${pad("ID", idWidth)}  ${pad("Name", nameWidth)}  Skill directory`,
    `  ${pad("-".repeat(idWidth), idWidth)}  ${pad("-".repeat(nameWidth), nameWidth)}  ${"-".repeat(14)}`,
  ];
  for (const p of sortedPlatforms()) {
    const star = p.preferred ? "⭐" : "  ";
    lines.push(`${star} ${pad(p.id, idWidth)}  ${pad(p.name, nameWidth)}  ${p.skillDir}`);
  }
  lines.push("", "⭐ = recommended (same as BMad Method)", "", "Example: npx wdi-method install --yes --agents claude-code,cursor");
  return lines.join("\n");
}

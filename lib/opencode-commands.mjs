import fs from "node:fs";
import path from "node:path";

const COMMANDS_DIR = ".opencode/commands";

/** OpenCode built-in slash commands — a skill name must not shadow these. */
export const RESERVED_OPENCODE_COMMANDS = new Set([
  "review",
  "commit",
  "init",
  "help",
  "skills",
  "fast",
  "compact",
  "clear",
  "undo",
  "redo",
  "edit",
  "editor",
  "exit",
  "quit",
  "theme",
  "config",
  "model",
  "session",
]);

/** @param {string} value */
export function isSafeSkillId(value) {
  return typeof value === "string" && /^[a-zA-Z0-9][a-zA-Z0-9_.-]*$/.test(value) && !value.includes("..");
}

/** @param {string} value */
function yamlSafeSingleLine(value) {
  const collapsed = String(value).replaceAll(/[\r\n]+/g, " ").trim();
  const needsQuoting = /[:#'"\\]/.test(collapsed) || /^[!&*?|>%@`[{]/.test(collapsed);
  if (!needsQuoting) return collapsed;
  const escaped = collapsed.replaceAll("\\", "\\\\").replaceAll('"', String.raw`\"`);
  return `"${escaped}"`;
}

/**
 * @param {string} skillDir
 */
export function readSkillDescription(skillDir) {
  const file = path.join(skillDir, "SKILL.md");
  if (!fs.existsSync(file)) return "";
  const text = fs.readFileSync(file, "utf8");
  const fm = text.match(/^---\n([\s\S]*?)\n---/);
  if (!fm) return "";
  const line = fm[1].match(/^description:\s*(.+)$/m);
  if (!line) return "";
  return line[1].trim().replace(/^["']|["']$/g, "");
}

/**
 * @param {string} description
 * @param {string} skillId
 */
export function buildOpencodeCommandBody(description, skillId) {
  const desc = description.trim() || `Run the ${skillId} skill`;
  return `---\ndescription: ${yamlSafeSingleLine(desc)}\n---\n\n@skills/${skillId}\n`;
}

/**
 * Write `.opencode/commands/<skill>.md` pointer files for each wdi-* skill.
 *
 * @param {string} target
 * @param {string[]} skillIds
 * @param {string} kitSkillsDir
 */
export function syncOpencodeCommands(target, skillIds, kitSkillsDir) {
  const commandsPath = path.join(target, COMMANDS_DIR);
  fs.mkdirSync(commandsPath, { recursive: true });

  let written = 0;
  for (const skillId of skillIds) {
    if (!skillId.startsWith("wdi-") || !isSafeSkillId(skillId)) continue;
    if (RESERVED_OPENCODE_COMMANDS.has(skillId)) continue;
    const src = path.join(kitSkillsDir, skillId);
    if (!fs.existsSync(path.join(src, "SKILL.md"))) continue;
    const body = buildOpencodeCommandBody(readSkillDescription(src), skillId);
    fs.writeFileSync(path.join(commandsPath, `${skillId}.md`), body);
    written += 1;
  }

  const removed = pruneRetiredOpencodeCommands(commandsPath, new Set(skillIds));
  return { written, removed };
}

/**
 * @param {string} commandsPath
 * @param {Set<string>} keep
 */
function pruneRetiredOpencodeCommands(commandsPath, keep) {
  if (!fs.existsSync(commandsPath)) return 0;
  let removed = 0;
  for (const entry of fs.readdirSync(commandsPath, { withFileTypes: true })) {
    if (!entry.isFile() || !entry.name.endsWith(".md")) continue;
    const skillId = entry.name.slice(0, -3);
    if (!skillId.startsWith("wdi-") || keep.has(skillId)) continue;
    fs.unlinkSync(path.join(commandsPath, entry.name));
    removed += 1;
  }
  return removed;
}

export function opencodeCommandsDir() {
  return COMMANDS_DIR;
}

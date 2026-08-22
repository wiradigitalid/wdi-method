import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  buildOpencodeCommandBody,
  readSkillDescription,
  syncOpencodeCommands,
} from "../lib/opencode-commands.mjs";

describe("OpenCode command pointers", () => {
  it("builds a frontmatter file that references @skills/<id>", () => {
    const body = buildOpencodeCommandBody("Help with gates", "wdi-help");
    assert.match(body, /^---\ndescription: Help with gates\n---\n\n@skills\/wdi-help\n$/);
  });

  it("reads description from SKILL.md frontmatter", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-oc-"));
    fs.writeFileSync(
      path.join(dir, "SKILL.md"),
      "---\nname: wdi-help\ndescription: Gate routing help\n---\n\n# Help\n",
    );
    assert.equal(readSkillDescription(dir), "Gate routing help");
  });

  it("writes and prunes wdi-* commands under .opencode/commands", () => {
    const target = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-oc-"));
    const kit = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-oc-kit-"));
    const skill = path.join(kit, "wdi-help");
    fs.mkdirSync(skill, { recursive: true });
    fs.writeFileSync(
      path.join(skill, "SKILL.md"),
      "---\ndescription: Help\n---\n\n# Help\n",
    );
    const retired = path.join(target, ".opencode", "commands");
    fs.mkdirSync(retired, { recursive: true });
    fs.writeFileSync(path.join(retired, "wdi-old.md"), "---\ndescription: x\n---\n\n@skills/wdi-old\n");

    const result = syncOpencodeCommands(target, ["wdi-help"], kit);
    assert.equal(result.written, 1);
    assert.equal(result.removed, 1);
    assert.ok(fs.existsSync(path.join(target, ".opencode", "commands", "wdi-help.md")));
    assert.equal(fs.existsSync(path.join(target, ".opencode", "commands", "wdi-old.md")), false);
  });
});

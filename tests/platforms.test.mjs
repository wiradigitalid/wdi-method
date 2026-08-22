import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  detectPlatforms,
  formatPlatformList,
  normalizePlatformId,
  normalizePlatformIds,
  platformSelectOptions,
  readYamlIdesList,
  skillDestinations,
  sortedPlatforms,
} from "../lib/platforms.mjs";

describe("platform registry", () => {
  it("maps legacy claude alias to claude-code", () => {
    assert.equal(normalizePlatformId("claude"), "claude-code");
    assert.deepEqual(normalizePlatformIds(["claude", "cursor"]), ["claude-code", "cursor"]);
  });

  it("lists preferred platforms first", () => {
    const sorted = sortedPlatforms();
    const firstPreferred = sorted.findIndex((p) => !p.preferred);
    assert.ok(firstPreferred > 0);
    assert.ok(sorted.slice(0, firstPreferred).every((p) => p.preferred));
  });

  it("marks preferred platforms with a star in select labels", () => {
    const options = platformSelectOptions([]);
    const cursor = options.find((o) => o.value === "cursor");
    assert.match(cursor.label, /⭐/);
    const adal = options.find((o) => o.value === "adal");
    assert.doesNotMatch(adal.label, /⭐/);
  });

  it("reads ides from a BMad manifest fragment", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-platforms-"));
    const file = path.join(dir, "manifest.yaml");
    fs.writeFileSync(
      file,
      "installation:\n  version: 1.0.0\nides:\n  - claude-code\n  - windsurf\n",
    );
    assert.deepEqual(readYamlIdesList(fs, file), ["claude-code", "windsurf"]);
  });

  it("detects platforms from BMad manifest before filesystem heuristics", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-platforms-"));
    const cfg = path.join(dir, "_bmad", "_config");
    fs.mkdirSync(cfg, { recursive: true });
    fs.writeFileSync(path.join(cfg, "manifest.yaml"), "ides:\n  - opencode\n");
    fs.writeFileSync(path.join(dir, "AGENTS.md"), "# rules\n");
    assert.deepEqual(detectPlatforms(dir, fs), ["opencode"]);
  });

  it("builds distinct skill destinations per platform", () => {
    const dests = skillDestinations("/repo", ["claude-code", "cursor", "adal"]);
    assert.equal(dests.length, 3);
    assert.ok(dests.some((d) => d.endsWith(`${path.sep}.claude${path.sep}skills`)));
    assert.ok(dests.some((d) => d.endsWith(`${path.sep}.agents${path.sep}skills`)));
    assert.ok(dests.some((d) => d.endsWith(`${path.sep}.adal${path.sep}skills`)));
  });

  it("formats a list-tools style table with stars", () => {
    const text = formatPlatformList();
    assert.match(text, /⭐.*claude-code/);
    assert.match(text, /cursor/);
  });
});

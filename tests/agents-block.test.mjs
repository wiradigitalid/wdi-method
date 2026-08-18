import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  extractBlock,
  upsertMethodBlock,
  fillProductTitle,
} from "../lib/agents-block.mjs";
import { writeProductIdentity, readProductIdentity } from "../lib/identity.mjs";

const BEGIN = "<!-- BEGIN:wdi-method -->";
const END = "<!-- END:wdi-method -->";

const template = `# Agent Rules — {product}

${BEGIN}
METHOD A
${END}

## Code
keep me
`;

describe("AGENTS.md method block", () => {
  it("extracts the marked block from the template", () => {
    const block = extractBlock(template);
    assert.equal(block.startsWith(BEGIN), true);
    assert.equal(block.endsWith(END), true);
    assert.match(block, /METHOD A/);
  });

  it("replaces an existing marked block and keeps product sections", () => {
    const existing = `# Agent Rules — Widget

Public rule stays.

${BEGIN}
OLD METHOD
${END}

## Code
app in src/
`;
    const next = upsertMethodBlock(existing, template);
    assert.match(next, /Public rule stays/);
    assert.match(next, /METHOD A/);
    assert.doesNotMatch(next, /OLD METHOD/);
    assert.match(next, /app in src\//);
  });

  it("injects the block before ## Code when markers are missing", () => {
    const existing = `# Agent Rules — Widget

## Public repository
do not leak

## Language
old language

## Bugs, decisions, questions
old bugs

## Code
app in src/
`;
    const next = upsertMethodBlock(existing, template);
    assert.match(next, /do not leak/);
    assert.match(next, /METHOD A/);
    assert.match(next, /app in src\//);
    const methodAt = next.indexOf("METHOD A");
    const codeAt = next.indexOf("## Code");
    assert.ok(methodAt < codeAt);
  });

  it("fills the product title on a fresh template", () => {
    assert.match(fillProductTitle(template, "Widget"), /# Agent Rules — Widget/);
  });
});

describe("index.yaml product identity", () => {
  it("inserts a product block when missing", () => {
    const next = writeProductIdentity("mode: catalog\n", { name: "Widget", client: "" });
    const id = readProductIdentity(next);
    assert.equal(id.name, "Widget");
    assert.equal(id.client, "");
  });

  it("replaces an existing product block", () => {
    const prev = `product:\n  name: "{product}"\n  client: ""\n\nmode: catalog\n`;
    const next = writeProductIdentity(prev, { name: "Widget", client: "Acme" });
    const id = readProductIdentity(next);
    assert.equal(id.name, "Widget");
    assert.equal(id.client, "Acme");
    assert.equal((next.match(/^product:/gm) || []).length, 1);
  });
});

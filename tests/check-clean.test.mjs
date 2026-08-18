import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(p));
    else if (entry.isFile()) out.push(p);
  }
  return out;
}

function read(rel) {
  return fs.readFileSync(path.join(ROOT, rel), "utf8");
}

const ALLOWED_GITHUB = [
  "github.com/wiradigitalid/wdi-method",
  "github.com/bmad-code-org/",
];

describe("published kit stays generic", () => {
  it("keeps the product-name placeholder in constitution and index.yaml", () => {
    // 0.5.0 split constitution.md: the product's half is authored in the room, and the overlay now
    // carries only the method's articles — which is exactly why it no longer holds {product}.
    assert.match(read("kit/.constitution/project/constitution.md"), /product\.name/);
    assert.match(read("kit/.constitution/project/constitution.md"), /\{product\}/);
    assert.match(read("scaffold/.control/registry/index.yaml"), /name: "\{product\}"/);
    assert.match(read("kit-overlay/AGENTS.md"), /BEGIN:wdi-method/);
    assert.match(read("kit-overlay/AGENTS.md"), /END:wdi-method/);
  });

  it("does not tell consumers to install from a private kit path", () => {
    const payload = ["kit", "kit-overlay", "scaffold"].flatMap((d) => walk(path.join(ROOT, d)));
    const hits = [];
    for (const file of payload) {
      const text = fs.readFileSync(file, "utf8");
      if (text.includes("handbook/method")) hits.push(path.relative(ROOT, file));
    }
    assert.deepEqual(hits, []);
  });

  it("does not link other private repositories", () => {
    const payload = ["kit", "kit-overlay", "scaffold", "bin", "lib", "README.md"].flatMap((d) => {
      const p = path.join(ROOT, d);
      if (fs.statSync(p).isFile()) return [p];
      return walk(p);
    });
    const hits = [];
    const re = /github\.com\/[^\s)'"`]+/g;
    for (const file of payload) {
      const text = fs.readFileSync(file, "utf8");
      for (const m of text.matchAll(re)) {
        const url = m[0].replace(/[.,;]+$/, "");
        if (!ALLOWED_GITHUB.some((ok) => url.startsWith(ok))) {
          hits.push(`${path.relative(ROOT, file)}: ${url}`);
        }
      }
    }
    assert.deepEqual(hits, []);
  });

  it("does not record a filesystem path to another checkout", () => {
    const payload = ["kit", "kit-overlay", "scaffold"].flatMap((d) => walk(path.join(ROOT, d)));
    const hits = [];
    for (const file of payload) {
      const text = fs.readFileSync(file, "utf8");
      if (/[A-Za-z]:\\Developer\\/.test(text) || /\/Users\/[^\s]+\/Developer\//.test(text)) {
        hits.push(path.relative(ROOT, file));
      }
    }
    assert.deepEqual(hits, []);
  });
});

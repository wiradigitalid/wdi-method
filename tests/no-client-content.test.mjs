// Nothing derived from one client may ship in this public package.
//
// 0.5.4 shipped `src/internal/referral/pool.go` inside sdd-guide.md, as the example of what a
// raise-to-verified must name. That is a real file in a real client's repo — 6,155 bytes, with a
// pool_integration_test.go beside it. A generic guide had been written by pointing at one product's
// tree and was never generalised.
//
// It surfaced as a V24 failure, but V24 could never have been the guard: it only fires in a
// CONSUMER, and only when the cited file is missing. The client whose tree it named stayed green
// precisely because it owned the file. So the detector has to live here, where the sentence is
// written — and it has to survive V24 no longer scanning `.constitution/method/` at all.
//
// Two shapes, because client content leaks in two ways:
//   1. a code path — `src/…`, `web/…`, `public/…`, `deploy/…`
//   2. a component-named corpus path — `.what/referral/…` names somebody's Product Component,
//      while `.what/_product-brief/` and `.what/business-rules.md` are the method's own slots
//
// A placeholder is exempt in both: `<` or `{` means the sentence is teaching a shape, which is
// exactly what the fix for pool.go turned it into.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
const TREES = ["kit", "kit-overlay", "scaffold"];
const READABLE = /\.(md|ya?ml|toml|py)$/;

const CITE = /`((?:\.what|\.how|src|web|public|deploy)\/[A-Za-z0-9_./*<>{}-]+\.[A-Za-z0-9]+)`/g;

function eachCite(fn) {
  const walk = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { walk(p); continue; }
      if (!READABLE.test(e.name)) continue;
      const rel = path.relative(ROOT, p).split(path.sep).join("/");
      for (const [, cited] of fs.readFileSync(p, "utf8").matchAll(CITE)) {
        if (cited.includes("<") || cited.includes("{")) continue;
        fn(rel, cited);
      }
    }
  };
  for (const t of TREES) walk(path.join(ROOT, t));
}

test("no product-code path ships in the kit — the pool.go defect, as a test", () => {
  const found = [];
  eachCite((rel, cited) => {
    if (/^(src|web|public|deploy)\//.test(cited)) found.push(`${rel} → \`${cited}\``);
  });
  assert.deepEqual(found, [],
    "a guide names one product's code tree. Write the shape instead — `src/<module>/<file>.go`:\n  " +
    found.join("\n  "));
});

test("no component-named corpus path ships in the kit — a PC name is the client's, not ours", () => {
  const found = [];
  eachCite((rel, cited) => {
    const [, second] = cited.split("/");
    // `_product-brief`, `_platform` and the like are the method's own slots; a bare name is a
    // Product Component, and only a product knows what its components are called.
    if (second && !second.startsWith("_") && !second.includes(".")) {
      found.push(`${rel} → \`${cited}\``);
    }
  });
  assert.deepEqual(found, [],
    "a guide names somebody's Product Component. Use `<pc>`:\n  " + found.join("\n  "));
});

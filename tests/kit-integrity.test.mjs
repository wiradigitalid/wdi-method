// Two checks that would each have stopped a defect this package actually shipped.
//
// 0.5.0 went out with kit/ carrying the PRE-FIX copy of the four overlay files, because `promote`
// ran before kit-overlay/ was swept and was never re-run. The result: three dead links in the very
// index a new install reads first. Nothing checked either fact, so nothing said anything.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
const KIT_CONST = path.join(ROOT, "kit", ".constitution");

/** Where each kit-overlay file is written into the kit. MUST match `replacements` in bin/. */
const OVERLAY_DESTINATIONS = {
  "constitution.md": ["method", "constitution.md"],
  "README.md": ["method", "README.md"],
  "repo-guide.md": ["method", "repo-guide.md"],
  "portability.md": ["method", "why", "portability.md"],
};

const lf = (s) => s.replaceAll("\r\n", "\n");

test("kit/ carries the CURRENT kit-overlay content — the 0.5.0 defect, as a test", () => {
  // kit/ is derived and kit-overlay/ is source, so the two can disagree with nothing to notice.
  // Comparing them is the cheapest possible guard, and it is the one that was missing.
  for (const [src, parts] of Object.entries(OVERLAY_DESTINATIONS)) {
    const overlay = path.join(ROOT, "kit-overlay", src);
    const inKit = path.join(KIT_CONST, ...parts);
    assert.ok(fs.existsSync(overlay), `kit-overlay/${src} is missing`);
    assert.ok(fs.existsSync(inKit), `${parts.join("/")} is missing from the kit`);
    assert.equal(lf(fs.readFileSync(inKit, "utf8")), lf(fs.readFileSync(overlay, "utf8")),
      `kit/.constitution/${parts.join("/")} is NOT the current kit-overlay/${src}. ` +
      `Run promote, or the overlay swap, before publishing — this is exactly what 0.5.0 shipped.`);
  }
});

test("every relative link inside the kit resolves — a dead link is what a new install reads first", () => {
  const dead = [];
  const walk = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.name.endsWith(".md")) {
        const text = fs.readFileSync(p, "utf8");
        for (const m of text.matchAll(/\]\(([^)]+)\)/g)) {
          const target = m[1];
          if (/^(https?:|#|mailto:)/.test(target) || target.includes("{")) continue;
          const [clean] = target.split("#");
          if (!clean) continue;
          if (!fs.existsSync(path.resolve(path.dirname(p), clean))) {
            dead.push(`${path.relative(KIT_CONST, p).split(path.sep).join("/")} -> ${target}`);
          }
        }
      }
    }
  };
  walk(KIT_CONST);
  assert.deepEqual(dead, [], `dead relative links in the kit:\n  ${dead.join("\n  ")}`);
});

test("no LIVE reference to a pre-0.5.0 path survives anywhere in what ships", () => {
  // The guard an external audit of 0.5.0 asked for, and it earns its place immediately: it finds a
  // pointer in scaffold/ that four hand sweeps had missed. scaffold/ is what a FRESH install receives,
  // so every new repo was being seeded with a link to a folder 0.5.0 deletes.
  //
  // Prose ABOUT the old layout is allowed — a migration note has to be able to name what moved — so a
  // line is only a finding when the path is not immediately preceded by a word like "formerly".
  const RETIRED = /\.constitution\/(document|codebase|scripts)\//g;
  const ALLOWED_NEARBY = /(formerly|used to|was at|pre-0\.5\.0|before 0\.5\.0|retired|old layout)/i;
  const hits = [];
  const walk = (dir) => {
    if (!fs.existsSync(dir)) return;
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { if (e.name !== "__pycache__") walk(p); continue; }
      if (!/\.(md|ya?ml|toml|py|mjs|js)$/.test(e.name)) continue;
      const lines = fs.readFileSync(p, "utf8").split(/\r?\n/);
      lines.forEach((line, i) => {
        RETIRED.lastIndex = 0;
        if (RETIRED.test(line) && !ALLOWED_NEARBY.test(line)) {
          hits.push(`${path.relative(ROOT, p).split(path.sep).join("/")}:${i + 1}  ${line.trim()}`);
        }
      });
    }
  };
  for (const d of ["kit", "kit-overlay", "scaffold"]) walk(path.join(ROOT, d));
  assert.deepEqual(hits, [],
    `a retired pre-0.5.0 path is still live in the published surface:\n  ${hits.join("\n  ")}`);
});

test("the AGENTS.md block does not call the whole kit non-binding", () => {
  // 0.5.0's block still said `.constitution/method/` is `status: Reference`, explains rather than
  // binds, and MUST NOT be installed as doc_standards. After the split that folder IS the kit — so the
  // block told every agent that no method guide binds, while bmad-prd.toml installed one of those very
  // guides as doc_standards. The Reference rule belongs to `method/why/` and nothing wider.
  const text = fs.readFileSync(path.join(ROOT, "kit-overlay", "AGENTS.md"), "utf8");
  for (const line of text.split(/\r?\n/)) {
    if (!/status: Reference|non-binding|MUST NOT be cited|doc_standards/.test(line)) continue;
    const m = line.match(/`\.constitution\/method\/(?!why\/)[^`]*`/);
    assert.equal(m, null,
      `this line applies a Reference-only rule to more than method/why/:\n  ${line.trim()}`);
  }
});

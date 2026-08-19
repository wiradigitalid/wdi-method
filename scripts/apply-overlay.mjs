#!/usr/bin/env node
// Copy kit-overlay/ into its four destinations inside kit/.
//
// `promote` used to be the only thing that did this, as a side effect. Now that promote is a rescue
// tool the swap needs a door of its own — otherwise editing kit-overlay/ leaves kit/ stale, which is
// exactly the defect 0.5.0 shipped: three dead links in the index a new install reads first.
//
// `npm run overlay` after touching any file in kit-overlay/. The kit-integrity test fails if you
// forget, so this is a convenience, not a trust boundary.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

// MUST match `replacements` in bin/wdi-method.js and OVERLAY_DESTINATIONS in tests/kit-integrity.
const DESTINATIONS = {
  "constitution.md": ["method", "constitution.md"],
  "README.md": ["method", "README.md"],
  "repo-guide.md": ["method", "repo-guide.md"],
  "portability.md": ["method", "why", "portability.md"],
};

let changed = 0;
for (const [src, parts] of Object.entries(DESTINATIONS)) {
  const from = path.join(ROOT, "kit-overlay", src);
  const to = path.join(ROOT, "kit", ".constitution", ...parts);
  if (!fs.existsSync(from)) {
    console.error(`error: kit-overlay/${src} is missing`);
    process.exit(1);
  }
  const before = fs.existsSync(to) ? fs.readFileSync(to, "utf8") : null;
  const after = fs.readFileSync(from, "utf8");
  if (before === after) continue;
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(from, to);
  console.log(`  kit-overlay/${src} → kit/.constitution/${parts.join("/")}`);
  changed += 1;
}
// AGENTS.md is deliberately absent: it is a template rendered into the product's own AGENTS.md by
// `upsertMethodBlock`, never copied into kit/. Adding it here would create a file no consumer reads.
console.log(changed ? `${changed} overlay file(s) applied` : "kit already matches kit-overlay");

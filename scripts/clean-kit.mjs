#!/usr/bin/env node
// Remove Python bytecode from kit/ before the package is built.
//
// Running any kit script writes kit/.constitution/method/scripts/__pycache__/*.pyc, and the fixture
// tests do exactly that. `files: ["kit/"]` in package.json then swept it into the tarball: 0.5.2 went
// out carrying a 123 kB validate.cpython-314.pyc nobody wanted. It embedded no machine path — CPython
// 3.14 no longer stores an absolute co_filename — but an earlier interpreter did, which is the whole
// reason walkFiles refuses .pyc for promote. Shipping it was luck, not design.
//
// Wired as `prepack`, so it runs for both `npm pack` and `npm publish`. The `!**/__pycache__` entries
// in `files` are the belt; this is the braces, because a negation in `files` is easy to get subtly
// wrong and hard to notice.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

let removed = 0;
function sweep(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === "__pycache__") {
        fs.rmSync(p, { recursive: true, force: true });
        console.log(`  removed ${path.relative(ROOT, p).split(path.sep).join("/")}`);
        removed += 1;
      } else {
        sweep(p);
      }
    } else if (/\.py[co]$/.test(entry.name)) {
      fs.rmSync(p, { force: true });
      console.log(`  removed ${path.relative(ROOT, p).split(path.sep).join("/")}`);
      removed += 1;
    }
  }
}

for (const dir of ["kit", "kit-overlay", "scaffold", "lib", "bin"]) sweep(path.join(ROOT, dir));
console.log(removed ? `${removed} bytecode artefact(s) removed` : "no bytecode in the package surface");

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

test("no Python bytecode anywhere in the package surface — 0.5.2 shipped 123 kB of it", () => {
  // Running any kit script writes __pycache__ next to it, and the fixture tests do exactly that.
  // `files: ["kit/"]` then swept it into the tarball. The published 0.5.2 embedded no machine path —
  // CPython 3.14 no longer stores an absolute co_filename — but 3.11 did, which is why walkFiles
  // already refuses .pyc for promote. Shipping it was luck. This test is what replaces the luck.
  const found = [];
  const walk = (dir) => {
    if (!fs.existsSync(dir)) return;
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) {
        if (e.name === "__pycache__") found.push(path.relative(ROOT, p).split(path.sep).join("/"));
        else walk(p);
      } else if (/\.py[co]$/.test(e.name)) {
        found.push(path.relative(ROOT, p).split(path.sep).join("/"));
      }
    }
  };
  for (const d of ["kit", "kit-overlay", "scaffold", "lib", "bin"]) walk(path.join(ROOT, d));
  assert.deepEqual(found, [],
    `bytecode inside the published surface — run \`npm run clean\`:\n  ${found.join("\n  ")}`);
});

test("a backtick cite of a method file resolves INSIDE the kit — the net cites-resolve gave up", () => {
  // cites-resolve no longer scans `.constitution/method/` in a product, and it should not: a consumer cannot
  // fix a guide that `update` overwrites, and a guide citing `.control/product-glossary.md` is
  // teaching where the glossary goes, not claiming this product already has one.
  //
  // But a guide citing a SIBLING guide is a real link, and dropping cites-resolve there would have left it
  // unchecked. So the check moves to where the fix would be made — here. Markdown links are already
  // covered above; this is the backtick form, which that walker never saw.
  const CITE = /`(\.constitution\/[A-Za-z0-9_./*-]+\.(?:md|yaml|yml|py))`/g;
  const dead = [];
  const walk = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { walk(p); continue; }
      if (!/\.(md|yaml|yml)$/.test(e.name)) continue;
      const text = fs.readFileSync(p, "utf8");
      for (const [, cited] of text.matchAll(CITE)) {
        // A `*` is a deliberate family — `codebase-*-guide.md` names three files by shape, and the
        // product decides how many exist. Resolve the family, not the literal string.
        const target = path.join(ROOT, "kit", cited);
        const hit = cited.includes("*")
          ? fs.existsSync(path.dirname(target)) &&
            fs.readdirSync(path.dirname(target)).some((f) =>
              new RegExp(`^${path.basename(cited).replaceAll(".", "\\.").replaceAll("*", ".*")}$`)
                .test(f))
          : fs.existsSync(target);
        if (!hit) dead.push(`${path.relative(ROOT, p).split(path.sep).join("/")} → \`${cited}\``);
      }
    }
  };
  walk(KIT_CONST);
  assert.deepEqual(dead, [],
    `a kit file cites a method path that does not ship:\n  ${dead.join("\n  ")}`);
});

test("what ships is English — the sweep missed 19 strings and nothing said so", () => {
  // This package is public and its documented language is English. Two sweeps have now left
  // Indonesian behind, and the second batch was worse than untidy: `wdi-log` told the agent to read
  // a `Berlaku` table and fill `Akibat`, while the file it scaffolds has `In force` and `Effect`.
  // A skill and the file it writes disagreeing is a defect no reader would think to look for.
  //
  // Function words only — they cannot appear inside English prose, so this cannot fire on a
  // technical term left in English, which language-guide.md requires.
  const WORDS = ["yang", "dengan", "untuk", "adalah", "dari", "pada", "tidak", "harus", "sudah",
                 "belum", "atau", "dalam", "akan", "hanya", "diisi", "dijalankan", "keputusan",
                 "berlaku", "sumber", "akibat", "digantikan", "beban", "paparan", "prioritas",
                 "rilis", "catatan", "penomoran", "dikonfirmasi", "bergantung"];
  const RE = new RegExp(`\\b(${WORDS.join("|")})\\b`, "gi");
  // validate.py is the one exemption, and it is deliberate: SENSITIVE_MARKERS is a bilingual union
  // and CRITICAL_YES matches `ya` as well as `yes`, because both read a PRODUCT's document, whose
  // language the product chooses. Those are reader-side by design — see the comments there.
  const EXEMPT = new Set(["kit/.constitution/method/scripts/validate.py"]);
  const found = [];
  const walk = (dir) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { walk(p); continue; }
      if (!/\.(md|ya?ml|toml|py|mjs|js|json)$/.test(e.name)) continue;
      const rel = path.relative(ROOT, p).split(path.sep).join("/");
      if (EXEMPT.has(rel)) continue;
      for (const m of fs.readFileSync(p, "utf8").matchAll(RE)) {
        found.push(`${rel}: ${m[0]}`);
      }
    }
  };
  for (const d of ["kit", "kit-overlay", "scaffold"]) walk(path.join(ROOT, d));
  assert.deepEqual(found, [],
    `Indonesian left in what ships:\n  ${[...new Set(found)].join("\n  ")}`);
});

// 0.5.35 shipped a DEADLOCK, and nothing said anything — which is the same shape as the two defects at
// the top of this file. Three statements, each reasonable alone, closed into a cycle:
//
//   wdi-ux         required Product Components before a run
//   wdi-init       requires "G2 passed" before Product Components are born
//   ux-guide       says G2 reads EXPERIENCE.md — which only a UX run produces
//
// So UX waited on components, components waited on G2, and G2 waited on UX. A project at that version
// could not open G2 at all once it needed UX. No validator can see this: every precondition lives in
// prose, in a different file, and each is correct on its own.
//
// The test is narrow on purpose. It does not try to parse the whole flow — it asserts that the one edge
// which closes the cycle stays broken.
test("wdi-ux does not wait for Product Components — that edge closes a deadlock", () => {
  const ux = lf(fs.readFileSync(path.join(ROOT, "kit", "skills", "wdi-ux", "SKILL.md"), "utf8"));
  const init = lf(fs.readFileSync(path.join(ROOT, "kit", "skills", "wdi-init", "SKILL.md"), "utf8"));
  const guide = lf(fs.readFileSync(path.join(KIT_CONST, "method", "document", "ux-guide.md"), "utf8"));

  // The two edges that make the third one fatal. If either ever stops being true the cycle is gone and
  // this test should be reconsidered rather than worked around — so assert them, and say so.
  assert.match(init, /`component`.*\*\*G2 passed\*\*/,
    "wdi-init no longer requires G2 passed before component birth. The deadlock this test guards may "
    + "no longer exist — re-derive the ordering before relaxing anything.");
  assert.match(guide, /Product Owner actually\s*\n?reads is `prd\.md` and `EXPERIENCE\.md`/,
    "G2 no longer reads EXPERIENCE.md. Same note as above — re-derive before relaxing.");

  // The edge that must stay broken.
  assert.doesNotMatch(ux, /MUST NOT run|refuses to run/,
    "wdi-ux refuses to run again. It MUST NOT gate on Product Components: G2 reads its EXPERIENCE.md, "
    + "and components are not born until G2 has passed. UX runs first, and the two <pc>-scoped halves "
    + "land when wdi-init births the components.");
  assert.match(ux, /MUST NOT wait for Product Components|needs a PRD and nothing else/,
    "wdi-ux no longer states that a run needs only a PRD — the rule that keeps the cycle open.");
});

test("both working templates point at the render command, and the pointer does not leak into it", () => {
  // The working brief and PRD are deliberately pointer-heavy now: Goals is one line, FR is an id,
  // and four PRD sections are gone entirely. A reader who opens one and finds it thin needs the
  // next step ON THE PAGE, or the split reads as a document that lost half its content.
  const T = (n) => path.join(ROOT, "kit", ".constitution", "method", "document", "templates", n);
  const brief = fs.readFileSync(T("brief.md"), "utf8");
  const prd = fs.readFileSync(T("prd.md"), "utf8");

  assert.match(brief, /`\/wdi-report render brief`/,
    "the brief template does not name the command that produces the readable version");
  assert.match(prd, /`\/wdi-report render prd`/,
    "the PRD template does not name the command that produces the readable version");

  // And it MUST sit ABOVE the first `##` heading the generator copies. `page_brief` and `page_prd`
  // lift sections by heading, so a pointer placed inside one would be copied into the deliverable —
  // where "run render to read the full document" is nonsense, because that IS the full document.
  for (const [name, raw, first] of [["brief.md", brief, "## Why"], ["prd.md", prd, "## Revision History"]]) {
    // Normalise line endings first: this repo is checked out CRLF on Windows, and splitting on a
    // bare "\n" silently found nothing rather than failing loudly.
    const body = raw.replace(/\r\n/g, "\n").split("```markdown\n")[1];
    assert.ok(body, `${name} no longer carries a \`\`\`markdown block — this test reads the wrong thing now`);
    assert.ok(body.indexOf("/wdi-report render") < body.indexOf(first),
      `in ${name} the render pointer sits below \`${first}\`, so the generator will copy it into the `
      + `deliverable and tell a reader to render the page they are already holding`);
  }
});

test("no skill reads a -rendered page as input — those trees are output, and a skill reading one reads its own echo", () => {
  // `.what-rendered/` and `.how-rendered/` are projections of the working documents plus the
  // registry. A skill that listed one under Inputs would be reading a copy of what it already has,
  // and — worse — treating a projection as a source. corpus-guide.md states the rule; this is what
  // makes it hold when the 16th skill is written.
  const skills = path.join(ROOT, "kit", "skills");
  const hits = [];
  for (const name of fs.readdirSync(skills)) {
    const p = path.join(skills, name, "SKILL.md");
    if (!fs.existsSync(p)) continue;
    const lines = fs.readFileSync(p, "utf8").split(/\r?\n/);
    let inInputs = false;
    lines.forEach((line, i) => {
      if (/^## /.test(line)) inInputs = /^## Inputs\b/.test(line);
      if (inInputs && /-rendered\//.test(line)) hits.push(`${name}/SKILL.md:${i + 1}  ${line.trim()}`);
    });
  }
  assert.deepEqual(hits, [],
    `a skill lists a rendered page as an Input. It is output — read the working document and the registry:\n  ${hits.join("\n  ")}`);
});

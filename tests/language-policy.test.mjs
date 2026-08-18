// Two language settings, and only two. What matters most here is the second test: a setting somebody
// already chose is NOT the installer's to change behind their back.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import {
  readLanguagePolicy,
  writeLanguagePolicy,
  readProductIdentity,
  DOC_LANGUAGES,
} from "../lib/identity.mjs";

const ROOT = path.resolve(import.meta.dirname, "..");
const CLI = path.join(ROOT, "bin", "wdi-method.js");

function repoWithIndex(policy) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-lang-"));
  fs.mkdirSync(path.join(dir, ".control", "registry"), { recursive: true });
  let text = 'product:\n  name: "X"\n  client: ""\n\nmode: catalog\n';
  if (policy) text = writeLanguagePolicy(text, policy);
  fs.writeFileSync(path.join(dir, ".control", "registry", "index.yaml"), text);
  return dir;
}

function run(args, dir) {
  return execFileSync(process.execPath,
    [CLI, "update", dir, "--yes", "--skip-bmad-check", "--agents", "claude", ...args],
    { cwd: ROOT, encoding: "utf8" });
}

function policyOf(dir) {
  return readLanguagePolicy(
    fs.readFileSync(path.join(dir, ".control", "registry", "index.yaml"), "utf8"));
}

test("writeLanguagePolicy is idempotent and leaves `product:` alone", () => {
  let text = 'product:\n  name: "X"\n  client: ""\n\nmode: catalog\n';
  text = writeLanguagePolicy(text, { docLanguage: "id", docFilenameLanguage: "id" });
  text = writeLanguagePolicy(text, { docLanguage: "en", docFilenameLanguage: "id" });
  assert.equal((text.match(/^policy:/gm) || []).length, 1, "a second policy block was written");
  assert.deepEqual(readLanguagePolicy(text), { docLanguage: "en", docFilenameLanguage: "id" });
  assert.match(text, /^product:\n  name: "X"/m, "product block was disturbed");
  assert.match(text, /^mode: catalog$/m, "the rest of index.yaml was disturbed");
});

test("the flags land in index.yaml", () => {
  const dir = repoWithIndex(null);
  try {
    run(["--doc-language", "id", "--doc-filename-language", "id"], dir);
    assert.deepEqual(policyOf(dir), { docLanguage: "id", docFilenameLanguage: "id" });
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("a setting that already exists is KEPT — update MUST NOT change it behind the owner's back", () => {
  const dir = repoWithIndex({ docLanguage: "id", docFilenameLanguage: "id" });
  try {
    const out = run(["--doc-language", "en", "--doc-filename-language", "en"], dir);
    assert.deepEqual(policyOf(dir), { docLanguage: "id", docFilenameLanguage: "id" },
      "update overwrote a language the product had already chosen");
    assert.match(out, /kept policy\.doc_language = id/,
      "keeping it silently is not enough — the run MUST say so");
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("English is the default when nothing is passed", () => {
  const dir = repoWithIndex(null);
  try {
    run([], dir);
    assert.deepEqual(policyOf(dir), { docLanguage: "en", docFilenameLanguage: "en" });
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("an unknown language is refused, not silently accepted", () => {
  const dir = repoWithIndex(null);
  try {
    assert.throws(() => run(["--doc-language", "jv"], dir), /doc-language needs one of/);
    assert.deepEqual(DOC_LANGUAGES, ["en", "id"]);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("CRLF: a Windows checkout is read and written without losing its endings", () => {
  // Bug found 2026-08-18 on the first real install into a Windows product repo. Every regex in
  // identity.mjs is anchored on a bare newline, so a CRLF file read as "" — and an empty name makes
  // identityIsPlaceholder true, which makes the installer write NOTHING and report nothing. It printed
  // `policy.doc_language = ` while the file plainly said `id`.
  const lf = [
    'product:',
    '  name: "X"',
    '  client: ""',
    '',
    'policy:',
    '  doc_language: id',
    '  doc_filename_language: id',
    '',
  ].join("\n");
  const crlf = lf.split("\n").join("\r\n");

  assert.deepEqual(readLanguagePolicy(crlf), { docLanguage: "id", docFilenameLanguage: "id" },
    "policy unreadable in a CRLF file");
  assert.equal(readProductIdentity(crlf).name, "X", "product name unreadable in a CRLF file");

  const out = writeLanguagePolicy(crlf, { docLanguage: "en", docFilenameLanguage: "id" });
  assert.ok(out.includes("\r\n"), "CRLF endings were flattened on write");
  assert.equal(out.split("\n").length - 1, out.split("\r\n").length - 1,
    "the file was left with mixed endings");
  assert.deepEqual(readLanguagePolicy(out), { docLanguage: "en", docFilenameLanguage: "id" });
  assert.equal((out.match(/^policy:/gm) || []).length, 1, "a second policy block appeared");

  const lfOut = writeLanguagePolicy(lf, { docLanguage: "en", docFilenameLanguage: "id" });
  assert.ok(!lfOut.includes("\r"), "an LF file was given CRLF endings");
});

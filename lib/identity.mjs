// index.yaml editing. Every regex here is anchored on `\n`, and a Windows checkout hands us `\r\n` —
// so every function normalises before matching and restores the file's own ending before writing.
//
// Skipping that is not a cosmetic bug. It silently returns "" for a name that IS set, which makes
// `identityIsPlaceholder` true, which makes `setProductIdentity` return early: the installer reports
// nothing and writes nothing, on every CRLF repo. Found 2026-08-18 on the first real install into a
// Windows product repo, where `policy.doc_language` printed empty while the file plainly said `id`.

const PRODUCT_BLOCK = /(?:^|\n)product:\n(?:  .*\n)*/;
const POLICY_BLOCK = /(?:^|\n)policy:\n(?:  .*\n)*/;
export const DOC_LANGUAGES = ["en", "id"];

/** LF view of the text, plus how to put the original endings back. */
function lf(text) {
  const crlf = text.includes("\r\n");
  return { body: crlf ? text.replaceAll("\r\n", "\n") : text, crlf };
}

function restore(body, crlf) {
  return crlf ? body.replaceAll("\n", "\r\n") : body;
}

export function yamlQuote(value) {
  return `"${String(value).replaceAll("\\", "\\\\").replaceAll('"', '\\"')}"`;
}

export function readProductIdentity(text) {
  const { body } = lf(text);
  const name = body.match(/product:\n(?:  .*\n)*?  name:\s*"([^"]*)"/);
  const client = body.match(/product:\n(?:  .*\n)*?  client:\s*"([^"]*)"/);
  return {
    name: name ? name[1] : "",
    client: client ? client[1] : "",
  };
}

export function writeProductIdentity(text, { name, client }) {
  const { body, crlf } = lf(text);
  const block =
    `product:\n  name: ${yamlQuote(name)}\n  client: ${yamlQuote(client ?? "")}\n`;
  if (/^product:/m.test(body)) {
    return restore(
      body.replace(PRODUCT_BLOCK, (m) => (m.startsWith("\n") ? `\n${block}` : block)), crlf);
  }
  return restore(`${block}\n${body.replace(/^﻿/, "")}`, crlf);
}

export function identityIsPlaceholder(name) {
  return !name || name === "{product}";
}

// ---------------------------------------------------------------------- language policy
//
// Two settings, and only two. Everything else about language is NOT a choice: method terminology,
// document code prefixes, machine-facing markers, and code identifiers are always English —
// `language-guide.md` owns that, and a caller MUST NOT ask about them.
//
//   doc_language           the PROSE of working documents in .what/ .how/ .control/
//   doc_filename_language  the SLUG part of a document filename
//
// Both default to `en`. A corpus written before these existed is NOT migrated for them: the readers
// in validate.py accept both languages, so an existing document keeps working and only new writing
// follows the setting.

export function readLanguagePolicy(text) {
  const { body } = lf(text);
  const doc = body.match(/policy:\n(?:  .*\n)*?  doc_language:\s*([A-Za-z-]+)/);
  const file = body.match(/policy:\n(?:  .*\n)*?  doc_filename_language:\s*([A-Za-z-]+)/);
  return {
    docLanguage: doc ? doc[1] : "",
    docFilenameLanguage: file ? file[1] : "",
  };
}

export function writeLanguagePolicy(text, { docLanguage, docFilenameLanguage }) {
  const { body, crlf } = lf(text);
  const block =
    `policy:\n  doc_language: ${docLanguage}\n  doc_filename_language: ${docFilenameLanguage}\n`;
  if (/^policy:/m.test(body)) {
    return restore(
      body.replace(POLICY_BLOCK, (m) => (m.startsWith("\n") ? `\n${block}` : block)), crlf);
  }
  // Sits right after `product:` when that block exists — the two answer the same kind of question,
  // so a reader who finds one finds the other.
  if (/^product:/m.test(body)) {
    return restore(body.replace(/^product:\n(?:  .*\n)*/m, (m) => `${m}\n${block}`), crlf);
  }
  return restore(`${block}\n${body.replace(/^﻿/, "")}`, crlf);
}

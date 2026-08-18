// index.yaml editing. Every regex here is anchored on `\n`, and a Windows checkout hands us `\r\n` —
// so every function normalises before matching and restores the file's own ending before writing.
//
// Skipping that is not a cosmetic bug. It silently returns "" for a name that IS set, which makes
// `identityIsPlaceholder` true, which makes `setProductIdentity` return early: the installer reports
// nothing and writes nothing, on every CRLF repo. Found 2026-08-18 on the first real install into a
// Windows product repo, where `policy.doc_language` printed empty while the file plainly said `id`.

const PRODUCT_BLOCK = /(?:^|\n)product:\n(?:  .*\n)*/;
const POLICY_BLOCK = /(?:^|\n)policy:\n(?:  .*\n)*/;

// FREE TEXT, not an enum. The consumer is a model, and a model does not need a list: "English",
// "Bahasa Indonesia", "id", "Indonesia" all read the same to it. Fencing this into two values would
// force the owner to translate their intent into the installer's vocabulary first, and nothing is
// bought with that.
export const DEFAULT_DOC_LANGUAGE = "English";

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
// A corpus written before these existed is NOT migrated for them: the readers in validate.py accept
// more than one language, so an existing document keeps working and only new writing follows the value.

function readPolicyValue(body, key) {
  const quoted = body.match(new RegExp(`policy:\\n(?:  .*\\n)*?  ${key}:[ \\t]*"([^"]*)"`));
  if (quoted) return quoted[1].trim();
  // Bare scalars are accepted because early repos wrote `doc_language: id` unquoted. Stops at a
  // comment so a trailing `# note` never becomes part of the value.
  const bare = body.match(new RegExp(`policy:\\n(?:  .*\\n)*?  ${key}:[ \\t]*([^\\n#]*)`));
  return bare ? bare[1].trim() : "";
}

export function readLanguagePolicy(text) {
  const { body } = lf(text);
  return {
    docLanguage: readPolicyValue(body, "doc_language"),
    docFilenameLanguage: readPolicyValue(body, "doc_filename_language"),
  };
}

export function writeLanguagePolicy(text, { docLanguage, docFilenameLanguage }) {
  const { body, crlf } = lf(text);
  // Always quoted: free text MAY carry a space or a colon, and a bare YAML scalar breaks on both.
  const block =
    `policy:\n  doc_language: ${yamlQuote(docLanguage)}\n` +
    `  doc_filename_language: ${yamlQuote(docFilenameLanguage)}\n`;
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

// A first install has nowhere to read a product name from, so the folder is the best guess available —
// and a guess the owner can accept with Enter beats a field they must type. `worship-presenter-web`
// becomes `Worship Presenter Web`; camelCase splits too. It is a SUGGESTION: G1 confirms the real name.
export function humaniseFolderName(name) {
  return String(name || "")
    .replace(/[._-]+/g, " ")
    .replace(/([a-z\d])([A-Z])/g, "$1 $2")
    .replace(/\s+/g, " ")
    .trim()
    .split(" ")
    .filter(Boolean)
    .map((w) => (w === w.toUpperCase() && w.length <= 4 ? w : w[0].toUpperCase() + w.slice(1)))
    .join(" ");
}

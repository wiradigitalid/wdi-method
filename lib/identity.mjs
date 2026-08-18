const PRODUCT_BLOCK = /(?:^|\n)product:\n(?:  .*\n)*/;

export function yamlQuote(value) {
  return `"${String(value).replaceAll("\\", "\\\\").replaceAll('"', '\\"')}"`;
}

export function readProductIdentity(text) {
  const name = text.match(/product:\n(?:  .*\n)*?  name:\s*"([^"]*)"/);
  const client = text.match(/product:\n(?:  .*\n)*?  client:\s*"([^"]*)"/);
  return {
    name: name ? name[1] : "",
    client: client ? client[1] : "",
  };
}

export function writeProductIdentity(text, { name, client }) {
  const block =
    `product:\n  name: ${yamlQuote(name)}\n  client: ${yamlQuote(client ?? "")}\n`;
  if (/^product:/m.test(text)) {
    return text.replace(PRODUCT_BLOCK, (m) => (m.startsWith("\n") ? `\n${block}` : block));
  }
  return `${block}\n${text.replace(/^﻿/, "")}`;
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
const POLICY_BLOCK = /(?:^|\n)policy:\n(?:  .*\n)*/;
export const DOC_LANGUAGES = ["en", "id"];

export function readLanguagePolicy(text) {
  const doc = text.match(/policy:\n(?:  .*\n)*?  doc_language:\s*([A-Za-z-]+)/);
  const file = text.match(/policy:\n(?:  .*\n)*?  doc_filename_language:\s*([A-Za-z-]+)/);
  return {
    docLanguage: doc ? doc[1] : "",
    docFilenameLanguage: file ? file[1] : "",
  };
}

export function writeLanguagePolicy(text, { docLanguage, docFilenameLanguage }) {
  const block =
    `policy:\n  doc_language: ${docLanguage}\n  doc_filename_language: ${docFilenameLanguage}\n`;
  if (/^policy:/m.test(text)) {
    return text.replace(POLICY_BLOCK, (m) => (m.startsWith("\n") ? `\n${block}` : block));
  }
  // Sits right after `product:` when that block exists — the two answer the same kind of question,
  // so a reader who finds one finds the other.
  if (/^product:/m.test(text)) {
    return text.replace(/^product:\n(?:  .*\n)*/m, (m) => `${m}\n${block}`);
  }
  return `${block}\n${text.replace(/^﻿/, "")}`;
}

export const BEGIN = "<!-- BEGIN:wdi-method -->";
export const END = "<!-- END:wdi-method -->";

export function extractBlock(template) {
  const i = template.indexOf(BEGIN);
  const j = template.indexOf(END);
  if (i === -1 || j === -1 || j < i) {
    throw new Error("AGENTS.md template is missing BEGIN/END:wdi-method markers");
  }
  return template.slice(i, j + END.length).trimEnd();
}

export function hasMethodBlock(text) {
  return text.includes(BEGIN) && text.includes(END) && text.indexOf(END) > text.indexOf(BEGIN);
}

export function replaceMarkedBlock(text, block) {
  const i = text.indexOf(BEGIN);
  const j = text.indexOf(END);
  return `${text.slice(0, i)}${block}${text.slice(j + END.length)}`;
}

export function injectWithoutMarkers(text, block) {
  const start = text.search(/^## Language\s*$/m);
  if (start !== -1) {
    const rest = text.slice(start);
    const endRel = rest.search(/\n(?=## Code\b|<!-- BEGIN:|## Sync rule\b)/);
    const end = endRel === -1 ? text.length : start + endRel;
    const before = text.slice(0, start).replace(/\s+$/, "\n\n");
    const after = text.slice(end).replace(/^\s+/, "\n\n");
    return `${before}${block}${after}`;
  }
  const heading = text.match(/^#[^\n]+\n+/);
  const at = heading ? heading[0].length : 0;
  return `${text.slice(0, at)}\n${block}\n\n${text.slice(at).replace(/^\s+/, "")}`;
}

export function upsertMethodBlock(existing, template) {
  const block = extractBlock(template);
  if (!existing || !existing.trim()) {
    return template;
  }
  if (hasMethodBlock(existing)) {
    return replaceMarkedBlock(existing, block);
  }
  return injectWithoutMarkers(existing, block);
}

export function fillProductTitle(template, productName) {
  if (!productName || productName === "{product}") return template;
  return template.replace(/^# Agent Rules — \{product\}/m, `# Agent Rules — ${productName}`);
}

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
  return `${block}\n${text.replace(/^\uFEFF/, "")}`;
}

export function identityIsPlaceholder(name) {
  return !name || name === "{product}";
}

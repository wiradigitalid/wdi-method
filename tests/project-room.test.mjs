// Kamar custom `.constitution/project/` punya tiga sifat, dan yang paling mahal kalau lepas adalah
// yang kedua: aturan khusus klien terbit ke repo publik.
//
// Tes ini MUST NOT menjalankan promote terhadap kit yang sebenarnya. Node menjalankan berkas tes
// secara paralel, dan promote menghapus kit sebelum menyalin ulang — versi pertama tes ini melakukannya
// dan membuat berkas tes lain gagal membaca kit di tengah jalan. Jadi paketnya disalin ke folder
// sementara lebih dulu, dan seluruh mutasi terjadi di salinan itu.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..");

function tmp(name) {
  return fs.mkdtempSync(path.join(os.tmpdir(), `wdi-${name}-`));
}

/** Salinan paket yang boleh dimutasi sepuasnya. */
function isolatedPackage() {
  const dir = tmp("pkg");
  for (const part of ["bin", "lib", "kit", "kit-overlay", "scaffold"]) {
    const src = path.join(ROOT, part);
    if (fs.existsSync(src)) fs.cpSync(src, path.join(dir, part), { recursive: true });
  }
  fs.copyFileSync(path.join(ROOT, "package.json"), path.join(dir, "package.json"));
  // @clack/prompts MUST resolve dari salinan ini. Junction, bukan symlink: di Windows symlink
  // direktori menuntut hak admin dan junction tidak.
  const deps = path.join(ROOT, "node_modules");
  if (fs.existsSync(deps)) {
    try {
      fs.symlinkSync(deps, path.join(dir, "node_modules"), "junction");
    } catch {
      fs.cpSync(deps, path.join(dir, "node_modules"), { recursive: true });
    }
  }
  return dir;
}

/** Repo produk tiruan: satu berkas generic, dan aturan khusus produk di kamarnya. */
function fakeLiveRepo(pkg) {
  const live = tmp("live");
  fs.mkdirSync(path.join(live, ".constitution", "project"), { recursive: true });
  fs.writeFileSync(path.join(live, ".constitution", "generic-guide.md"), "# generic\n");
  fs.writeFileSync(path.join(live, ".constitution", "project", "klien-rahasia.md"),
    "---\nscope: project\npurpose: \"aturan yang MUST NOT terbit\"\n---\nNama Klien Rahasia\n");
  fs.writeFileSync(path.join(live, ".constitution", "project", "README.md"), "DISUNTING DI PRODUK\n");
  for (const name of fs.readdirSync(path.join(pkg, "kit", "skills"))) {
    const dst = path.join(live, ".claude", "skills", name);
    fs.mkdirSync(dst, { recursive: true });
    fs.writeFileSync(path.join(dst, "SKILL.md"), "# stub\n");
  }
  return live;
}

test("kit membawa README kamar, dan itu satu-satunya berkas paket di dalamnya", () => {
  const room = path.join(ROOT, "kit", ".constitution", "project");
  assert.ok(fs.existsSync(path.join(room, "README.md")), "kit/.constitution/project/README.md hilang");
  assert.deepEqual(fs.readdirSync(room), ["README.md"],
    "kamar di kit MUST berisi README.md saja — berkas lain berarti aturan sebuah produk sudah terbit");
});

test("promote MELEWATI kamar: aturan khusus produk tidak terbit, dan README paket bertahan", () => {
  const pkg = isolatedPackage();
  const live = fakeLiveRepo(pkg);
  const room = path.join(pkg, "kit", ".constitution", "project");
  const before = fs.readFileSync(path.join(room, "README.md"), "utf8");
  try {
    execFileSync(process.execPath, [path.join(pkg, "bin", "wdi-method.js"), "promote", live],
                 { cwd: pkg, encoding: "utf8" });
    assert.ok(!fs.existsSync(path.join(room, "klien-rahasia.md")),
      "aturan khusus produk terbit ke kit — kebocoran yang tes ini ada untuk mencegahnya");
    assert.equal(fs.readFileSync(path.join(room, "README.md"), "utf8"), before,
      "README kamar tertimpa salinan produk; ia MUST tetap milik paket");
    assert.ok(fs.existsSync(path.join(pkg, "kit", ".constitution", "generic-guide.md")),
      "berkas generic justru tidak naik — penyaringnya terlalu lebar");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(live, { recursive: true, force: true });
  }
});

test("update MENYEMAI kamar sekali dan tidak pernah menimpanya", () => {
  const pkg = isolatedPackage();
  const target = tmp("target");
  const mine = path.join(target, ".constitution", "project", "aturan-saya.md");
  fs.mkdirSync(path.dirname(mine), { recursive: true });
  fs.writeFileSync(mine, "milik produk\n");
  fs.writeFileSync(path.join(target, ".constitution", "project", "README.md"), "DISUNTING\n");
  try {
    execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check"],
      { cwd: pkg, encoding: "utf8" });
    assert.equal(fs.readFileSync(mine, "utf8"), "milik produk\n",
      "update menimpa aturan produk di kamarnya — itu yang kamar ini ada untuk mencegahnya");
    assert.equal(fs.readFileSync(path.join(target, ".constitution", "project", "README.md"), "utf8"),
      "DISUNTING\n", "update menimpa berkas kamar yang sudah ada; ia MUST menyemai hanya bila kosong");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("walkFiles menolak keluaran build — sebuah .pyc membawa path absolut bernama produk", () => {
  const src = fs.readFileSync(path.join(ROOT, "bin", "wdi-method.js"), "utf8");
  const skipDirs = /const SKIP_DIRS = new Set\(\[([^\]]*)\]/s.exec(src);
  const skipFile = /const SKIP_FILE = (\/.*\/i);/.exec(src);
  assert.ok(skipDirs, "SKIP_DIRS hilang dari bin/wdi-method.js");
  assert.ok(skipDirs[1].includes('"__pycache__"'), "__pycache__ tidak disaring");
  assert.ok(skipFile, "SKIP_FILE hilang");
  const re = eval(skipFile[1]);
  assert.match("inventory.cpython-314.pyc", re);
  assert.doesNotMatch("keep.md", re);
});

test("update MENGHAPUS wrapper yang dipensiunkan, dan membiarkan yang bukan milik kita", () => {
  const pkg = isolatedPackage();
  const target = tmp("target");
  const skills = path.join(target, ".claude", "skills");
  // dipensiunkan: nama lama yang masih membawa SKILL.md
  fs.mkdirSync(path.join(skills, "wdi-apply"), { recursive: true });
  fs.writeFileSync(path.join(skills, "wdi-apply", "SKILL.md"), "# wrapper lama");
  // bukan milik kita: berawalan wdi- tetapi tanpa SKILL.md
  fs.mkdirSync(path.join(skills, "wdi-punya-saya"), { recursive: true });
  fs.writeFileSync(path.join(skills, "wdi-punya-saya", "catatan.md"), "milik pengguna");
  try {
    execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check",
       "--agents", "claude"],
      { cwd: pkg, encoding: "utf8" });
    assert.ok(!fs.existsSync(path.join(skills, "wdi-apply")),
      "wrapper yang dipensiunkan tetap tinggal — agent akan memanggilnya dan guide-nya sudah tidak ada");
    assert.ok(fs.existsSync(path.join(skills, "wdi-punya-saya", "catatan.md")),
      "folder wdi-* tanpa SKILL.md dihapus; itu milik pengguna, bukan milik metode");
    assert.ok(fs.existsSync(path.join(skills, "wdi-decision", "SKILL.md")),
      "wrapper yang berlaku tidak terpasang");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

test("update keeps the product's initiative slug — promote scrubs it, update MUST NOT write it back", () => {
  // Found on the first real install: promote replaces the slug with ISI-slug-inisiatif before publishing
  // (right), and update then wrote that placeholder into the product repo (wrong). The slug lives in TWO
  // places in bmad-prd.toml and the file itself says both MUST change together, so restoring only one
  // produced exactly the inconsistency it forbids.
  const pkg = isolatedPackage();
  const target = fs.mkdtempSync(path.join(os.tmpdir(), "wdi-slug-"));
  const kitToml = path.join(pkg, "kit", "assets", "bmad-custom", "bmad-prd.toml");
  const mine = path.join(target, "_bmad", "custom", "bmad-prd.toml");
  fs.mkdirSync(path.dirname(mine), { recursive: true });

  // what the package publishes: scrubbed in both spots, and one bare mention inside a comment
  fs.mkdirSync(path.dirname(kitToml), { recursive: true });
  fs.writeFileSync(kitToml, [
    '# a PRD landing in the folder named ISI-slug-inisiatif',
    'run_folder_pattern = "ISI-slug-inisiatif"',
    'facts = ["--path {project-root}/.control/memlog/prd-ISI-slug-inisiatif.md"]',
    '',
  ].join("\n"));
  // what the product actually has
  fs.writeFileSync(mine, [
    '# a PRD landing in the folder named ISI-slug-inisiatif',
    'run_folder_pattern = "shop-without-account"',
    'facts = ["--path {project-root}/.control/memlog/prd-shop-without-account.md"]',
    '',
  ].join("\n"));

  try {
    const out = execFileSync(process.execPath,
      [path.join(pkg, "bin", "wdi-method.js"), "update", target, "--yes", "--skip-bmad-check",
       "--agents", "claude"],
      { cwd: pkg, encoding: "utf8" });
    const after = fs.readFileSync(mine, "utf8");
    assert.match(after, /run_folder_pattern = "shop-without-account"/,
      "the placeholder overwrote a live run_folder_pattern");
    assert.match(after, /prd-shop-without-account\.md/,
      "the memlog path was left on the placeholder while the setting was restored — the two MUST agree");
    assert.match(after, /folder named ISI-slug-inisiatif/,
      "a bare mention in a comment was rewritten; that sentence explains the pattern");
    assert.match(out, /kept run_folder_pattern in bmad-prd\.toml/, "keeping it silently is not enough");
  } finally {
    fs.rmSync(pkg, { recursive: true, force: true });
    fs.rmSync(target, { recursive: true, force: true });
  }
});

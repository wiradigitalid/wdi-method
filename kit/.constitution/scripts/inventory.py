#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""inventory — menurunkan tiga inventaris dari kode, lalu mengadunya dengan rencananya.

Tiga inventaris — tabel, endpoint, layar — adalah keluaran G3 Blueprint dan ADA pada setiap `mode`,
termasuk `catalog`. Mereka lahir dua cara, dan `derived_from` di frontmatter menyatakan yang mana:

    plan   belum ada kode. Ditulis sebagai RENCANA oleh wdi-blueprint. Tidak ada yang bisa
           diturunkan, karena belum ada sumbernya.
    code   kodenya sudah ada. Diturunkan LEBIH DULU oleh script ini, lalu diadu dengan rencananya.

Selisih rencana-versus-kenyataan adalah TEMUAN, dan ia dilaporkan. Ia MUST NOT ditambal dengan
menyunting sisi yang lain — itu mengubah pekerjaan yang bisa terlupa jadi pekerjaan yang pasti
terlupa. Script ini karena itu punya dua mode dan yang pertama adalah defaultnya:

    inventory --check    turunkan, adu, laporkan. TIDAK menulis satu berkas pun
    inventory --write    tulis ulang bagian ## Rows dari apa yang diturunkan, lalu laporkan selisihnya

Determinisme adalah kontraknya, sama seperti validate.py: dua run atas kode yang sama MUST memberi
hasil yang sama. Karena itu semua iterasi terurut dan tidak ada yang bergantung pada jam dinding.

BATAS YANG DINYATAKAN DI MUKA. Ini pembaca pola, bukan compiler. Ia membaca:
    tabel     pernyataan CREATE TABLE di src/internal/platform/migrate/migrations/*.sql
    endpoint  registrasi route pada router Gin di src/**/*.go
    layar     komponen route pada SPA React di web/*/src/**/*.tsx
Apa yang tidak terbaca pola itu dilaporkan sebagai yang tidak terbaca — TIDAK ditebak, dan TIDAK
dihilangkan diam-diam. Sebuah inventaris MUST NOT dirakit dari README atau dari nama route yang
tampak masuk akal.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

KINDS = ("db", "api", "screen")

# ------------------------------------------------------------------ pola baca

# CREATE TABLE [IF NOT EXISTS] `nama` | nama
RE_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?([A-Za-z_][A-Za-z0-9_]*)[`\"]?",
    re.I)
RE_DROP_TABLE = re.compile(
    r"DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?[`\"]?([A-Za-z_][A-Za-z0-9_]*)[`\"]?", re.I)
# PRIMARY KEY / UNIQUE / FOREIGN KEY — kolom kunci, bukan seluruh kolom
RE_KEYCOL = re.compile(
    r"(?:PRIMARY\s+KEY|UNIQUE(?:\s+KEY)?|FOREIGN\s+KEY)[^(\n]*\(([^)]*)\)", re.I)

# r.GET("/path", ...) · group.POST(`/path`, ...) · r.Handle("GET", "/path", ...)
RE_ROUTE = re.compile(
    r"\.\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*\(\s*[`\"]([^`\"]+)[`\"]", re.I)
RE_GROUP = re.compile(r"\.\s*Group\s*\(\s*[`\"]([^`\"]+)[`\"]", re.I)

# Sebuah route group DIBUAT di satu berkas dan DIPAKAI di berkas lain:
#     portal.go:26   mountMemberAPI(engine.Group("/api"), ...)
#     member_api.go  api.GET("/me", ...)
# Karena itu prefiks TIDAK dapat disimpulkan per berkas. Ia harus mengikuti mount-nya, dan host-nya
# ikut dari titik pasang di app.go. Pola di bawah yang membuat penelusuran itu mungkin.
RE_FUNC_DEF = re.compile(r"^func\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)", re.M)
# mux.Handle(cfg.HostPublic, routing.NewPublicWithStore(...)) -> host `public`, entry NewPublicWithStore
RE_HOST_MOUNT = re.compile(
    r"Handle\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\.Host([A-Za-z0-9_]+)\s*,\s*"
    r"(?:[A-Za-z_][A-Za-z0-9_]*\.)?([A-Za-z_][A-Za-z0-9_]*)\s*\(")
# mountX(engine.Group("/api"), ...)  |  mountX(api, ...)
RE_CALL_GROUP = re.compile(
    r"\b([a-z][A-Za-z0-9_]*)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*Group\s*\(\s*[`\"]([^`\"]*)[`\"]\s*\)")
RE_CALL_PLAIN = re.compile(r"\b([a-z][A-Za-z0-9_]*)\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*[,)]")
# api := engine.Group("/x")  |  protected := api.Group("")
RE_ASSIGN_GROUP = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:?=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*Group\s*\(\s*[`\"]([^`\"]*)[`\"]",
    re.M)
RE_ASSIGN_ENGINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:?=\s*gin\.New\s*\(", re.M)
RE_ROUTE_ON = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*\(\s*[`\"]([^`\"]+)[`\"]",
    re.I)

# <Route path="/x" element={<Thing />} /> — react-router
RE_ROUTE_TSX = re.compile(
    r"<Route\s[^>]*path\s*=\s*[{\"']+([^\"'}]+)[\"'}]+[^>]*?"
    r"element\s*=\s*\{\s*<\s*([A-Za-z0-9_]+)", re.S)


@dataclass
class Row:
    key: str                      # identitas stabil baris, dipakai membandingkan
    cells: list[str]
    source: str                   # berkas tempat ia terbaca


@dataclass
class Derived:
    rows: list[Row] = field(default_factory=list)
    unread: list[str] = field(default_factory=list)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


RE_DOWN = re.compile(r"^\s*--\s*\+(?:goose|migrate)\s+Down\b", re.I | re.M)


def up_section(text: str) -> str:
    """Hanya bagian Up sebuah migrasi.

    Bagian Down memuat DROP TABLE untuk setiap tabel yang Up-nya membuat, jadi membaca seluruh berkas
    membuat setiap tabel terbaca sebagai dibuang. Pemisahannya MUST terjadi SEBELUM komentar
    dibuang, karena penanda goose sendiri adalah komentar.
    """
    match = RE_DOWN.search(text)
    return text[:match.start()] if match else text


def strip_sql_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"(--|#).*$", "", line) for line in text.splitlines())


# --------------------------------------------------------------------- tabel


def table_owner(root: Path) -> dict[str, str]:
    """Pemilik tiap tabel, dibaca dari `owns` dan `platform_owns` di components.yaml.

    Kolom pemilik BISA diturunkan sejak nilai `owns` disetel, jadi menuliskannya sebagai
    [NEEDS CONFIRMATION] akan menandai sebagai tidak diketahui sesuatu yang registry sudah nyatakan.
    Yang tidak diklaim siapa pun tetap [NEEDS CONFIRMATION] — itu temuan, bukan celah.
    """
    import yaml as _yaml
    path = root / ".control/registry/components.yaml"
    if not path.exists():
        return {}
    data = _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, str] = {}
    for pc in (data.get("product_components") or []):
        for entity in (pc.get("owns") or []):
            out[str(entity)] = str(pc.get("id"))
    for entity in (data.get("platform_owns") or []):
        out.setdefault(str(entity), "_platform")
    return out


def derive_db(root: Path) -> Derived:
    out = Derived()
    owner = table_owner(root)
    folder = root / "src/internal/platform/migrate/migrations"
    if not folder.is_dir():
        out.unread.append(f"{folder.as_posix()} tidak ada — tidak ada migrasi yang bisa dibaca")
        return out

    created: dict[str, tuple[str, str]] = {}   # tabel -> (kolom kunci, berkas)
    dropped: set[str] = set()
    for path in sorted(folder.glob("*.sql")):
        body = strip_sql_comments(up_section(read(path)))
        rel = path.relative_to(root).as_posix()
        for stmt in body.split(";"):
            match = RE_TABLE.search(stmt)
            if match:
                name = match.group(1)
                keys = sorted({c.strip().strip("`\"") for group in RE_KEYCOL.findall(stmt)
                               for c in group.split(",") if c.strip()})
                created[name] = (", ".join(f"`{k}`" for k in keys) or "—", rel)
                continue
            for name in RE_DROP_TABLE.findall(stmt):
                dropped.add(name)

    for name in sorted(created):
        if name in dropped:
            continue
        keys, rel = created[name]
        who = owner.get(name)
        out.rows.append(Row(key=name, source=rel,
                            cells=[f"`{name}`",
                                   f"`{who}`" if who else "[NEEDS CONFIRMATION]",
                                   "[NEEDS CONFIRMATION]", keys, "published"]))
        if not who:
            out.unread.append(f"tabel `{name}` tidak diklaim `owns` maupun `platform_owns` — "
                              f"V21 tidak melihatnya, dan tidak ada yang berwenang menulisnya")
    if dropped:
        out.unread.append("tabel yang di-DROP di bagian Up dan karena itu tidak didaftarkan: "
                          + ", ".join(sorted(dropped)))
    return out


# ------------------------------------------------------------------ endpoint


def _go_funcs(root: Path) -> tuple[dict[str, str], list[str]]:
    """Tiap fungsi Go di src/ dengan body-nya, plus daftar berkas yang dibaca."""
    bodies: dict[str, str] = {}
    files: list[str] = []
    for path in sorted((root / "src").rglob("*.go")):
        if path.name.endswith("_test.go"):
            continue
        body = read(path)
        files.append(body)
        marks = [(m.start(), m.group(1), m.group(2)) for m in RE_FUNC_DEF.finditer(body)]
        for i, (start, name, params) in enumerate(marks):
            end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
            bodies[name] = body[start:end]
            bodies[name + "\x00params"] = params
    return bodies, files


def _walk(fn: str, host: str, prefix: str, router_vars: dict[str, str],
          bodies: dict[str, str], out: dict[tuple[str, str, str], str],
          seen_calls: set[tuple[str, str, str]], depth: int = 0) -> None:
    """Telusuri satu fungsi: catat route-nya, lalu ikuti mount yang ia pasang.

    Sebuah fungsi MAY dipasang dari lebih dari satu host — `mountSharedPublicReads` dipanggil dari
    `member_api.go` DAN `public_api.go` — jadi rekursi ini sengaja tidak memoisasi per fungsi,
    hanya per (fungsi, host, prefiks). Tanpa itu, endpoint pada host kedua hilang tanpa jejak.
    """
    if depth > 8 or (fn, host, prefix) in seen_calls:
        return
    seen_calls.add((fn, host, prefix))
    body = bodies.get(fn)
    if body is None:
        return

    local = dict(router_vars)
    params = bodies.get(fn + "\x00params", "")
    for piece in params.split(","):
        piece = piece.strip()
        if "gin.RouterGroup" in piece or "gin.Engine" in piece:
            local[piece.split()[0]] = prefix
    for m in RE_ASSIGN_ENGINE.finditer(body):
        local[m.group(1)] = prefix
    for m in RE_ASSIGN_GROUP.finditer(body):
        base = local.get(m.group(2))
        if base is not None:
            local[m.group(1)] = (base + m.group(3)).rstrip("/")

    for var, method, raw in RE_ROUTE_ON.findall(body):
        if not raw.startswith("/") or var not in local:
            continue
        full = (local[var] + raw).replace("//", "/")
        out.setdefault((host, method.upper(), full), fn)

    for callee, var, grp in RE_CALL_GROUP.findall(body):
        if var in local and callee in bodies:
            _walk(callee, host, (local[var] + grp).rstrip("/"), {}, bodies, out, seen_calls, depth + 1)
    for callee, var in RE_CALL_PLAIN.findall(body):
        if var in local and callee in bodies:
            _walk(callee, host, local[var], {}, bodies, out, seen_calls, depth + 1)


def derive_api(root: Path) -> Derived:
    out = Derived()
    if not (root / "src").is_dir():
        out.unread.append("src/ tidak ada — tidak ada registrasi route yang bisa dibaca")
        return out

    bodies, files = _go_funcs(root)
    entries: list[tuple[str, str]] = []
    for body in files:
        for host, fn in RE_HOST_MOUNT.findall(body):
            entries.append((host.lower(), fn))
    if not entries:
        out.unread.append(
            "tidak satu pun titik pasang host terbaca (pola `Handle(cfg.Host<X>, <Fn>(`) — "
            "seluruh path di bawah ini MUST diperiksa tangan, sebab prefiks group tidak dapat "
            "ditelusuri tanpa titik pasangnya")

    found: dict[tuple[str, str, str], str] = {}
    for host, fn in sorted(set(entries)):
        _walk(fn, host, "", {}, bodies, found, set())

    _, plat = decisions(root / ".how/_platform/inventory-api.md")
    for (host, method, path_str) in sorted(found):
        key = f"{host} {method} {path_str}"
        owner = "`_platform`" if (key in plat or f"{method} {path_str}" in plat
                                 or path_str in plat) else "[NEEDS CONFIRMATION]"
        out.rows.append(Row(key=key, source=found[(host, method, path_str)],
                            cells=[host, method, f"`{path_str}`", owner,
                                   "[NEEDS CONFIRMATION]", "published"]))
    if not found:
        out.unread.append("tidak satu pun registrasi route terbaca di src/**/*.go — "
                          "bila API-nya memang belum ada, `derived_from: plan` yang benar")
    return out


def derive_screen(root: Path) -> Derived:
    out = Derived()
    folder = root / "web"
    if not folder.is_dir():
        out.unread.append("web/ tidak ada — tidak ada halaman yang bisa dibaca")
        return out

    # KUNCINYA (spa, rute), BUKAN rute saja. Produk ini punya dua SPA yang dibangun terpisah, dan
    # keduanya mendeklarasikan `/`, `/login`, dan `*`. Mengunci pada rute saja menghilangkan yang
    # kembar tanpa suara: 26 layar terbaca sebagai 23. Sebuah rute bukan identitas sebuah layar di
    # produk ber-SPA jamak — hostnya bagian dari identitas itu.
    seen: dict[tuple[str, str], tuple[str, str]] = {}
    for path in sorted(folder.rglob("*.tsx")):
        if "node_modules" in path.parts or path.name.endswith(".test.tsx"):
            continue
        rel = path.relative_to(root).as_posix()
        parts = path.relative_to(folder).parts
        spa = parts[0] if parts else "?"
        for route, component in RE_ROUTE_TSX.findall(read(path)):
            seen.setdefault((spa, route.strip()), (component, rel))

    states, _ = decisions(root / ".how/_platform/inventory-screen.md")
    folded: dict[str, list[str]] = {}
    for (spa, route) in sorted(seen):
        parent = states.get(route)
        if parent:
            folded.setdefault(f"{spa}:{parent}", []).append(route)

    for spa, route in sorted(seen):
        if route in states:
            continue  # ia keadaan dari layar lain, bukan baris tersendiri
        component, rel = seen[(spa, route)]
        extra = folded.get(f"{spa}:{route}") or []
        state_cell = ", ".join(f"`{r}`" for r in sorted(extra)) if extra else "—"
        out.rows.append(Row(key=f"{spa}:{route}", source=rel,
                            cells=[f"`{spa}/{component}`", f"`{route}`", state_cell,
                                   "[NEEDS CONFIRMATION]", "[NEEDS CONFIRMATION]"]))

    orphan = sorted(r for r in states
                    if not any(states[r] == route for _, route in seen))
    if orphan:
        out.unread.append("rute-keadaan yang induknya tidak terbaca di kode: " + ", ".join(orphan))
    if not seen:
        out.unread.append("tidak satu pun <Route path=... element={<X />}> terbaca di web/**/*.tsx")
    else:
        shared = sorted({r for _, r in seen} & {r for s, r in seen if s != sorted({x for x, _ in seen})[0]})
        dupes = sorted({r for s, r in seen} )
        collide = sorted({r for r in dupes if sum(1 for s2, r2 in seen if r2 == r) > 1})
        if collide:
            out.unread.append("rute yang dideklarasikan LEBIH DARI SATU SPA, dan karena itu bukan "
                              "identitas layar dengan sendirinya: " + ", ".join(collide))
    return out


DERIVERS = {"db": derive_db, "api": derive_api, "screen": derive_screen}
HEADERS = {
    "db": ("No", "Table", "Owning component", "What it holds", "Key columns", "Status"),
    "api": ("No", "Host", "Method", "Path", "Owning component", "Description", "Status"),
    "screen": ("No", "Screen", "Route", "States", "Owning component", "UC served"),
}


# ------------------------------------------------------- rencana yang tercatat


ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.*)\|\s*$")
FM_RE = re.compile(r"\A---\n(.*?)\n---", re.S)


def decisions(path: Path) -> tuple[dict[str, str], set[str]]:
    """(`states`, `platform_rows`) dari frontmatter — keputusan pemilik, bukan hasil pola.

    `states` memetakan rute-keadaan ke rute layar induknya. Sebuah keadaan BUKAN layar: ux-guide
    sudah menuntut tiap layar punya keadaan kosong dan error, jadi keadaan adalah kolom pada baris
    induknya, bukan baris kedua.

    `platform_rows` menyebut baris yang dimiliki `_platform`. Tidak ada janji Product Component di
    belakangnya, dan corpus-guide memiliki tes dua-bagiannya.
    """
    if not path.exists():
        return {}, set()
    match = FM_RE.match(read(path))
    if not match:
        return {}, set()
    try:
        import yaml as _yaml
        fm = _yaml.safe_load(match.group(1)) or {}
    except Exception:
        return {}, set()
    states = {str(k): str(v) for k, v in (fm.get("states") or {}).items()}
    plat = {str(x) for x in (fm.get("platform_rows") or [])}
    return states, plat


def plan_rows(path: Path) -> tuple[dict[int, list[str]], str | None]:
    """Baca bagian ## Rows dari inventaris yang tercatat. None bila berkasnya belum ada."""
    if not path.exists():
        return {}, None
    text = read(path)
    inside = False
    rows: dict[int, list[str]] = {}
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower().startswith("rows")
            continue
        if not inside:
            continue
        match = ROW_RE.match(line.strip())
        if match:
            rows[int(match.group(1))] = [c.strip() for c in match.group(2).split("|")]
    mode = "plan"
    fm = re.search(r"^derived_from:\s*(\w+)", text, re.M)
    if fm:
        mode = fm.group(1)
    return rows, mode


def plan_keys(kind: str, rows: dict[int, list[str]]) -> dict[str, int]:
    """Identitas stabil baris rencana, disusun sama dengan Row.key hasil derivasi."""
    out: dict[str, int] = {}
    for number, cells in sorted(rows.items()):
        if kind == "db" and cells:
            out[cells[0].strip("`")] = number
        elif kind == "api" and len(cells) >= 3:
            # Host bagian identitas: satu fungsi mount MAY dipasang di lebih dari satu host, dan
            # tanpa host di kunci kedua endpoint itu melebur jadi satu baris.
            out[f"{cells[0]} {cells[1].upper()} {cells[2].strip('`')}"] = number
        elif kind == "screen" and len(cells) >= 2:
            # Screen ditulis `<spa>/<Component>`; spa-nya bagian identitas, sama seperti di derivasi.
            screen = cells[0].strip("`")
            spa = screen.split("/", 1)[0] if "/" in screen else "?"
            out[f"{spa}:{cells[1].strip('`')}"] = number
    return out


def render_rows(kind: str, derived: Derived, keys: dict[str, int]) -> str:
    """Nomor STABIL: baris yang sudah punya nomor mempertahankannya, yang baru mengambil berikutnya.

    Menomori ulang berarti mengganti nama setiap berkas sesudahnya dan mematahkan setiap tautan yang
    menunjuk ke arahnya, jadi ia MUST NOT dilakukan — juga ketika baris di tengah menghilang.
    """
    next_no = max(keys.values(), default=0) + 1
    lines = ["| " + " | ".join(HEADERS[kind]) + " |",
             "| " + " | ".join("---" for _ in HEADERS[kind]) + " |"]
    for row in derived.rows:
        number = keys.get(row.key)
        if number is None:
            number = next_no
            next_no += 1
        lines.append(f"| {number} | " + " | ".join(row.cells) + " |")
    return "\n".join(lines)


def write_rows(path: Path, block: str) -> None:
    text = read(path)
    if "## Rows" not in text:
        raise SystemExit(f"inventory: {path.as_posix()} tidak punya bagian `## Rows` — "
                         f"lahirkan dulu dari templates/inventory.md")
    head, _, rest = text.partition("## Rows")
    tail = ""
    for marker in ("\n## ",):
        idx = rest.find(marker)
        if idx != -1:
            tail = rest[idx:]
            break
    path.write_text(head + "## Rows\n\n" + block + "\n" + tail, encoding="utf-8")


# ----------------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="inventory",
        description="Turunkan tiga inventaris dari kode, lalu adu dengan rencananya")
    parser.add_argument("--check", action="store_true",
                        help="turunkan dan laporkan; tidak menulis apa pun (default)")
    parser.add_argument("--write", action="store_true",
                        help="tulis ulang bagian ## Rows dari hasil derivasi")
    parser.add_argument("--kind", choices=KINDS, action="append",
                        help="batasi ke satu jenis; boleh diulang")
    parser.add_argument("--root", default=".", help="akar repo (default: direktori sekarang)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / ".control" / "registry").is_dir():
        print(f"inventory: {root} tidak punya .control/registry/ — salah akar repo?", file=sys.stderr)
        return 2

    kinds = args.kind or list(KINDS)
    findings = 0

    for kind in kinds:
        path = root / f".how/_platform/inventory-{kind}.md"
        rel = path.relative_to(root).as_posix()
        derived = DERIVERS[kind](root)
        recorded, mode = plan_rows(path)
        keys = plan_keys(kind, recorded)

        print(f"\n=== {kind} — {rel}")
        if mode is None:
            print("  berkasnya belum ada. Lahirkan dari templates/inventory.md; sampai itu terjadi "
                  "tidak ada rencana yang bisa diadu")
        else:
            print(f"  derived_from: {mode} · {len(recorded)} baris tercatat")
        print(f"  {len(derived.rows)} baris terbaca dari kode")

        derived_keys = {row.key for row in derived.rows}
        missing = sorted(set(keys) - derived_keys)      # direncanakan, tidak ada di kode
        extra = sorted(derived_keys - set(keys))        # ada di kode, tidak direncanakan

        for item in missing:
            print(f"  TEMUAN  direncanakan tetapi tidak terbaca di kode: {item}")
        for item in extra:
            print(f"  TEMUAN  ada di kode tetapi tidak tercatat di rencana: {item}")
        for note in derived.unread:
            print(f"  TIDAK TERBACA  {note}")
        findings += len(missing) + len(extra)

        if args.write:
            if not path.exists():
                print("  --write dilewati: berkasnya belum ada")
                continue
            write_rows(path, render_rows(kind, derived, keys))
            print(f"  tulis {rel} — bagian ## Rows saja")

    print(f"\n{findings} selisih rencana-versus-kode.")
    if findings:
        print("Selisih ini TEMUAN, bukan pekerjaan tangan. Ia dirutekan ke skill yang memiliki "
              "sisinya, dan MUST NOT ditambal dengan menyunting sisi yang lain.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

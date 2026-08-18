#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""inventory — derives the three inventories from code, then compares them against the plan.

The three inventories — tables, endpoints, screens — are a G3 Blueprint output and EXIST at every
`mode`, including `catalog`. They are born two ways, and `derived_from` in the frontmatter states
which one:

    plan   no code yet. Written as a PLAN by wdi-blueprint. Nothing can be derived,
           because there is no source yet.
    code   the code already exists. Derived FIRST by this script, then compared against the plan.

A plan-versus-reality gap is a FINDING, and it is reported. It MUST NOT be patched over by
editing the other side — that turns work that could be forgotten into work that definitely
will be. This script therefore has two modes, and the first is the default:

    inventory --check    derive, compare, report. Writes NOT ONE file
    inventory --write    rewrite the ## Rows section from what was derived, then report the gap

Determinism is the contract, same as validate.py: two runs over the same code MUST produce the
same result. That is why every iteration is ordered and none depends on the wall clock.

THE STATED-UP-FRONT LIMIT. This is a pattern reader, not a compiler. It reads:
    table     CREATE TABLE statements in src/internal/platform/migrate/migrations/*.sql
    endpoint  route registrations on the Gin router in src/**/*.go
    screen    route components in the React SPA in web/*/src/**/*.tsx
Whatever the pattern cannot read is reported as unread — NOT guessed, and NOT silently
dropped. An inventory MUST NOT be assembled from a README or from a route name that merely
looks plausible.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

KINDS = ("db", "api", "screen")

# ------------------------------------------------------------------ read patterns

# CREATE TABLE [IF NOT EXISTS] `name` | name
RE_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?([A-Za-z_][A-Za-z0-9_]*)[`\"]?",
    re.I)
RE_DROP_TABLE = re.compile(
    r"DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?[`\"]?([A-Za-z_][A-Za-z0-9_]*)[`\"]?", re.I)
# PRIMARY KEY / UNIQUE / FOREIGN KEY — key columns, not every column
RE_KEYCOL = re.compile(
    r"(?:PRIMARY\s+KEY|UNIQUE(?:\s+KEY)?|FOREIGN\s+KEY)[^(\n]*\(([^)]*)\)", re.I)

# r.GET("/path", ...) · group.POST(`/path`, ...) · r.Handle("GET", "/path", ...)
RE_ROUTE = re.compile(
    r"\.\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*\(\s*[`\"]([^`\"]+)[`\"]", re.I)
RE_GROUP = re.compile(r"\.\s*Group\s*\(\s*[`\"]([^`\"]+)[`\"]", re.I)

# A route group is CREATED in one file and USED in another:
#     portal.go:26   mountMemberAPI(engine.Group("/api"), ...)
#     member_api.go  api.GET("/me", ...)
# Because of that, a prefix CANNOT be inferred per file. It must follow its mount, and the host
# comes along from the mount point in app.go. The patterns below are what make that trace possible.
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
    key: str                      # the row's stable identity, used for comparison
    cells: list[str]
    source: str                   # the file where it was read


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
    """Only a migration's Up section.

    The Down section holds a DROP TABLE for every table its Up creates, so reading the whole
    file makes every table read as dropped. This split MUST happen BEFORE comments are
    stripped, because the goose marker itself is a comment.
    """
    match = RE_DOWN.search(text)
    return text[:match.start()] if match else text


def strip_sql_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"(--|#).*$", "", line) for line in text.splitlines())


# --------------------------------------------------------------------- table


def table_owner(root: Path) -> dict[str, str]:
    """Every table's owner, read from `owns` and `platform_owns` in components.yaml.

    The owner column CAN be derived as soon as an `owns` value is set, so writing it as
    [NEEDS CONFIRMATION] would flag as unknown something the registry has already stated.
    Whatever no one claims stays [NEEDS CONFIRMATION] — that is a finding, not a gap in the rule.
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
        out.unread.append(f"{folder.as_posix()} does not exist — no migration can be read")
        return out

    created: dict[str, tuple[str, str]] = {}   # table -> (key columns, file)
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
            out.unread.append(f"table `{name}` is claimed by neither `owns` nor `platform_owns` — "
                              f"V21 does not see it, and no one is authorized to write it")
    if dropped:
        out.unread.append("tables dropped in the Up section and therefore not registered: "
                          + ", ".join(sorted(dropped)))
    return out


# ------------------------------------------------------------------ endpoint


def _go_funcs(root: Path) -> tuple[dict[str, str], list[str]]:
    """Every Go function in src/ with its body, plus the list of files read."""
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
    """Walk one function: record its routes, then follow the mounts it sets up.

    A function MAY be mounted from more than one host — `mountSharedPublicReads` is called from
    `member_api.go` AND `public_api.go` — so this recursion deliberately does not memoize per
    function, only per (function, host, prefix). Without that, the endpoints on the second host
    disappear without a trace.
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
        out.unread.append("src/ does not exist — no route registration can be read")
        return out

    bodies, files = _go_funcs(root)
    entries: list[tuple[str, str]] = []
    for body in files:
        for host, fn in RE_HOST_MOUNT.findall(body):
            entries.append((host.lower(), fn))
    if not entries:
        out.unread.append(
            "not one host mount point was read (pattern `Handle(cfg.Host<X>, <Fn>(`) — "
            "every path below MUST be checked by hand, since a group's prefix cannot be "
            "traced without its mount point")

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
        out.unread.append("not one route registration was read in src/**/*.go — "
                          "if the API genuinely does not exist yet, `derived_from: plan` is correct")
    return out


def derive_screen(root: Path) -> Derived:
    out = Derived()
    folder = root / "web"
    if not folder.is_dir():
        out.unread.append("web/ does not exist — no page can be read")
        return out

    # THE KEY IS (spa, route), NOT the route alone. This product has two SPAs built separately,
    # and both declare `/`, `/login`, and `*`. Keying on the route alone silently collapses the
    # duplicates: 26 screens read as 23. A route is not a screen's identity in a product with
    # multiple SPAs — the host is part of that identity.
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
            continue  # it is a state of another screen, not a row of its own
        component, rel = seen[(spa, route)]
        extra = folded.get(f"{spa}:{route}") or []
        state_cell = ", ".join(f"`{r}`" for r in sorted(extra)) if extra else "—"
        out.rows.append(Row(key=f"{spa}:{route}", source=rel,
                            cells=[f"`{spa}/{component}`", f"`{route}`", state_cell,
                                   "[NEEDS CONFIRMATION]", "[NEEDS CONFIRMATION]"]))

    orphan = sorted(r for r in states
                    if not any(states[r] == route for _, route in seen))
    if orphan:
        out.unread.append("state-routes whose parent was not read in the code: " + ", ".join(orphan))
    if not seen:
        out.unread.append("not one <Route path=... element={<X />}> was read in web/**/*.tsx")
    else:
        shared = sorted({r for _, r in seen} & {r for s, r in seen if s != sorted({x for x, _ in seen})[0]})
        dupes = sorted({r for s, r in seen} )
        collide = sorted({r for r in dupes if sum(1 for s2, r2 in seen if r2 == r) > 1})
        if collide:
            out.unread.append("routes declared by MORE THAN ONE SPA, and therefore not a "
                              "screen's identity on their own: " + ", ".join(collide))
    return out


DERIVERS = {"db": derive_db, "api": derive_api, "screen": derive_screen}
HEADERS = {
    "db": ("No", "Table", "Owning component", "What it holds", "Key columns", "Status"),
    "api": ("No", "Host", "Method", "Path", "Owning component", "Description", "Status"),
    "screen": ("No", "Screen", "Route", "States", "Owning component", "UC served"),
}


# ------------------------------------------------------- the recorded plan


ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.*)\|\s*$")
FM_RE = re.compile(r"\A---\n(.*?)\n---", re.S)


def decisions(path: Path) -> tuple[dict[str, str], set[str]]:
    """(`states`, `platform_rows`) from frontmatter — the owner's decision, not a pattern result.

    `states` maps a state-route to its parent screen's route. A state is NOT a screen: ux-guide
    already demands every screen have an empty and an error state, so a state is a column on its
    parent's row, not a second row.

    `platform_rows` names rows owned by `_platform`. There is no Product Component promise
    behind them, and corpus-guide owns their two-part test.
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
    """Read the ## Rows section from the recorded inventory. None if the file does not exist yet."""
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
    """Stable identity of a plan row, built the same way as the derived Row.key."""
    out: dict[str, int] = {}
    for number, cells in sorted(rows.items()):
        if kind == "db" and cells:
            out[cells[0].strip("`")] = number
        elif kind == "api" and len(cells) >= 3:
            # The host is part of the identity: one mount function MAY be mounted on more than
            # one host, and without the host in the key the two endpoints collapse into one row.
            out[f"{cells[0]} {cells[1].upper()} {cells[2].strip('`')}"] = number
        elif kind == "screen" and len(cells) >= 2:
            # A screen is written `<spa>/<Component>`; the spa is part of the identity, same as in derivation.
            screen = cells[0].strip("`")
            spa = screen.split("/", 1)[0] if "/" in screen else "?"
            out[f"{spa}:{cells[1].strip('`')}"] = number
    return out


def render_rows(kind: str, derived: Derived, keys: dict[str, int]) -> str:
    """STABLE numbering: a row that already has a number keeps it; a new one takes the next.

    Renumbering means renaming every reference to it afterward and breaking every link that
    points to it, so it MUST NOT be done — even when a row in the middle disappears.
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
        raise SystemExit(f"inventory: {path.as_posix()} has no `## Rows` section — "
                         f"give it birth first from templates/inventory.md")
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
        description="Derive the three inventories from code, then compare against the plan")
    parser.add_argument("--check", action="store_true",
                        help="derive and report; write nothing (default)")
    parser.add_argument("--write", action="store_true",
                        help="rewrite the ## Rows section from the derived result")
    parser.add_argument("--kind", choices=KINDS, action="append",
                        help="restrict to one kind; may be repeated")
    parser.add_argument("--root", default=".", help="repo root (default: current directory)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / ".control" / "registry").is_dir():
        print(f"inventory: {root} has no .control/registry/ — wrong repo root?", file=sys.stderr)
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
            print("  the file does not exist yet. Give it birth from templates/inventory.md; "
                  "until that happens there is no plan to compare against")
        else:
            print(f"  derived_from: {mode} · {len(recorded)} rows recorded")
        print(f"  {len(derived.rows)} rows read from code")

        derived_keys = {row.key for row in derived.rows}
        missing = sorted(set(keys) - derived_keys)      # planned, not present in code
        extra = sorted(derived_keys - set(keys))        # present in code, not planned

        for item in missing:
            print(f"  FINDING  planned but not read in code: {item}")
        for item in extra:
            print(f"  FINDING  present in code but not recorded in the plan: {item}")
        for note in derived.unread:
            print(f"  UNREAD  {note}")
        findings += len(missing) + len(extra)

        if args.write:
            if not path.exists():
                print("  --write skipped: the file does not exist yet")
                continue
            write_rows(path, render_rows(kind, derived, keys))
            print(f"  wrote {rel} — the ## Rows section only")

    print(f"\n{findings} plan-versus-code gaps.")
    if findings:
        print("This gap is a FINDING, not hand work. It is routed to the skill that owns "
              "its side, and MUST NOT be patched over by editing the other side.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

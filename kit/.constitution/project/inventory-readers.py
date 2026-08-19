"""inventory readers — how THIS product's code is read. Owned by the product, not the method.

The engine lives in `.constitution/method/scripts/inventory.py` and is generic: it compares what was
derived against the plan, reports the gap, renders rows, and keeps numbering stable. None of that
depends on a language. Reading the code does — so it lives here, in the room `wdi-method update`
never overwrites and `promote` never publishes.

WHAT THE ENGINE EXPECTS. Three functions, each taking the repo root and returning a `Derived`:

    derive_db(root)      -> Derived    the tables this product stores
    derive_api(root)     -> Derived    the endpoints it serves
    derive_screen(root)  -> Derived    the screens it renders

Three names are INJECTED by the engine before this module executes, so there is nothing to import
for them:

    Row · Derived    what a reader returns. A `Row` carries `key` (its stable identity, used for
                     comparison), `cells` (in the column order the engine renders), and `source`
                     (the file it was read from)
    decisions(path)  an inventory's own `platform_rows:` and `states:`, read from its frontmatter.
                     Those are a judgement no pattern can derive, so they are declared in the
                     artifact they govern

Nothing else is offered. Needing more of the engine means the seam is in the wrong place, and that
is a change to make in the method — not to reach around here.

A kind this product does not have MAY return `Derived()` — no rows, no unread. That is a real
answer, and it is not the same as having no reader at all.

THE RULE THAT DOES NOT CHANGE WITH THE STACK: whatever a pattern cannot read is appended to
`unread` and reported. It MUST NOT be guessed, and it MUST NOT be silently dropped. An inventory
assembled from a README, or from a route name that merely looks plausible, is worth less than none
— it reads as derived while being invented.

WHAT THIS SEED READS. Replace it with your own; it is a starting point, not a standard:
    table     CREATE TABLE statements in src/internal/platform/migrate/migrations/*.sql
    endpoint  route registrations on the Gin router in src/**/*.go
    screen    route components in the React SPA in web/*/src/**/*.tsx
"""

from __future__ import annotations

import re
from pathlib import Path


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


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





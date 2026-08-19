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

WHERE THE STACK LIVES, AND WHY NOT HERE. Comparing, reporting, rendering, and keeping the numbers
stable do not depend on a language. READING the code does — a migration folder, a router, a screen
route are each written differently in every stack. So this file holds none of that. It loads three
functions from the product:

    .constitution/project/inventory-readers.py    derive_db · derive_api · derive_screen

That path is the room: `wdi-method update` never overwrites it and `promote` never publishes it, so
a product owns how its own code is read while every product shares this engine. What the package
seeds there is a SKELETON — no patterns, no stack, and it says so. The `wdi-init` skill, intent
`readers`, writes it against the repo actually in front of it, which is why no example ships: an
example is a guess about somebody else's stack, and guessing is the thing this script exists to
refuse. An unwritten reader is reported, never worked around.

THE STATED-UP-FRONT LIMIT, which no stack changes: this is a pattern reader, not a compiler.
Whatever a reader cannot read is reported as unread — NOT guessed, and NOT silently dropped. An
inventory MUST NOT be assembled from a README or from a route name that merely looks plausible.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

KINDS = ("db", "api", "screen")
READERS = Path(".constitution") / "project" / "inventory-readers.py"

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


# ------------------------------------------------------------- the product's readers


def load_readers(root: Path):
    """Load the product's three readers, or return None if it has not written them.

    Three names are injected BEFORE the module executes, so a reader neither imports them nor
    redeclares them: one definition, and it is this file's. That also means a reader written against
    an older shape fails loudly at import rather than silently producing rows the engine then
    mis-renders.

        Row · Derived    the shape every reader returns
        decisions        an inventory's own `platform_rows:` and `states:`. Those are a judgement
                         the pattern cannot derive, declared in the artifact they govern, so every
                         reader needs them and none should re-implement reading them

    Nothing else is offered. A reader needing more of the engine is a sign the seam is in the wrong
    place, and moving the seam is the fix — not reaching through it.
    """
    file = root / READERS
    if not file.exists():
        return None
    spec = importlib.util.spec_from_file_location("wdi_inventory_readers", file)
    if spec is None or spec.loader is None:
        raise SystemExit(f"inventory: {READERS.as_posix()} could not be loaded as Python")
    mod = importlib.util.module_from_spec(spec)
    # Importing the readers writes .constitution/project/__pycache__/ into the product. A method
    # script MUST NOT leave litter in the repo it was asked to read — and a .pyc is worse than
    # litter: an older CPython stores the absolute path it was compiled from, which is why
    # walkFiles refuses to publish one. A product whose .gitignore lacks __pycache__ would commit
    # it. Turned off here rather than at module level so it is unmistakably about this import.
    sys.dont_write_bytecode = True
    mod.Row, mod.Derived, mod.decisions = Row, Derived, decisions
    spec.loader.exec_module(mod)
    missing = [f"derive_{k}" for k in KINDS if not callable(getattr(mod, f"derive_{k}", None))]
    if missing:
        raise SystemExit(f"inventory: {READERS.as_posix()} defines no {', '.join(missing)} — "
                         f"the engine expects one function per kind, each taking the repo root")
    return mod


def is_skeleton(mod) -> bool:
    """The seeded skeleton announces itself, because silence would be a lie.

    A skeleton returns no rows, and so does a product that genuinely stores no tables. In the
    output those are the same thing — "0 rows read from code" — and only one of them is true. The
    flag is what keeps an unwritten reader from reading as a finished one.
    """
    return bool(getattr(mod, "SKELETON", False))


def shaped(kind: str, result) -> Derived:
    """Refuse a reader's answer that is not the shape the engine renders.

    A reader is the product's code, so it is the one part of this run the method did not write.
    Checking its shape here turns a wrong return into one clear sentence, rather than a
    TypeError thrown from inside render_rows with no clue whose fault it was.
    """
    rows = getattr(result, "rows", None)
    unread = getattr(result, "unread", None)
    if not isinstance(rows, list) or not isinstance(unread, list):
        raise SystemExit(f"inventory: derive_{kind} returned {type(result).__name__}, "
                         f"which carries no `rows` and `unread` lists")
    for row in rows:
        if not all(hasattr(row, attr) for attr in ("key", "cells", "source")):
            raise SystemExit(f"inventory: derive_{kind} returned a row without key, cells, "
                             f"and source — see the contract in {READERS.as_posix()}")
    return result


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

    readers = load_readers(root)
    # NOT an error, and NOT a reason to guess. A product that has not written its readers has said
    # nothing about how its code is read, and inventing an answer here is the one failure this
    # script exists to prevent. Both states get the same refusal and the same next step.
    if readers is None or is_skeleton(readers):
        state = ("has no" if readers is None else "still has the seeded skeleton at")
        print(f"inventory: this product {state} {READERS.as_posix()}, so nothing can be derived "
              f"from code.\n"
              f"  The engine is generic; reading a stack is not. Write the three readers for this "
              f"repo with\n"
              f"  the `wdi-init` skill, intent `readers` — it reads the code in front of it rather "
              f"than\n"
              f"  starting from somebody else's stack.", file=sys.stderr)
        return 2

    kinds = args.kind or list(KINDS)
    findings = 0

    for kind in kinds:
        path = root / f".how/_platform/inventory-{kind}.md"
        rel = path.relative_to(root).as_posix()
        derived = shaped(kind, getattr(readers, f"derive_{kind}")(root))
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

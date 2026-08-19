"""inventory readers — how THIS product's code is read. Owned by the product, not the method.

THIS FILE IS A SKELETON. It reads nothing yet, and it says so rather than reporting an empty
product: `SKELETON = True` below makes the engine refuse to run until the readers are written.
Delete that line when they are.

Write them with the skill rather than by hand:

    wdi-init  intent `readers`

That skill reads this repo — its migrations, its routes, its screens, whatever shape they take —
and fills the three functions in for the stack actually in front of it. It is the right way round:
the package ships no stack, and no example to be mistaken for one.

The whole file is yours. `wdi-method update` never writes over it and `promote` never publishes it,
so there is nothing here marked off-limits and nothing to merge. The engine —
`.constitution/method/scripts/inventory.py` — is the method's and is replaced on every update.
That is the seam: a folder, not a marked region inside a shared file.

WHAT THE ENGINE EXPECTS. Three functions, each taking the repo root and returning a `Derived`:

    derive_db(root)      -> Derived    the tables this product stores
    derive_api(root)     -> Derived    the endpoints it serves
    derive_screen(root)  -> Derived    the screens it renders

Three names are INJECTED before this module executes, so import nothing for them:

    Row(key, cells, source)   one row. `key` is its stable identity, used for comparison; `cells`
                              are in the column order the engine renders; `source` is the file it
                              was read from
    Derived(rows, unread)     what a reader returns
    decisions(path)           an inventory's own `states:` and `platform_rows:`, read from its
                              frontmatter — a judgement no pattern can derive, so it is declared in
                              the artifact it governs

Nothing else is offered. Needing more of the engine means the seam is in the wrong place, and that
is a change to make in the method — not to reach around here.

THE COLUMN ORDER `cells` MUST FOLLOW:

    db      Table · Owning component · What it holds · Key columns · Status
    api     Host · Method · Path · Owning component · Description · Status
    screen  Screen · Route · States · Owning component · UC served

(The leading `No` is the engine's; it keeps the numbering stable and a reader MUST NOT supply it.)

THE RULE THAT NO STACK CHANGES: whatever a pattern cannot read is appended to `unread` and
reported. It MUST NOT be guessed, and it MUST NOT be silently dropped. An inventory assembled from
a README, or from a route name that merely looks plausible, is worth less than none — it reads as
derived while being invented.

A kind this product genuinely does not have MAY return `Derived()`. That is a real answer, and it
is not the same as this file still being a skeleton.
"""

from __future__ import annotations

from pathlib import Path

# Delete this line once the three functions below actually read something. While it is here the
# engine refuses to run, because a skeleton returning nothing and a product owning nothing look
# identical in the output — and only one of them is true.
SKELETON = True


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def derive_db(root: Path) -> "Derived":       # noqa: F821 — injected by the engine
    """Every table this product stores, from wherever its schema actually lives."""
    return Derived(unread=["derive_db has not been written for this product yet"])


def derive_api(root: Path) -> "Derived":      # noqa: F821 — injected by the engine
    """Every endpoint this product serves, from wherever its routes are registered."""
    return Derived(unread=["derive_api has not been written for this product yet"])


def derive_screen(root: Path) -> "Derived":   # noqa: F821 — injected by the engine
    """Every screen this product renders, from wherever its routes are declared."""
    return Derived(unread=["derive_screen has not been written for this product yet"])

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""validate — V1..V27 plus the .control/generated/ generator.

Two modes:
    validate --check      exit non-zero if anything is red; writes nothing
    validate --generate   rewrite .control/generated/ (and still runs --check)

Determinism is the contract: two runs over the same data MUST produce the same result.
That is why there is no unordered iteration, and the one time-dependent input
(--asof, used by V14) is stated explicitly instead of being taken silently from the wall clock.

What is NOT done here: the time dimension from git. `generated/timeline` and
`generated/report` belong to wdi-report. See 08-project-management.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REGISTRY = "control/registry"  # tidied up in resolve(); '.control' is what is actually used
GENERATED_ORDER = ["components", "risks", "dag", "rtm", "status"]

# Pages read by HUMANS, not machines: written as real markdown tables, not yaml
# in a fence. All three are named in §22 and each has one clear reader.
GENERATED_PAGES = ["decisions", "blueprint", "estimate"]

MODES = ("catalog", "outline", "guarded", "deep")

# Keywords that make a component "sensitive" for V23. Matched against `risk_note`, which is PROSE in
# whatever `policy.doc_language` the product chose — so the set is the UNION of both languages rather
# than a translation. It leans toward disclosing more, which is what this check is for: it discloses,
# it does not judge. Deliberately short.
SENSITIVE_MARKERS = (
    # English
    "money", "payment", "personal data", "pii",
    "irreversible", "cannot be undone", "contractual", "contract", "integration",
    # Bahasa Indonesia
    "uang", "pembayaran", "data pribadi",
    "tak-terbalikkan", "tak terbalikkan", "tidak dapat dibatalkan",
    "kontraktual", "kontrak", "integrasi",
)


# ---------------------------------------------------------------- infrastructure


@dataclass(frozen=True)
class Finding:
    vid: str
    subject: str
    message: str

    @property
    def sort_key(self) -> tuple[int, str, str]:
        digits = "".join(ch for ch in self.vid if ch.isdigit())
        return (int(digits or 0), self.subject, self.message)


@dataclass
class Result:
    findings: list[Finding] = field(default_factory=list)
    skipped: dict[str, str] = field(default_factory=dict)

    def fail(self, vid: str, subject: str, message: str) -> None:
        self.findings.append(Finding(vid, subject, message))

    def skip(self, vid: str, why: str) -> None:
        self.skipped[vid] = why

    @property
    def red(self) -> list[str]:
        return sorted({f.vid for f in self.findings})


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def rows(data: dict, key: str) -> list[dict]:
    """Registry list, always sorted by id so the output is deterministic."""
    value = data.get(key) or []
    if not isinstance(value, list):
        return []
    items = [v for v in value if isinstance(v, dict)]
    return sorted(items, key=lambda r: str(r.get("id", "")))


FM = re.compile(r"\A---\s*\n(.*?)\n---\s*(\n|\Z)", re.S)


class Dumper(yaml.SafeDumper):
    """No anchors/aliases: output MUST be readable and diffable line by line."""

    def ignore_aliases(self, data) -> bool:  # noqa: ARG002
        return True


def dump(payload: dict) -> str:
    return yaml.dump(payload, Dumper=Dumper, allow_unicode=True, sort_keys=False,
                     default_flow_style=False, width=100)


def frontmatter(path: Path) -> dict | None:
    """None if the file does not exist; {} if it exists but has no frontmatter."""
    if not path.exists():
        return None
    match = FM.match(path.read_text(encoding="utf-8", errors="replace"))
    if not match:
        return {}
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else {}


def git(root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


# ------------------------------------------------------------------- loading


@dataclass
class Corpus:
    root: Path
    requirements: dict
    usecases: dict
    decisions: dict
    risks: dict
    components: dict
    waves: dict
    defects: dict
    index: dict

    @classmethod
    def load(cls, root: Path) -> "Corpus":
        reg = root / ".control" / "registry"
        return cls(
            root=root,
            requirements=load_yaml(reg / "requirements.yaml"),
            usecases=load_yaml(reg / "usecases.yaml"),
            decisions=load_yaml(reg / "decisions.yaml"),
            risks=load_yaml(reg / "risks.yaml"),
            components=load_yaml(reg / "components.yaml"),
            waves=load_yaml(reg / "waves.yaml"),
            defects=load_yaml(reg / "defects.yaml"),
            index=load_yaml(reg / "index.yaml"),
        )

    # --- shortcuts used repeatedly
    @property
    def goals(self) -> list[dict]:
        return rows(self.requirements, "goals")

    @property
    def caps(self) -> list[dict]:
        return rows(self.requirements, "capabilities")

    @property
    def frs(self) -> list[dict]:
        return rows(self.requirements, "functional")

    @property
    def nfrs(self) -> list[dict]:
        return rows(self.requirements, "nonfunctional")

    @property
    def ucs(self) -> list[dict]:
        return rows(self.usecases, "usecases")

    @property
    def decs(self) -> list[dict]:
        return rows(self.decisions, "decisions")

    def mode_of(self, pc: dict) -> str:
        """Per-component `mode` wins over the global one; with neither, default `catalog`."""
        own = str(pc.get("mode") or "").strip()
        if own:
            return own
        return str(self.index.get("mode") or "").strip() or "catalog"

    @property
    def lcs(self) -> list[dict]:
        return rows(self.components, "logical_components")

    @property
    def pcs(self) -> list[dict]:
        return rows(self.components, "product_components")

    @property
    def wave_list(self) -> list[dict]:
        return rows(self.waves, "waves")

    @property
    def defect_list(self) -> list[dict]:
        return rows(self.defects, "defects")

    def stories(self) -> list[tuple[dict, dict, dict]]:
        """(wave, epic, story) — sorted by id at each level."""
        out = []
        for wave in self.wave_list:
            for epic in sorted(wave.get("epics") or [], key=lambda e: str(e.get("id", ""))):
                if not isinstance(epic, dict):
                    continue
                for story in sorted(epic.get("stories") or [], key=lambda s: str(s.get("id", ""))):
                    if isinstance(story, dict):
                        out.append((wave, epic, story))
        return out


def listy(row: dict, key: str) -> list[str]:
    value = row.get(key) or []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value if v is not None]


# ------------------------------------------------------------------ validators


def v1(c: Corpus, r: Result) -> None:
    """Every BG has >=1 FR through its CAP, OR states its reason in `no_fr`.

    A goal MAY be satisfied by an **invariant** rather than a feature. `BG-6` — the data and
    deployment foundation can be extended without being torn down — is measured by two architectural
    properties that its own `measure` names, and no `FR` can carry it without being invented. Demanding
    one `FR` there produces a false promise, and a false promise is more expensive than a finding.

    The escape MUST carry a reason, not a boolean — the same shape as `no_uc` on `FR` (V2).
    """
    cap_by_goal: dict[str, list[str]] = {}
    for cap in c.caps:
        cap_by_goal.setdefault(str(cap.get("goal", "")), []).append(str(cap.get("id")))
    fr_caps = {str(fr.get("capability", "")) for fr in c.frs}
    for goal in c.goals:
        gid = str(goal.get("id"))
        reachable = [cid for cid in cap_by_goal.get(gid, []) if cid in fr_caps]
        if reachable:
            continue
        if str(goal.get("no_fr") or "").strip():
            continue
        r.fail("V1", gid, "has no FR through its CAP and states no reason in `no_fr`")


def v2(c: Corpus, r: Result) -> None:
    covered = {fr for uc in c.ucs for fr in listy(uc, "satisfies")}
    for fr in c.frs:
        fid = str(fr.get("id"))
        if fid in covered:
            continue
        if str(fr.get("no_uc") or "").strip():
            continue
        r.fail("V2", fid, "has no UC and states no reason in `no_uc`")


def v3(c: Corpus, r: Result) -> None:
    """A UC on a component that a wave has ALREADY touched MUST be scheduled to a story.

    The old shape demanded this of EVERY UC, at any time. Before the first wave that meant the
    entire catalogue was reported red — 56 findings out of 62, and those 56 were the correct state,
    not drift: a story is born in a wave, and there was no wave yet. A validator that drowns six real
    findings under fifty-six expected ones stops being read, and a validator that is not read
    guards nothing.

    What is guarded now is the actual omission: a wave touches a component, and a UC of that
    component is left behind without a story. Full coverage of the whole catalogue is a G5 question,
    and `wdi-build` owns it — the same way V12 was shifted to wave closing.
    """
    scheduled = {uc for _, _, s in c.stories() for uc in listy(s, "satisfies")}
    touched = {str(s.get("component")) for _, _, s in c.stories() if s.get("component")}
    if not c.wave_list:
        r.skip("V3", "no wave yet, so no story yet — every unscheduled UC is the correct "
                     "state. Full catalogue coverage is checked at G5")
        return
    for uc in c.ucs:
        uid = str(uc.get("id"))
        if uid in scheduled or str(uc.get("component")) not in touched:
            continue
        r.fail("V3", uid, f"component `{uc.get('component')}` has already been touched by a wave, "
                          f"but this UC is not scheduled to any story")


def v4(c: Corpus, r: Result) -> None:
    for _, _, story in c.stories():
        if not [t for t in listy(story, "tests") if t.strip()]:
            r.fail("V4", str(story.get("id")), "has not one named test")


def v5(c: Corpus, r: Result) -> None:
    """Every NFR has an enforcer, OR states its reason in `no_enforcer`.

    Two NFRs in this repo cannot have an enforcer, and both are valid: one has already been
    **retired**, and the other states of itself that it is a **design measure, not a gate**. Demanding
    a test for both produces a test that cannot fail, and a test that cannot fail is theater.
    """
    for nfr in c.nfrs:
        if [e for e in listy(nfr, "enforced_by") if e.strip()]:
            continue
        if str(nfr.get("no_enforcer") or "").strip():
            continue
        r.fail("V5", str(nfr.get("id")),
               "has no enforcer in `enforced_by` and states no reason in `no_enforcer`")


def v6(c: Corpus, r: Result) -> None:
    defined: set[str] = set()
    for group in (c.goals, c.caps, c.frs, c.nfrs, c.ucs, c.decs, c.lcs, c.pcs,
                  rows(c.requirements, "journeys"), rows(c.risks, "risks"), c.defect_list):
        defined |= {str(row.get("id")) for row in group if row.get("id") is not None}
    for wave in c.wave_list:
        defined.add(str(wave.get("id")))
    for _, epic, story in c.stories():
        defined.add(str(epic.get("id")))
        defined.add(str(story.get("id")))

    refs: list[tuple[str, str]] = []
    for cap in c.caps:
        refs.append((str(cap.get("id")), str(cap.get("goal", ""))))
        refs += [(str(cap.get("id")), d) for d in listy(cap, "depends_on")]
    for fr in c.frs:
        refs.append((str(fr.get("id")), str(fr.get("capability", ""))))
    for nfr in c.nfrs:
        refs.append((str(nfr.get("id")), str(nfr.get("goal", ""))))
    for uc in c.ucs:
        refs += [(str(uc.get("id")), f) for f in listy(uc, "satisfies")]
    for dec in c.decs:
        refs += [(str(dec.get("id")), s) for s in listy(dec, "serves")]
    for defect in c.defect_list:
        refs += [(str(defect.get("id")), v) for v in listy(defect, "violates")]
    for _, _, story in c.stories():
        refs += [(str(story.get("id")), u) for u in listy(story, "satisfies")]
        refs += [(str(story.get("id")), d) for d in listy(story, "depends_on")]

    for owner, target in sorted(set(refs)):
        if target and target not in defined:
            r.fail("V6", owner, f"points to `{target}` which does not exist in any registry")


def _cycles(graph: dict[str, list[str]]) -> list[str]:
    state: dict[str, int] = {}
    bad: list[str] = []

    def walk(node: str) -> None:
        state[node] = 1
        for nxt in sorted(graph.get(node, [])):
            if state.get(nxt) == 1:
                bad.append(node)
            elif state.get(nxt) is None and nxt in graph:
                walk(nxt)
        state[node] = 2

    for node in sorted(graph):
        if state.get(node) is None:
            walk(node)
    return sorted(set(bad))


def v7(c: Corpus, r: Result) -> None:
    caps = {str(x.get("id")): listy(x, "depends_on") for x in c.caps}
    for node in _cycles(caps):
        r.fail("V7", node, "is part of a `depends_on` cycle among CAPs")
    stories = {str(s.get("id")): listy(s, "depends_on") for _, _, s in c.stories()}
    for node in _cycles(stories):
        r.fail("V7", node, "is part of a `depends_on` cycle among stories")


def v8(c: Corpus, r: Result) -> None:
    """Every `applied` decision names a non-empty `touches`.

    Replaces the old shape "every accepted decision serves >=1 FR/NFR". A decision like
    "the filter MUST work like this" serves no FR at all, and that is VALID — it is exactly
    decisions like that which most need remembering, and the old rule discarded them.
    """
    for dec in c.decs:
        if str(dec.get("status")) != "applied":
            continue
        if not [x for x in listy(dec, "touches") if str(x).strip()]:
            r.fail("V8", str(dec.get("id")),
                   "is applied but `touches` is empty — an application with no file trace")


def v9(c: Corpus, r: Result) -> None:
    passed = {str(g) for g in (c.index.get("gates_passed") or [])}
    for path in sorted(c.root.glob(".what/**/*.md")) + sorted(c.root.glob(".how/**/*.md")):
        fm = frontmatter(path) or {}
        if str(fm.get("status")) != "locked":
            continue
        gate = str(fm.get("locked_at_gate") or "")
        if gate not in passed:
            rel = path.relative_to(c.root).as_posix()
            r.fail("V9", rel, f"is locked but gate `{gate or '?'}` is not recorded as passed")


def v11(c: Corpus, r: Result) -> None:
    per_wave: dict[str, list[dict]] = {}
    for wave, _, story in c.stories():
        per_wave.setdefault(str(wave.get("id")), []).append(story)

    for wid in sorted(per_wave):
        items = per_wave[wid]
        edges = {str(s.get("id")): set(listy(s, "depends_on")) for s in items}

        def reaches(a: str, b: str, seen: set[str] | None = None) -> bool:
            seen = seen or set()
            if a in seen:
                return False
            seen.add(a)
            if b in edges.get(a, set()):
                return True
            return any(reaches(n, b, seen) for n in sorted(edges.get(a, set())))

        for i, left in enumerate(items):
            for right in items[i + 1:]:
                lid, rid = str(left.get("id")), str(right.get("id"))
                shared = sorted(set(listy(left, "touches")) & set(listy(right, "touches")))
                if not shared:
                    continue
                if reaches(lid, rid) or reaches(rid, lid):
                    continue
                r.fail("V11", f"{lid} + {rid}",
                       f"share touches {shared} with no depends_on relation — MUST NOT run in parallel")


def v12(c: Corpus, r: Result) -> None:
    """LC registration is checked when a wave CLOSES, not before a story goes `ready-for-dev`.

    The old shape demanded the answer when the information was thinnest. At wave closing,
    every `touches` already has an area and every boundary already has a name.
    """
    areas = {str(lc.get("area")) for lc in c.lcs if lc.get("area")}
    lcs_per_pc: dict[str, int] = {}
    for lc in c.lcs:
        lcs_per_pc[str(lc.get("component"))] = lcs_per_pc.get(str(lc.get("component")), 0) + 1
    pc_by_id = {str(x.get("id")): x for x in c.pcs}

    seen: set[tuple[str, str]] = set()
    for wave, _, story in c.stories():
        if str(wave.get("status")) != "closed":
            continue
        for area in listy(story, "touches"):
            if area not in areas:
                r.fail("V12", str(story.get("id")),
                       f"its wave is already closed, but `{area}` is not registered as an `area` "
                       f"in components.yaml")
        pid = str(story.get("component") or "")
        row = pc_by_id.get(pid)
        if row is None or (str(wave.get("id")), pid) in seen:
            continue
        seen.add((str(wave.get("id")), pid))
        if c.mode_of(row) in ("guarded", "deep") and not lcs_per_pc.get(pid):
            r.fail("V12", f"{wave.get('id')} / {pid}",
                   f"wave closed and component with mode `{c.mode_of(row)}` has not one "
                   f"`LC` registered")


LENS_BY_RISK = {
    "low": {"edge-case-hunter"},
    "medium": {"edge-case-hunter"},
    "high": set(),
}
FRONTMATTER_KEYS = ("reviewed:", "date:", "sha:", "lenses:", "updated:")


def _reviewed_ok(r: Result, rel: str, block: object, need: set[str]) -> None:
    # str() before the truth test: an unquoted sha of all digits — `0000000`, and roughly one
    # short sha in twenty-seven is all digits — is read by YAML as the INTEGER 0, which is falsy.
    # The old test then reported "carries no reviewed trace" about a file that plainly carries one,
    # which is the worst kind of finding: correct-looking, and wrong.
    if not isinstance(block, dict):
        r.fail("V13", rel, "carries no `reviewed` trace with a date and sha")
        return
    # NOT `block.get("sha") or ""` — for the integer 0 that yields "" and reintroduces the very
    # bug this guards. `.get(key, "")` returns the 0, and str(0) is "0", which is truthy.
    if not str(block.get("sha", "")).strip() or not str(block.get("date", "")).strip():
        r.fail("V13", rel, "carries no `reviewed` trace with a date and sha")
        return
    lenses = {str(x) for x in (block.get("lenses") or [])}
    if not lenses:
        r.fail("V13", rel, "the `reviewed` trace names not one lens")
    missing = sorted(need - lenses)
    if missing:
        r.fail("V13", rel,
               f"lenses {missing} MUST be included — that is what the component's `risk_accepted` demands")


def _only_reviewed_block(diff: str) -> bool:
    """True if a commit's diff on one file ONLY touches the `reviewed:` block.

    This is the OQ-146 fix. The old V13 compared `sha` against the last commit that changed
    the file — but the commit that WRITES the `reviewed:` block always changes the file, and
    writing its own hash into a git commit is cryptographically impossible. As a result every
    artifact that had just been stamped immediately read as "stale review", forever.
    """
    touched = [ln for ln in diff.splitlines()
               if ln[:1] in "+-" and not ln.startswith("+++") and not ln.startswith("---")]
    if not touched:
        return True
    for ln in touched:
        body = ln[1:].strip()
        if not body or body.startswith("#"):
            continue
        if not body.startswith(FRONTMATTER_KEYS):
            return False
    return True


def _stale_since(c: Corpus, rel: str, sha: str) -> str | None:
    """First commit after `sha` that changes this file for a reason other than a review stamp."""
    log = git(c.root, "log", "--format=%H", f"{sha}..HEAD", "--", rel)
    if not log:
        return None
    for head in log.splitlines():
        head = head.strip()
        if not head:
            continue
        diff = git(c.root, "show", "--format=", "--unified=0", head, "--", rel)
        if diff is None:
            return head
        if _only_reviewed_block(diff):
            continue
        return head
    return None


def v13(c: Corpus, r: Result) -> None:
    """Review trace follows review INTENSITY, not document depth.

    Narrowed to components with `risk_accepted` `low` or `medium`. At `high` the owner has already
    stated they accept the risk, and demanding a trace there is bookkeeping with no buyer.
    """
    watched = [pc for pc in c.pcs
               if str(pc.get("risk_accepted") or "").strip() in ("low", "medium")]
    if not watched:
        r.skip("V13", "no component with risk_accepted low or medium — nothing to guard")
    targets: list[tuple[Path, set[str]]] = []
    if watched:
        targets.append((c.root / ".how/_platform/ARCHITECTURE-SPINE.md", set()))
    for pc in watched:
        pid = str(pc.get("id"))
        need = LENS_BY_RISK.get(str(pc.get("risk_accepted")).strip(), set())
        # The SRS exists and is meaningful at EVERY mode: it carries the Actor Register and UC
        # Catalogue, and both are born at G3, which the depth knob does not touch.
        targets.append((c.root / f".what/{pid}/SRS-{pid}.md", need))
        # The SDD is guarded only when it HAS content worth guarding. Two states exempt it, and
        # both are FINISHED states, not neglected ones:
        #   mode: catalog        the skeleton is its final form; G4 is skipped there
        #   g4_passed not set    G4 has not run yet, so not one section is written
        # Demanding a review trace on a file whose content is 13 lines of template comments is
        # theater — exactly the ceremony this redesign cut, and a review that cannot fail proves
        # nothing. Once G4 passes, the demand comes back and it is meaningful.
        passed = str(pc.get("g4_passed") or "").strip().lower()
        if c.mode_of(pc) != "catalog" and passed not in ("", "false", "no", "belum"):
            targets.append((c.root / f".how/{pid}/SDD-{pid}.md", need))

    for path, need in targets:
        fm = frontmatter(path)
        if fm is None:
            continue  # not born yet — not V13's business
        rel = path.relative_to(c.root).as_posix()
        _reviewed_ok(r, rel, fm.get("reviewed"), need)
        block = fm.get("reviewed")
        if isinstance(block, dict) and block.get("sha"):
            stale = _stale_since(c, rel, str(block["sha"]))
            if stale:
                r.fail("V13", rel,
                       f"changed at {stale[:7]} after being reviewed at {str(block['sha'])[:7]} — "
                       f"stale review")

    for wave in c.wave_list:
        if not wave.get("epics"):
            continue
        _reviewed_ok(r, f"waves.yaml:{wave.get('id')}", wave.get("spec_reviewed"),
                     {"edge-case-hunter"})


def cap_stories(c: Corpus) -> dict[str, list[dict]]:
    """CAP -> story, traced through CAP -> FR -> UC -> story. No git, no timeline."""
    frs_of: dict[str, list[str]] = {}
    for fr in c.frs:
        frs_of.setdefault(str(fr.get("capability", "")), []).append(str(fr.get("id")))
    ucs_of: dict[str, list[str]] = {}
    for uc in c.ucs:
        for fid in listy(uc, "satisfies"):
            ucs_of.setdefault(fid, []).append(str(uc.get("id")))
    out: dict[str, list[dict]] = {}
    for cap in c.caps:
        cid = str(cap.get("id"))
        wanted = {u for fid in frs_of.get(cid, []) for u in ucs_of.get(fid, [])}
        out[cid] = [s for _, _, s in c.stories()
                    if wanted & set(listy(s, "satisfies"))]
    return out


def v14(c: Corpus, r: Result, asof: dt.date) -> None:
    """Overdue-ness is computed from the registry itself — the timeline only reinforces, never gates."""
    by_cap = cap_stories(c)
    timeline = load_yaml(c.root / ".control/generated/timeline.yaml")
    listed = {str(row.get("id")) for row in rows(timeline, "capabilities")
              if str(row.get("state")) == "overdue"} if timeline else None
    if listed is None:
        r.skip("V14", "generated/timeline.yaml does not exist yet — overdue-ness is still computed "
                      "from the registry, but its presence in generated/report is not checked")

    for cap in c.caps:
        cid = str(cap.get("id"))
        end = str(cap.get("planned_end") or "")
        if not end:
            continue
        try:
            due = dt.date.fromisoformat(end)
        except ValueError:
            r.fail("V14", cid, f"`planned_end` `{end}` is not an ISO date")
            continue
        items = by_cap.get(cid, [])
        closed = bool(items) and all(_story_status(c, s) == "done" for s in items)
        if closed or due >= asof:
            continue
        late = (asof - due).days
        if listed is not None and cid not in listed:
            r.fail("V14", cid, f"{late} days overdue with nothing delivered, and not flagged "
                               f"`overdue` in generated/timeline")
        else:
            r.fail("V14", cid, f"{late} days overdue with nothing closed")


def v15(c: Corpus, r: Result) -> None:
    for cap in c.caps:
        if not str(cap.get("goal") or "").strip():
            r.fail("V15", str(cap.get("id")), "does not point to a `goal`")
    for fr in c.frs:
        if not str(fr.get("capability") or "").strip():
            r.fail("V15", str(fr.get("id")), "does not point to a `capability`")


def v16(c: Corpus, r: Result) -> None:
    for path in sorted((c.root / ".control/memlog").glob("*.md")):
        fm = frontmatter(path) or {}
        rel = path.relative_to(c.root).as_posix()
        artifact = str(fm.get("artifact") or "")
        if not artifact:
            r.fail("V16", rel, "has no `artifact:` in frontmatter")
        elif not (c.root / artifact).exists():
            r.fail("V16", rel, f"`artifact:` points to `{artifact}` which does not exist")
    for layer in (".what", ".how"):
        for stray in sorted(c.root.glob(f"{layer}/**/.memlog.md")):
            r.fail("V16", stray.relative_to(c.root).as_posix(),
                   "a memlog MUST NOT live inside the corpus")


def v17(c: Corpus, r: Result) -> None:
    for wave in c.wave_list:
        wid = str(wave.get("id"))
        if not str(wave.get("release") or "").strip():
            r.fail("V17", wid, "does not name a `release`")
        slugs = listy(wave, "prd")
        if not slugs:
            r.fail("V17", wid, "does not name a `prd`")
        for slug in slugs:
            if not (c.root / ".what/_prd" / slug).is_dir():
                r.fail("V17", wid, f"`prd: {slug}` has no folder .what/_prd/{slug}/")


def v18(c: Corpus, r: Result) -> None:
    for _, _, story in c.stories():
        sid = str(story.get("id"))
        folder = str(story.get("spec_folder") or "").strip()
        if not folder:
            r.fail("V18", sid, "does not name a `spec_folder`")
            continue
        matches = sorted((c.root / folder / "stories").glob(f"{sid}-*.md"))
        if not matches:
            r.fail("V18", sid, f"has no story file in {folder}stories/")
            continue
        fm = frontmatter(matches[0]) or {}
        if not str(fm.get("status") or "").strip():
            r.fail("V18", sid, "story file has no `status` in frontmatter")


def v19(c: Corpus, r: Result) -> None:
    """The retrospective archive is tied to WAVE SIZE, not to `mode`.

    Mandatory on wave `L`; advisory on `S` and `M`. Document depth and volume of work are two
    different things, and demanding a retrospective for a three-story wave is ceremony.
    """
    names = [x.name for x in sorted((c.root / ".control/reports").glob("RTR-*"))]
    advisory: list[str] = []
    for wave in c.wave_list:
        if str(wave.get("status")) != "closed":
            continue
        wid = str(wave.get("id"))
        if any(wid in name for name in names):
            continue
        if str(wave.get("size")).upper() == "L":
            r.fail("V19", wid, "wave `L` closed without an `RTR-` in .control/reports/")
        else:
            advisory.append(wid)
    if advisory:
        r.skip("V19", "advisory — wave S/M closed without an RTR-: " + ", ".join(sorted(advisory)))
    else:
        r.skip("V19", "only the RTR- line item is checked mechanically; the rest of the distillation is guarded by wdi-build")


PLATFORM = "_platform"
CROSS_CUTTING = ".how/_platform/cross-cutting.md"
# The section heading V21 looks for. A heading a SCRIPT matches is a machine-facing key, and
# `language-guide.md` says a key is always English — so the template writes the English one and
# this is what a new corpus carries. The Indonesian form is kept as a READER-side alias, exactly
# like `yes|ya`: a corpus written before this MUST NOT be migrated for a regex.
PLATFORM_DATA_HEADINGS = ("Platform-owned", "Milik platform")
PLATFORM_DATA_HEADING = PLATFORM_DATA_HEADINGS[0]


def v21(c: Corpus, r: Result) -> None:
    """One domain entity has EXACTLY ONE owner authorized to write it.

    The owner is a Product Component, OR `_platform` for an entity with no single component
    promise behind it. Semantic collisions across PRDs have already happened for real: one
    component took a business-rule numbering range from a shared global sequence. Two `FR`s
    that both claim write authority over the same entity, with neither pointing at the other,
    are a defect the moment they are written.

    `_platform` is NOT a Product Component and therefore has no `mode`, `risk_accepted`, SRS,
    or G4. It is a home for ownership, not a domain slice — and so it does not become a dumping
    ground, every entity it claims MUST be explained in `cross-cutting.md`: if the platform
    owns the data, the platform documents it.
    """
    owner: dict[str, str] = {}
    for pc in c.pcs:
        pid = str(pc.get("id"))
        for entity in listy(pc, "owns"):
            if entity in owner and owner[entity] != pid:
                r.fail("V21", entity,
                       f"claimed as `owns` by both `{owner[entity]}` and `{pid}` — one entity MUST "
                       f"have exactly one owner")
            else:
                owner.setdefault(entity, pid)

    platform = listy(c.components, "platform_owns")
    for entity in platform:
        if entity in owner:
            r.fail("V21", entity,
                   f"claimed as `platform_owns` and also as `owns` by `{owner[entity]}` — "
                   f"`{PLATFORM}` is not a second path for an entity that already has an owner")
        else:
            owner[entity] = PLATFORM

    _platform_documented(c, r, platform + _platform_inventory_rows(c))

    cap_home = {str(x.get("id")): str(x.get("component") or "") for x in c.caps}
    for fr in c.frs:
        fid = str(fr.get("id"))
        home = str(fr.get("component") or cap_home.get(str(fr.get("capability", "")), ""))
        for entity in listy(fr, "writes"):
            own = owner.get(entity)
            if not own or not home or own == home:
                continue
            if own == PLATFORM:
                # The platform has no `FR`, so there is nothing a `defers_to` could point to. What
                # stands in for "one writer" here is ONE DOCUMENTED FORM, and that is what
                # _platform_documented checks above.
                continue
            if not [d for d in listy(fr, "defers_to") if str(d).strip()]:
                r.fail("V21", fid,
                       f"promises to write `{entity}` which `{own}` owns, without `defers_to` "
                       f"pointing to an `FR` owned by that owner")


def _platform_inventory_rows(c: Corpus) -> list[str]:
    """Inventory rows owned by `_platform`, read from `platform_rows:` in each inventory.

    `_platform` is a valid value at EVERY ownership position, so the guard applies at every
    position too: whatever it owns MUST be documented in `cross-cutting.md`.
    """
    out: list[str] = []
    for kind in ("db", "api", "screen"):
        path = c.root / f".how/_platform/inventory-{kind}.md"
        fm = frontmatter(path)
        if not fm:
            continue
        out += [str(x) for x in (fm.get("platform_rows") or [])]
    return out


def _platform_documented(c: Corpus, r: Result, entities: list[str]) -> None:
    """Every entity with `platform_owns` MUST be named in `cross-cutting.md`.

    Skipped while the file does not yet carry that section: `cross-cutting.md` is a G3 output, and
    an artifact the next gate will produce MUST NOT be reported missing.
    """
    if not entities:
        return
    path = c.root / CROSS_CUTTING
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    if not any(h.lower() in text.lower() for h in PLATFORM_DATA_HEADINGS):
        r.skip("V21", f"`{CROSS_CUTTING}` has no `{PLATFORM_DATA_HEADING}` section yet — "
                      f"{len(entities)} entities with platform_owns are not documented yet: "
                      + ", ".join(sorted(entities)))
        return
    for entity in sorted(entities):
        if entity not in text:
            r.fail("V21", entity,
                   f"claimed as `platform_owns` but not named in `{CROSS_CUTTING}` — "
                   f"a platform that owns data MUST document it")


def v22(c: Corpus, r: Result) -> None:
    """A wave MUST NOT touch a component whose G4 has not passed and whose mode is not catalog.

    `catalog` skips G4 on purpose, so it is not an exception — it is part of the rule.
    """
    pc_by_id = {str(x.get("id")): x for x in c.pcs}
    seen: set[tuple[str, str]] = set()
    for wave, _, story in c.stories():
        pid = str(story.get("component") or "")
        row = pc_by_id.get(pid)
        if row is None:
            continue
        key = (str(wave.get("id")), pid)
        if key in seen:
            continue
        seen.add(key)
        mode = c.mode_of(row)
        if mode == "catalog":
            continue
        if mode not in MODES:
            r.fail("V22", pid, f"`mode: {mode}` is not one of {list(MODES)}")
            continue
        passed = row.get("g4_passed")
        if not passed or str(passed).strip().lower() in ("false", "no", "belum"):
            r.fail("V22", f"{wave.get('id')} / {pid}",
                   f"wave touches a component with mode `{mode}` whose `g4_passed` has not been set")


def v23(c: Corpus, r: Result) -> None:
    """`risk_accepted: high` on a sensitive component demands a `DEC-` in `risk_accepted_by`.

    On a component that touches nothing on that list, `high` is FREE. The control is
    disclosure, not veto — the owner may still choose quickly, just not without knowing what
    they are wagering.
    """
    known = {str(x.get("id")) for x in c.decs}
    for pc in c.pcs:
        pid = str(pc.get("id"))
        if str(pc.get("risk_accepted") or "").strip() != "high":
            continue
        note = str(pc.get("risk_note") or "").lower()
        hits = sorted({m for m in SENSITIVE_MARKERS if m in note})
        if not hits:
            continue
        ref = str(pc.get("risk_accepted_by") or "").strip()
        if not ref:
            r.fail("V23", pid,
                   f"`risk_accepted: high` while `risk_note` mentions {hits}, without "
                   f"`risk_accepted_by` pointing to a risk-acceptance `DEC-`")
        elif ref not in known:
            r.fail("V23", pid, f"`risk_accepted_by: {ref}` does not exist in decisions.yaml")


def v20(c: Corpus, r: Result) -> None:
    needs_link = {"requirement", "architecture"}
    for defect in c.defect_list:
        did = str(defect.get("id"))
        cause = str(defect.get("root_cause") or "")
        if cause not in needs_link:
            continue
        if not listy(defect, "violates"):
            r.fail("V20", did, f"has `root_cause` `{cause}` but `violates` is empty")
        if str(defect.get("status")) == "fixed" and not str(defect.get("decision") or "").strip():
            r.fail("V20", did,
                   f"closed as fixed with root_cause `{cause}` without an accompanying `DEC-`")


# Files that DESCRIBE the past, not STATE what currently holds. A dangling citation here is
# not a finding — corpus-guide.md owns that rule, and rewriting it would falsify history.
PAST_RECORD = (
    ".control/memlog/",
    ".control/decisions/",
    ".control/questions/answered.md",
    ".control/reports/",
)
# Corpus that §25 freezes as-is. Its citation of a now-retired prototype is authorized by DEC-016.
FROZEN = (".what/",)
# Derived output. A finding here is UNACTIONABLE by construction — the folder MUST NOT be written
# by hand, so nobody may fix it where it is reported. It also renders registry values inside
# backticks, which makes a frozen `DEC-` `touches:` entry look like a live citation: the 0.5.0
# layout move surfaced three of those, all of them correct history. Fix the source or leave it.
DERIVED = (".control/generated/",)
# A path a run WILL PRODUCE, not one a document cites as existing. A rule stating "this pass's
# memlog lands at X" names a DESTINATION; demanding X already exist would demand the run has already
# happened.
DESTINATION = (
    ".control/memlog/",
    ".control/meetings/",
    ".control/reports/",
    "_bmad-output/",
)

# Material the INSTALLER wrote, which this product neither authored nor may edit.
#
# `.constitution/method/` is portable explanation. Its citations teach where a thing GOES — "the
# glossary lives at `.control/product-glossary.md`" — and are not this product's claim that it has
# one yet. Scanning it made V24 unsatisfiable in both directions: a fresh install went RED on 69
# such lines before G1 had run, and a mature one stayed quiet only by accident. A method guide that
# cites a method file IS checked, but here in the package where it can be fixed — see
# tests/kit-integrity.test.mjs. A product cannot fix a guide `update` overwrites.
#
# The BMad skill trees are the same class under whichever host the installer wrote them to. Both
# hosts MUST be listed: `.claude/skills/bmad-` alone left the `.agents/` copy of one identical
# template failing, which reads as a defect in that product rather than an omission here.
#
# `wdi-*` skills are OURS and are deliberately NOT here. They MUST NOT cite a product file that
# does not exist unless the cite is a placeholder.
INSTALLED = (
    ".constitution/method/",
    ".claude/skills/bmad-",
    ".agents/skills/bmad-",
)

# The extension list is deliberately WIDE. A narrow one does not make V24 safer — it makes it
# silent: a product written in a language missing from the list has its code citations
# unchecked, and nothing says so. Adding one is cheap; a gap is invisible.
CITE_RE = re.compile(
    r"`((?:\.constitution|\.control|\.what|\.how|_bmad-output|\.work|src|web|public|deploy)"
    r"/[A-Za-z0-9_./-]+\.(?:md|txt|yaml|yml|toml|json|sql|html|css|scss|"
    r"py|go|rs|rb|php|java|kt|cs|swift|ts|tsx|js|jsx|mjs|cjs|vue|svelte|ex|exs))`")


# Directories that MUST be pruned DURING traversal, not filtered afterwards.
#
# The old form was `c.root.rglob("*.md")` plus a `rel.startswith(...)` filter, and it had two faults
# that only showed up on a real machine:
#
#   The filter ran too late. rglob had already walked in, so a dangling symlink inside
#   node_modules — an npm workspace link left behind by an abandoned git worktree — raised
#   FileNotFoundError and took the whole run down. A validator that CRASHES on somebody's build
#   output reports nothing about the corpus at all.
#
#   `node_modules/` matched only at the ROOT. `web/node_modules/` sailed straight through, which is
#   where a monorepo actually keeps it.
PRUNE_DIRS = frozenset({
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".next", ".turbo", ".idea", ".vscode",
    "worktrees",   # .claude/worktrees/ — another checkout's tree is not this corpus
})


def _walk_corpus(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    """Every file under `root` with one of `suffixes`, sorted, pruning PRUNE_DIRS as it goes.

    Sorted because determinism is this script's contract: two runs over the same tree MUST report the
    same thing in the same order.
    """
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, onerror=lambda _e: None):
        dirnames[:] = sorted(d for d in dirnames if d not in PRUNE_DIRS)
        for name in filenames:
            if name.endswith(suffixes):
                out.append(Path(dirpath) / name)
    return sorted(out)


def v24(c: Corpus, r: Result) -> None:
    """A path citation inside a document that STATES what currently holds MUST resolve.

    This is the mechanical half of `wdi-reconcile`'s Evidence check, and it is the only way to know
    that a migration stayed complete. Its failure class is distinctive: a file gets deleted or moved,
    while the routing line that points at it stays behind — no other validator sees it, because no
    id moved.

    Deliberately SKIPPED: files that describe the past, corpus that has been frozen, derived
    output, and material the installer wrote (see INSTALLED). A `DEC-` Trace that names material that has since been retired describes what was read on
    that date; reporting it would demand history be rewritten to match the present. Derived output is
    skipped for a second reason on top of that: it MUST NOT be edited by hand, so a finding reported
    there names a file nobody is allowed to fix.
    """
    scanned = 0
    for path in _walk_corpus(c.root, (".md", ".yaml")):
        rel = path.relative_to(c.root).as_posix()
        if rel.startswith("_bmad-output/") or rel.startswith(INSTALLED):
            continue
        if rel.startswith(PAST_RECORD) or rel.startswith(FROZEN) or rel.startswith(DERIVED):
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for cited in sorted(set(CITE_RE.findall(text))):
            if "<" in cited or "{" in cited:
                continue  # placeholder, not a path
            if cited.startswith(DESTINATION):
                continue
            if not (c.root / cited).exists():
                r.fail("V24", rel, f"cites `{cited}` which does not exist")
    if not scanned:
        r.skip("V24", "no file was scanned")


CTR_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.M)


def map_container_headings(root: Path) -> list[str] | None:
    """Heading `### x` under `## Containers` in the code map. None if the map does not exist."""
    path = root / ".control" / "structure-codebase.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    start = text.find("\n## Containers")
    if start < 0:
        return []
    rest = text[start + 1:]
    nxt = re.search(r"^##\s+(?!#)", rest[len("## Containers"):], re.M)
    if nxt:
        rest = rest[:len("## Containers") + nxt.start()]
    return [m.group(1).strip().strip("`") for m in CTR_HEADING.finditer(rest)]


def v25(c: Corpus, r: Result) -> None:
    """A container's `built` and its four consequences, plus the PC x container matrix.

    A container EXISTS inside the boundary whether or not we write its content, and that is what
    used to make the rule unsatisfiable: `structure-guide.md` demands every code-map heading match
    the registry, while a database or web server MUST be registered and MUST NOT have a heading.
    `built` separates the two, and this check is what makes that separation hold instead of the
    argument being repeated on every project. `DEC-017` records its definition.

    Anything whose runtime we do not deploy is an external system: it lives in C4 L1 and MUST NOT
    be registered here at all — its absence from the registry is the check.
    """
    containers = rows(c.components, "containers")
    if not containers:
        r.skip("V25", "`containers:` is not registered yet")
        return

    built: dict[str, bool] = {}
    for ctr in containers:
        cid = str(ctr.get("id") or "").strip()
        if not cid:
            r.fail("V25", "containers", "a container has no `id`")
            continue
        flag = ctr.get("built")
        if not isinstance(flag, bool):
            r.fail("V25", cid, "`built` MUST be a bool — true if we write its content, false if someone else implements it")
            continue
        built[cid] = flag

    # (1) code-map heading = EXACTLY a container with `built: true`
    headings = map_container_headings(c.root)
    if headings is None:
        r.fail("V25", ".control/structure-codebase.md", "the code map does not exist, so container headings cannot be compared")
    else:
        for h in headings:
            if h not in built:
                r.fail("V25", f"code map §{h}", "heading is not a registered container — register it, or it is not a container")
            elif not built[h]:
                r.fail("V25", f"code map §{h}", "`built: false` MUST NOT have a heading — there is no code of ours inside it")
        for cid, flag in sorted(built.items()):
            if flag and cid not in headings:
                r.fail("V25", cid, "`built: true` MUST have a heading in the code map")

    # (2) `built: false` MUST NOT be used by an LC, and (3) MUST NOT appear in a PC's `containers:`
    for lc in c.lcs:
        ctr = str(lc.get("container") or "").strip()
        if ctr and built.get(ctr) is False:
            r.fail("V25", str(lc.get("id") or "LC-?"), f"names container `{ctr}` which is `built: false`")
        elif ctr and ctr not in built:
            r.fail("V25", str(lc.get("id") or "LC-?"), f"names container `{ctr}` which is not registered")

    # (4) PC x container matrix — this field is its SSOT, and it MUST be complete at G3
    for pc in c.pcs:
        pid = str(pc.get("id") or "?")
        listed = listy(pc, "containers")
        if not listed:
            r.fail("V25", pid, "`containers:` is empty — every PC MUST live in at least one container (a G3 debt)")
            continue
        for ctr in listed:
            if ctr not in built:
                r.fail("V25", pid, f"`containers:` names `{ctr}` which is not registered")
            elif not built[ctr]:
                r.fail("V25", pid, f"`containers:` names `{ctr}` which is `built: false` — the data lives there by definition, so the row tells us nothing")

    # (5) L3 — only for `built: true`, and only ones that hold more than one PC
    pcs_per: dict[str, list[str]] = {}
    for pc in c.pcs:
        for ctr in listy(pc, "containers"):
            pcs_per.setdefault(ctr, []).append(str(pc.get("id") or "?"))
    for path in sorted((c.root / ".how" / "_platform").glob("c4-l3-*.md")):
        cid = path.name[len("c4-l3-"):-len(".md")]
        if cid not in built:
            r.fail("V25", path.relative_to(c.root).as_posix(),
                   f"L3 for `{cid}` which is not a registered container")
        elif not built[cid]:
            r.fail("V25", path.relative_to(c.root).as_posix(),
                   f"`{cid}` `built: false` MUST NOT have an L3 — not one box inside it is ours to draw")
    for cid, pids in sorted(pcs_per.items()):
        if built.get(cid) and len(pids) > 1:
            l3 = c.root / ".how" / "_platform" / f"c4-l3-{cid}.md"
            if not l3.exists():
                r.fail("V25", cid, f"holds {len(pids)} PCs, so `c4-l3-{cid}.md` MUST exist")


UC_ROW_RE = re.compile(r"^\|\s*(UC-\d+)\s*\|([^\n]*)$", re.M)

# The `critical` column value is machine-matched, so it is machine-facing and its canonical form
# is English `yes`. `ya` is still accepted: a corpus that wrote it before this rule took effect
# MUST NOT be forced to migrate just so a regex can be tidier. The word boundary keeps `ya` from
# matching inside other words.
CRITICAL_YES = re.compile(r"\b(yes|ya)\b", re.I)


def v26(c: Corpus, r: Result) -> None:
    """The UC catalogue in every SRS MUST agree with `usecases.yaml` — both its id AND its `critical`.

    This is the most expensive gap this pass closes, because it is the only one that **had already
    happened and no validator saw it.** Step 16 re-derived `critical` in the registry with a
    narrowed definition — money, personal data, irreversible action — and the seven catalogue tables
    in the SRS did not follow along. Twenty-six rows disagreed, and the disagreement was only
    discovered when a human read the sentence "nine of these are critical" in SRS-admin while the
    registry held three.

    The registry is the SSOT. The table in the SRS is the catalogue's permanent home for a reader,
    and two homes for one fact are only safe if something compares them. This is what compares them.

    What is NOT checked here: title and actor. Both are prose, and prose with different words is
    not prose with a different meaning — comparing them would report style as a defect.
    """
    reg = {str(uc.get("id")): bool(uc.get("critical")) for uc in c.ucs}
    reg_pc = {str(uc.get("id")): str(uc.get("component") or "") for uc in c.ucs}
    checked = 0
    for pc in c.pcs:
        pid = str(pc.get("id"))
        path = c.root / f".what/{pid}/SRS-{pid}.md"
        if not path.exists():
            continue
        checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        seen: set[str] = set()
        for match in UC_ROW_RE.finditer(text):
            uid = match.group(1)
            cells = [x.strip() for x in match.group(2).split("|")]
            if len(cells) < 4:
                continue
            seen.add(uid)
            if uid not in reg:
                r.fail("V26", f"{pid}/{uid}", "is in the SRS catalogue but not in `usecases.yaml`")
                continue
            if reg_pc[uid] != pid:
                r.fail("V26", f"{pid}/{uid}",
                       f"the registry places it in `{reg_pc[uid]}`, not in this component")
            marked = CRITICAL_YES.search(cells[3]) is not None
            if marked != reg[uid]:
                r.fail("V26", f"{pid}/{uid}",
                       f"`critical` in the SRS {'yes' if marked else 'no'}, "
                       f"in the registry {'yes' if reg[uid] else 'no'}")
        for uid, owner in sorted(reg_pc.items()):
            if owner == pid and uid not in seen:
                r.fail("V26", f"{pid}/{uid}", "is in `usecases.yaml` but not in the SRS catalogue")
    if not checked:
        r.skip("V26", "no SRS could be read")


def v27(c: Corpus, r: Result) -> None:
    """Every file in the custom room MUST declare itself, and a rebuttal MUST have a decision.

    The `.constitution/project/` room exists so product-specific rules have a home that `update`
    does not overwrite and `promote` does not publish. The cost that comes with it: it is also the
    easiest place to break a generic rule without a trace. Its frontmatter is what holds that back.

    A file here MAY narrow or add without naming anything. To REBUT a generic rule it MUST name it
    in `overrides:` and carry a `decision:` — because a method that can be rebutted without a
    decision stops being trustworthy in the next repo.

    Four files in the room are STRUCTURAL and are skipped, because they are not ad-hoc rules and
    carry their own frontmatter conventions instead:

        README.md               authored in the package, not in the product
        constitution.md         Articles 1, 2, 5 — carries `status:`, and Article 4 governs it
        codebase-*-guide.md     the stack, conventions, and brownfield guides — `status:` plus
                                `ratified_by:`, and they are filled by a wave's distillation

    Demanding `scope:` and `purpose:` of those would be demanding a declaration of files whose
    role is already fixed by the layout. What V27 exists to guard is the file somebody ADDS.

    Only `.md` is looked at. A script in the room — `inventory-readers.py` is the one the package
    seeds — is not an ad-hoc rule and has nowhere to put frontmatter.
    """
    room = c.root / ".constitution" / "project"
    if not room.is_dir():
        r.skip("V27", "the `.constitution/project/` room does not exist yet — it is seeded at install")
        return
    structural = {"README.md", "constitution.md"}
    files = [p for p in sorted(room.rglob("*.md"))
             if p.name not in structural and not p.name.startswith("codebase-")]
    if not files:
        r.skip("V27", "the `.constitution/project/` room is empty, and that is a valid state — "
                      "a generic rule MUST NOT be moved here just to give the room content")
        return
    dec_ids = {str(d.get("id")) for d in c.decs}
    for path in files:
        rel = path.relative_to(c.root).as_posix()
        fm = frontmatter(path)
        if fm is None:
            r.fail("V27", rel, "has no frontmatter")
            continue
        if str(fm.get("scope") or "").strip() != "project":
            r.fail("V27", rel, "`scope:` MUST contain exactly `project`")
        if not str(fm.get("purpose") or "").strip():
            r.fail("V27", rel, "`purpose:` is empty — one line: what this rule guards")
        over = str(fm.get("overrides") or "").strip()
        dec = str(fm.get("decision") or "").strip()
        if over:
            if not (c.root / over).exists():
                r.fail("V27", rel, f"`overrides:` points to `{over}` which does not exist — "
                                   f"the rebutted rule may already be gone")
            if not dec:
                r.fail("V27", rel, "rebuts a generic rule without `decision:` — "
                                   "a rebuttal MUST have a `DEC-` that decided it")
            elif dec not in dec_ids:
                r.fail("V27", rel, f"`decision: {dec}` is not registered in decisions.yaml")
        elif dec:
            r.fail("V27", rel, "`decision:` is set without `overrides:` — "
                               "name which rule is rebutted, or drop `decision:`")


def run_checks(c: Corpus, asof: dt.date) -> Result:
    r = Result()
    for fn in (v1, v2, v3, v4, v5, v6, v7, v8, v9, v11, v12, v13, v15, v16, v17, v18, v19, v20,
               v21, v22, v23, v24, v25, v26, v27):
        fn(c, r)
    v14(c, r, asof)
    return r


# ------------------------------------------------------------------ generator


def _story_status(c: Corpus, story: dict) -> str:
    folder = str(story.get("spec_folder") or "").strip()
    if not folder:
        return "unknown"
    matches = sorted((c.root / folder / "stories").glob(f"{story.get('id')}-*.md"))
    if not matches:
        return "unknown"
    return str((frontmatter(matches[0]) or {}).get("status") or "unknown")


def gen_components(c: Corpus) -> dict:
    return {
        "product_components": [
            {"id": pc.get("id"), "name": pc.get("name"),
             "containers": listy(pc, "containers"),
             "logical_components": sorted(
                 str(lc.get("id")) for lc in c.lcs
                 if str(lc.get("component")) == str(pc.get("id")))}
            for pc in c.pcs
        ],
        "logical_components": [
            {"id": lc.get("id"), "type": lc.get("type"), "component": lc.get("component"),
             "area": lc.get("area"), "owner": lc.get("owner")}
            for lc in c.lcs
        ],
    }


def gen_risks(c: Corpus) -> dict:
    return {"risks": [
        {"id": x.get("id"), "impact": x.get("impact"), "likelihood": x.get("likelihood"),
         "owner": x.get("owner"), "status": x.get("status"),
         "pivot_trigger": x.get("pivot_trigger")}
        for x in rows(c.risks, "risks") if str(x.get("status")) != "closed"
    ]}


def gen_dag(c: Corpus) -> dict:
    out = []
    per_wave: dict[str, list[dict]] = {}
    for wave, _, story in c.stories():
        per_wave.setdefault(str(wave.get("id")), []).append(story)
    for wid in sorted(per_wave):
        items = per_wave[wid]
        done: set[str] = set()
        pending = {str(s.get("id")): set(listy(s, "depends_on")) for s in items}
        waves_out = []
        while pending:
            ready = sorted(k for k, deps in pending.items() if not (deps - done))
            if not ready:  # cycle — V7 has already reported it
                waves_out.append({"blocked": sorted(pending)})
                break
            waves_out.append({"parallel": ready})
            done |= set(ready)
            for k in ready:
                pending.pop(k)
        out.append({"wave": wid, "order": waves_out})
    return {"dag": out}


def gen_rtm(c: Corpus) -> dict:
    cap_goal = {str(x.get("id")): str(x.get("goal", "")) for x in c.caps}
    ucs_for_fr: dict[str, list[str]] = {}
    for uc in c.ucs:
        for fr in listy(uc, "satisfies"):
            ucs_for_fr.setdefault(fr, []).append(str(uc.get("id")))
    stories_for_uc: dict[str, list[tuple[dict, dict]]] = {}
    for wave, _, story in c.stories():
        for uc in listy(story, "satisfies"):
            stories_for_uc.setdefault(uc, []).append((wave, story))
    decs_for: dict[str, list[str]] = {}
    for dec in c.decs:
        for target in listy(dec, "serves"):
            decs_for.setdefault(target, []).append(str(dec.get("id")))

    lines = []
    for fr in c.frs:
        fid = str(fr.get("id"))
        cap = str(fr.get("capability", ""))
        base = {"BG": cap_goal.get(cap, ""), "CAP": cap, "FR": fid,
                "DEC": sorted(decs_for.get(fid, []))}
        ucs = sorted(ucs_for_fr.get(fid, []))
        if not ucs:
            exempt = bool(str(fr.get("no_uc") or "").strip())
            lines.append({**base, "UC": "", "story": "", "wave": "", "release": "",
                          "test": [], "status": "", "green": False,
                          "exempt": exempt,
                          "broken_at": "no_uc" if exempt else "UC"})
            continue
        for uid in ucs:
            pairs = sorted(stories_for_uc.get(uid, []), key=lambda p: str(p[1].get("id")))
            if not pairs:
                lines.append({**base, "UC": uid, "story": "", "wave": "", "release": "",
                              "test": [], "status": "", "green": False, "exempt": False,
                              "broken_at": "story"})
                continue
            for wave, story in pairs:
                status = _story_status(c, story)
                tests = listy(story, "tests")
                broken = ""
                if not tests:
                    broken = "test"
                elif status != "done":
                    broken = "status"
                lines.append({**base, "UC": uid, "story": str(story.get("id")),
                              "wave": str(wave.get("id")), "release": str(wave.get("release", "")),
                              "test": tests, "status": status, "exempt": False,
                              "green": broken == "", "broken_at": broken})
    return {"rtm": lines}


def gen_status(c: Corpus, rtm: dict, result: Result) -> dict:
    lines = rtm.get("rtm") or []
    counted = [line for line in lines if not line.get("exempt")]
    exempt = len(lines) - len(counted)
    green = sum(1 for line in counted if line.get("green"))
    per_wave = []
    for wave in c.wave_list:
        wid = str(wave.get("id"))
        items = [s for w, _, s in c.stories() if str(w.get("id")) == wid]
        done = sum(1 for s in items if _story_status(c, s) == "done")
        per_wave.append({"wave": wid, "status": wave.get("status"),
                         "stories_done": done, "stories_total": len(items),
                         "work_progress": _pct(done, len(items))})
    applicable = 26  # V1..V27 minus V10, which was retired
    return {
        "promise_progress": _pct(green, len(counted)),
        "rtm_rows": {"green": green, "counted": len(counted),
                      "excluded_no_uc": exempt},
        "work_progress": per_wave,
        "gate_readiness": _pct(applicable - len(result.red), applicable),
        "validators_red": result.red,
        "validators_skipped": dict(sorted(result.skipped.items())),
        "open_questions": _question_budget(c),
    }


def _question_budget(c: Corpus) -> dict:
    """Counts of all four question lists, compared against the budget in index.yaml.

    The budget is NOT a hard gate. It is reported when a batch exceeds it, because a larger
    batch is a signal about the pass, not about the corpus.
    """
    budget = c.index.get("question_budget") or {}
    out: dict[str, object] = {}
    for name in ("blocking", "assumptions", "external", "answered"):
        path = c.root / ".control/questions" / f"{name}.md"
        rows_n = 0
        if path.exists():
            rows_n = sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
                         if line.startswith("| OQ-"))
        out[name] = rows_n
    cap_block = budget.get("blocking_per_component")
    if cap_block and c.pcs:
        allowed = int(cap_block) * len(c.pcs)
        out["blocking_budget"] = allowed
        out["blocking_over_budget"] = out["blocking"] > allowed
    cap_assume = budget.get("assumptions_per_gate")
    if cap_assume:
        out["assumptions_budget_per_gate"] = int(cap_assume)
    return out


def _pct(part: int, total: int) -> str:
    return "n/a" if total == 0 else f"{round(100 * part / total)}%"


def as_markdown(name: str, payload: dict) -> str:
    body = dump(payload)
    return (f"# {name}\n\n"
            f"> Generated by `.constitution/method/scripts/validate.py --generate`. "
            f"MUST NOT be hand-edited.\n\n"
            f"```yaml\n{body}```\n")


# ------------------------------------------------------- pages for humans

PAGE_HEADER = ("> Generated by `.constitution/method/scripts/validate.py --generate`. "
               "MUST NOT be hand-edited.\n")


def _section(path: Path, heading: str) -> str:
    """Extract one `## <heading>` section from a markdown file, as-is."""
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower().startswith(heading.lower())
            continue
        if inside:
            out.append(line)
    return "\n".join(out).strip("\n")


def _body(path: Path) -> str:
    """File content without frontmatter and without template comments."""
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    match = FM.match(text)
    if match:
        text = text[match.end():]
    while "<!--" in text and "-->" in text:
        head, _, rest = text.partition("<!--")
        _, _, tail = rest.partition("-->")
        text = head + tail
    return text.strip("\n")


def page_decisions(c: Corpus) -> str:
    """Flat table of every `DEC-`. This is what replaces looking up decisions through the memlog."""
    rows_out = ["| id | Title | Status | Type | Touches | File |",
                "| --- | --- | --- | --- | --- | --- |"]
    for dec in c.decs:
        touches = ", ".join(f"`{x}`" for x in listy(dec, "touches")) or "—"
        rows_out.append(
            f"| `{dec.get('id')}` | {_cell(dec.get('title'))} | `{dec.get('status', '')}` "
            f"| {dec.get('type') or '—'} | {touches} | `{dec.get('file', '')}` |")
    counts: dict[str, int] = {}
    for dec in c.decs:
        key = str(dec.get("status"))
        counts[key] = counts.get(key, 0) + 1
    tally = " · ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "no decisions yet"
    return ("# decisions\n\n" + PAGE_HEADER +
            "\nDecisions are no longer looked up through the memlog — the memlog goes back to being just a pass log.\n"
            f"\n**{len(c.decs)} decisions** — {tally}.\n\n" + "\n".join(rows_out) + "\n")


def page_blueprint(c: Corpus) -> str:
    """One-page roll-up reviewed at G3. Seven files become one read.

    The UC catalogue, actor list, and domain model stay put in their own component's kernel as
    their permanent home. This is their view. One fact, one home, one view.
    """
    parts = ["# blueprint\n", PAGE_HEADER,
             "\nThis is what the owner reads at **G3 Blueprint**, instead of seven files. Its "
             "content is affected by neither `mode` nor `risk_accepted`.\n"]

    crit = sum(1 for uc in c.ucs if uc.get("critical"))
    parts.append(f"\n## Use case catalogue\n\n**{len(c.ucs)} use cases**, {crit} marked "
                 f"`critical`.\n")
    parts.append("| id | Use case | Component | Satisfies | critical |")
    parts.append("| --- | --- | --- | --- | --- |")
    for uc in c.ucs:
        sat = ", ".join(f"`{x}`" for x in listy(uc, "satisfies")) or "—"
        flag = "yes" if uc.get("critical") else "no"
        parts.append(f"| `{uc.get('id')}` | {_cell(uc.get('title'))} | "
                     f"`{uc.get('component', '')}` | {sat} | {flag} |")

    parts.append("\n## Actor list\n")
    for pc in c.pcs:
        pid = str(pc.get("id"))
        block = _section(c.root / f".what/{pid}/SRS-{pid}.md", "Actor Register")
        # A Product Component carries no `name` in `components.yaml` — only a container does — so
        # this heading rendered as `### settings — `, with an orphaned separator, for every
        # component of every product. The separator belongs to the name, not to the heading.
        name = str(pc.get("name") or "").strip()
        parts.append(f"\n### {pid} — {name}\n" if name else f"\n### {pid}\n")
        parts.append(_demote(block) if block
                     else "_no § Actor Register in this component's SRS yet._")

    parts.append("\n## Domain model\n")
    for pc in c.pcs:
        pid = str(pc.get("id"))
        block = _body(c.root / f".what/{pid}/03-domain/domain-model.md")
        parts.append(f"\n### {pid}\n")
        parts.append(_demote(block) if block else "_no `03-domain/domain-model.md` yet._")

    parts.append("\n## Three inventories\n")
    for kind, name in (("db", "table"), ("api", "endpoint"), ("screen", "screen")):
        block = _body(c.root / f".how/_platform/inventory-{kind}.md")
        parts.append(f"\n### List of {name}s — `inventory-{kind}.md`\n")
        parts.append(_demote(block) if block else f"_no `inventory-{kind}.md` yet._")

    return "\n".join(parts) + "\n"


def _cell(value: object, limit: int = 110) -> str:
    """One table row, shortened. The full-length source stays in the registry — this is just a view."""
    text = " ".join(str(value or "").split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _demote(block: str, by: int = 2) -> str:
    """Demote the heading level of inlined content, so it does not clash with the roll-up's own structure."""
    out = []
    for line in block.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            hashes = len(stripped) - len(stripped.lstrip("#"))
            out.append("#" * min(6, hashes + by) + stripped[hashes:])
        else:
            out.append(line)
    return "\n".join(out)


def page_estimate(c: Corpus) -> str:
    """Table of CANDIDATE tasks. One row per `FR`, since that is a wave's ideal shape."""
    mode_of = {str(pc.get("id")): c.mode_of(pc) for pc in c.pcs}
    risk_of = {str(pc.get("id")): (str(pc.get("risk_accepted") or "—"),
                                   str(pc.get("risk_note") or "—")) for pc in c.pcs}
    cap_by_id = {str(x.get("id")): x for x in c.caps}
    fr_per_cap: dict[str, int] = {}
    for fr in c.frs:
        key = str(fr.get("capability", ""))
        fr_per_cap[key] = fr_per_cap.get(key, 0) + 1

    have_mandays = any(x.get("estimate_mandays") for x in c.caps)
    parts = ["# estimate\n", PAGE_HEADER,
             "\n**THIS IS AN ESTIMATE, FORWARD-LOOKING.** Every row below is a **candidate** "
             "task; the wave in `waves.yaml` is the real one. One row MAY become one wave, and three "
             "neighboring rows MAY be merged into one — that merge is a human decision made when the "
             "wave is opened.\n"]
    if not have_mandays:
        parts.append("\n**With no `estimate_mandays` on a single `CAP`**, the Load column is empty and "
                     "this output is only as good as a T-shirt-size estimate. It MUST be reported as such.\n")

    parts.append("\n| Task | FR | Epic | mode | Exposure | Load | Priority | Depends on | Release |")
    parts.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for fr in c.frs:
        cap_id = str(fr.get("capability", ""))
        cap = cap_by_id.get(cap_id, {})
        pid = str(fr.get("component") or cap.get("component") or "")
        risk, note = risk_of.get(pid, ("—", "—"))
        exposure = "not set yet" if risk == "—" else f"`{risk}` — {_cell(note, 60)}"
        mandays = cap.get("estimate_mandays")
        share = "—"
        if mandays:
            try:
                share = f"{float(mandays) / max(1, fr_per_cap.get(cap_id, 1)):.1f}"
            except (TypeError, ValueError):
                share = "—"
        deps = ", ".join(f"`{x}`" for x in listy(cap, "depends_on")) or "—"
        parts.append(
            f"| {_cell(fr.get('text') or fr.get('title'))} | `{fr.get('id')}` | `{pid or '—'}` "
            f"| `{mode_of.get(pid, 'catalog')}` | {exposure} | {share} "
            f"| {cap.get('priority', '—')} | {deps} | {cap.get('target_release', '—')} |")
    return "\n".join(parts) + "\n"


def generate(c: Corpus, result: Result) -> list[Path]:
    out_dir = c.root / ".control" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    rtm = gen_rtm(c)
    payloads = {
        "components": gen_components(c),
        "risks": gen_risks(c),
        "dag": gen_dag(c),
        "rtm": rtm,
        "status": gen_status(c, rtm, result),
    }
    written = []
    for name in GENERATED_ORDER:
        payload = payloads[name]
        yaml_path = out_dir / f"{name}.yaml"
        yaml_path.write_text(dump(payload), encoding="utf-8")
        md_path = out_dir / f"{name}.md"
        md_path.write_text(as_markdown(name, payload), encoding="utf-8")
        written += [yaml_path, md_path]

    # Three pages for HUMANS: real markdown tables, with no .yaml twin. What people read is
    # not wrapped in a yaml fence, and no machine reader demands a second version of it.
    for name, render in (("decisions", page_decisions),
                         ("blueprint", page_blueprint),
                         ("estimate", page_estimate)):
        page = out_dir / f"{name}.md"
        page.write_text(render(c), encoding="utf-8")
        written.append(page)
    return written


# ------------------------------------------------------------------------ CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate", description="V1..V27 and the .control/generated/ generator")
    parser.add_argument("--check", action="store_true",
                        help="check only; exit non-zero if anything is red")
    parser.add_argument("--generate", action="store_true",
                        help="rewrite .control/generated/ (still runs the check first)")
    parser.add_argument("--root", default=".", help="repo root (default: current directory)")
    parser.add_argument("--asof", default=None,
                        help="reference date for V14, format YYYY-MM-DD (default: today). "
                             "Stated explicitly so a run can be repeated exactly")
    args = parser.parse_args(argv)

    if not args.check and not args.generate:
        args.check = True

    root = Path(args.root).resolve()
    if not (root / ".control" / "registry").is_dir():
        print(f"validate: {root} has no .control/registry/ — wrong repo root?", file=sys.stderr)
        return 2

    asof = dt.date.fromisoformat(args.asof) if args.asof else dt.date.today()
    corpus = Corpus.load(root)
    result = run_checks(corpus, asof)

    if args.generate:
        for path in generate(corpus, result):
            print(f"  wrote {path.relative_to(root).as_posix()}")

    if result.findings:
        print(f"\nRED — {len(result.findings)} findings across {len(result.red)} validators\n")
        for finding in sorted(result.findings, key=lambda f: f.sort_key):
            print(f"  {finding.vid:<4} {finding.subject}: {finding.message}")
    else:
        print("\nGREEN — no findings")

    if result.skipped:
        print("\nSkipped:")
        for vid, why in sorted(result.skipped.items()):
            print(f"  {vid:<4} {why}")

    print(f"\nV14 reference date: {asof.isoformat()}")
    return 1 if result.findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

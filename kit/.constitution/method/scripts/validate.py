#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""validate — goal-has-fr..id-allocated-once plus the .control/generated/ generator.

Two modes:
    validate --check      exit non-zero if anything is red; writes nothing
    validate --generate   rewrite .control/generated/ (and still runs --check)

Determinism is the contract: two runs over the same data MUST produce the same result.
That is why there is no unordered iteration, and the one time-dependent input
(--asof, used by plan-dates) is stated explicitly instead of being taken silently from the wall clock.

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

# Every check, in the order findings are printed. A check is NAMED for what must be true, so a
# failure reads as "this is what is not true". The numbers these replaced are kept as a `# was V<n>`
# marker on each def, because decisions and reports frozen in real repos still cite them.
CHECK_ORDER = (
    "goal-has-fr",
    "fr-has-uc",
    "uc-scheduled",
    "ticket-has-test",
    "nfr-has-enforcer",
    "refs-resolve",
    "no-cycles",
    "applied-dec-touches",
    "locked-gate-passed",
    "parallel-tickets-blocked",
    "lc-registered",
    "review-trace",
    "plan-dates",
    "chain-links",
    "memlog-home",
    "spec-names-release-prd",
    "ticket-status-one-home",
    "defect-root-cause",
    "entity-one-writer",
    "spec-after-g4",
    "high-risk-named",
    "cites-resolve",
    "container-built",
    "custom-room-declared",
    "id-allocated-once",
)

REGISTRY = "control/registry"  # tidied up in resolve(); '.control' is what is actually used
GENERATED_ORDER = ["components", "risks", "dag", "rtm", "status"]

# Pages read by HUMANS, not machines: written as real markdown tables, not yaml
# in a fence. Each has one clear reader. `brief` and `prd-<slug>` are deliverables — see
# page_brief/page_prd — and are not listed here because a PRD page is one per initiative found
# on disk, not one fixed name.
GENERATED_PAGES = ["decisions", "estimate"]

# The two trees a HUMAN reads. Every file in them is a projection: prose lifted from the working
# document at the mirror path, rows rendered from the registry, nothing authored, nothing edited.
# A skill MUST NOT read them as input — they are output, and the working document is the source.
RENDERED_WHAT = ".what-rendered"
RENDERED_HOW = ".how-rendered"

MODES = ("catalog", "outline", "guarded", "deep")

# Keywords that make a component "sensitive" for high-risk-named. Matched against `risk_note`, which is PROSE in
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
        order = CHECK_ORDER.index(self.vid) if self.vid in CHECK_ORDER else len(CHECK_ORDER)
        return (order, self.subject, self.message)


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


REQUIREMENT_KEYS = ("goals", "capabilities", "functional", "nonfunctional", "journeys")


@dataclass
class Corpus:
    root: Path
    requirements: dict
    """The MERGED view of every requirement file. Read by everything that asks a product-wide
    question — the RTM, the estimate, goal-has-fr/fr-has-uc/nfr-has-enforcer/chain-links. What is merged is decided in `load`."""
    requirement_files: dict[str, dict]
    """Each requirement file kept separately, keyed by its name: `goals` for the product's `BG`,
    and one `requirements-<slug>` per PRD — the slug being that PRD's folder name.

    ONE FILE, ONE WRITER, ONE GATE. `wdi-problem` owns `goals.yaml` at G1; `wdi-product` owns its
    own initiative's file at G2, and that is where `CAP` lives too — a capability is declared by a
    feature, one feature is one capability, and a feature lives in exactly one PRD. Co-locating
    `CAP` with `BG` was tried and reverted: the argument for it was that `depends_on` between
    capabilities crosses initiatives, and that turned out to buy nothing, because no-cycles reads the
    MERGED view and never opens a file.

    The split also makes an `FR`'s initiative STRUCTURAL — before it, nothing in the registry
    recorded which PRD a promise belonged to, and the only way to find out was to grep the PRD's
    prose for its id."""
    usecases: dict
    decisions: dict
    risks: dict
    components: dict
    specs: dict
    defects: dict
    index: dict

    @classmethod
    def load(cls, root: Path) -> "Corpus":
        reg = root / ".control" / "registry"
        files: dict[str, dict] = {}
        product = reg / "goals.yaml"
        if product.exists():
            files[product.stem] = load_yaml(product)
        # A corpus from before the split keeps ONE `requirements.yaml`, and it is still read: an
        # install that has not been cut per PRD yet stays green. `update` seeds `goals.yaml`;
        # moving the rows is the owner's act, done by the skill that owns each row.
        legacy = reg / "requirements.yaml"
        if legacy.exists():
            files[legacy.stem] = load_yaml(legacy)
        for path in sorted(reg.glob("requirements-*.yaml")):
            files[path.stem] = load_yaml(path)

        # Union, not precedence. A row present in two files is a REAL defect — id-allocated-once names it — and
        # preferring one file would hide it instead.
        merged = {key: [row for doc in files.values() for row in rows(doc, key)]
                  for key in REQUIREMENT_KEYS}
        return cls(
            root=root,
            requirements=merged,
            requirement_files=files,
            usecases=load_yaml(reg / "usecases.yaml"),
            decisions=load_yaml(reg / "decisions.yaml"),
            risks=load_yaml(reg / "risks.yaml"),
            components=load_yaml(reg / "components.yaml"),
            specs=load_yaml(reg / "specs.yaml"),
            defects=load_yaml(reg / "defects.yaml"),
            index=load_yaml(reg / "index.yaml"),
        )

    def requirements_of(self, slug: str) -> dict:
        """One initiative's own requirement file, empty when it has none yet."""
        return self.requirement_files.get(f"requirements-{slug}", {})

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
    def spec_list(self) -> list[dict]:
        return rows(self.specs, "specs")

    @property
    def defect_list(self) -> list[dict]:
        return rows(self.defects, "defects")

    def tickets(self) -> list[tuple[dict, dict]]:
        """(spec, ticket) — sorted by ticket id.

        FLAT. The `epics` level between a spec and its tickets is repealed: it grouped rows and
        bought nothing, and every reader here had to walk through it to reach the row it wanted.
        A ticket names its `component` directly.
        """
        out = []
        for spec in self.spec_list:
            for ticket in sorted(spec.get("tickets") or [], key=lambda t: str(t.get("id", ""))):
                if isinstance(ticket, dict):
                    out.append((spec, ticket))
        return out


def listy(row: dict, key: str) -> list[str]:
    value = row.get(key) or []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value if v is not None]


# ------------------------------------------------------------------ validators


def goal_has_fr(c: Corpus, r: Result) -> None:  # was V1
    """Every BG has >=1 FR through its CAP, OR states its reason in `no_fr`.

    A goal MAY be satisfied by an **invariant** rather than a feature. `BG-6` — the data and
    deployment foundation can be extended without being torn down — is measured by two architectural
    properties that its own `measure` names, and no `FR` can carry it without being invented. Demanding
    one `FR` there produces a false promise, and a false promise is more expensive than a finding.

    The escape MUST carry a reason, not a boolean — the same shape as `no_uc` on `FR` (fr-has-uc).
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
        r.fail("goal-has-fr", gid, "has no FR through its CAP and states no reason in `no_fr`")


def fr_has_uc(c: Corpus, r: Result) -> None:  # was V2
    covered = {fr for uc in c.ucs for fr in listy(uc, "satisfies")}
    for fr in c.frs:
        fid = str(fr.get("id"))
        if fid in covered:
            continue
        if str(fr.get("no_uc") or "").strip():
            continue
        r.fail("fr-has-uc", fid, "has no UC and states no reason in `no_uc`")


def uc_scheduled(c: Corpus, r: Result) -> None:  # was V3
    """A UC on a component that a spec has ALREADY touched MUST be scheduled to a ticket.

    The old shape demanded this of EVERY UC, at any time. Before the first spec that meant the
    entire catalogue was reported red — 56 findings out of 62, and those 56 were the correct state,
    not drift: a ticket is born in a spec, and there was no spec yet. A validator that drowns six
    real findings under fifty-six expected ones stops being read, and a validator that is not read
    guards nothing.

    What is guarded now is the actual omission: a spec touches a component, and a UC of that
    component is left behind without a ticket. Full coverage of the whole catalogue is a G5
    question, and `wdi-build` owns it — the same way lc-registered was shifted to spec closing.
    """
    scheduled = {uc for _, t in c.tickets() for uc in listy(t, "satisfies")}
    touched = {str(t.get("component")) for _, t in c.tickets() if t.get("component")}
    if not c.spec_list:
        r.skip("uc-scheduled", "no spec yet, so no ticket yet — every unscheduled UC is the correct "
                     "state. Full catalogue coverage is checked at G5")
        return
    for uc in c.ucs:
        uid = str(uc.get("id"))
        if uid in scheduled or str(uc.get("component")) not in touched:
            continue
        r.fail("uc-scheduled", uid, f"component `{uc.get('component')}` has already been touched by a spec, "
                          f"but this UC is not scheduled to any ticket")


def ticket_has_test(c: Corpus, r: Result) -> None:  # was V4
    for _, ticket in c.tickets():
        if not [t for t in listy(ticket, "tests") if t.strip()]:
            r.fail("ticket-has-test", str(ticket.get("id")), "has not one named test")


def nfr_has_enforcer(c: Corpus, r: Result) -> None:  # was V5
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
        r.fail("nfr-has-enforcer", str(nfr.get("id")),
               "has no enforcer in `enforced_by` and states no reason in `no_enforcer`")


def refs_resolve(c: Corpus, r: Result) -> None:  # was V6
    defined: set[str] = set()
    for group in (c.goals, c.caps, c.frs, c.nfrs, c.ucs, c.decs, c.lcs, c.pcs,
                  rows(c.requirements, "journeys"), rows(c.risks, "risks"), c.defect_list):
        defined |= {str(row.get("id")) for row in group if row.get("id") is not None}
    for spec in c.spec_list:
        defined.add(str(spec.get("id")))
    for _, ticket in c.tickets():
        defined.add(str(ticket.get("id")))

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
    for spec in c.spec_list:
        refs += [(str(spec.get("id")), d) for d in listy(spec, "depends_on")]
    for _, ticket in c.tickets():
        refs += [(str(ticket.get("id")), u) for u in listy(ticket, "satisfies")]
        refs += [(str(ticket.get("id")), b) for b in listy(ticket, "blocked_by")]

    for owner, target in sorted(set(refs)):
        if target and target not in defined:
            r.fail("refs-resolve", owner, f"points to `{target}` which does not exist in any registry")


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


def no_cycles(c: Corpus, r: Result) -> None:  # was V7
    caps = {str(x.get("id")): listy(x, "depends_on") for x in c.caps}
    for node in _cycles(caps):
        r.fail("no-cycles", node, "is part of a `depends_on` cycle among CAPs")
    # Two graphs, two field names, and the difference is not cosmetic. A spec `depends_on` another
    # spec — an ordering between units of delivery. A ticket is `blocked_by` other tickets, which is
    # what the frontier is read from and what the tracker calls the same edge.
    specs = {str(x.get("id")): listy(x, "depends_on") for x in c.spec_list}
    for node in _cycles(specs):
        r.fail("no-cycles", node, "is part of a `depends_on` cycle among specs")
    tickets = {str(t.get("id")): listy(t, "blocked_by") for _, t in c.tickets()}
    for node in _cycles(tickets):
        r.fail("no-cycles", node, "is part of a `blocked_by` cycle among tickets — the frontier is empty "
                           "and no ticket can ever start")


def applied_dec_touches(c: Corpus, r: Result) -> None:  # was V8
    """Every `applied` decision names a non-empty `touches`.

    Replaces the old shape "every accepted decision serves >=1 FR/NFR". A decision like
    "the filter MUST work like this" serves no FR at all, and that is VALID — it is exactly
    decisions like that which most need remembering, and the old rule discarded them.
    """
    for dec in c.decs:
        if str(dec.get("status")) != "applied":
            continue
        if not [x for x in listy(dec, "touches") if str(x).strip()]:
            r.fail("applied-dec-touches", str(dec.get("id")),
                   "is applied but `touches` is empty — an application with no file trace")


def locked_gate_passed(c: Corpus, r: Result) -> None:  # was V9
    passed = {str(g) for g in (c.index.get("gates_passed") or [])}
    for path in sorted(c.root.glob(".what/**/*.md")) + sorted(c.root.glob(".how/**/*.md")):
        fm = frontmatter(path) or {}
        if str(fm.get("status")) != "locked":
            continue
        gate = str(fm.get("locked_at_gate") or "")
        if gate not in passed:
            rel = path.relative_to(c.root).as_posix()
            r.fail("locked-gate-passed", rel, f"is locked but gate `{gate or '?'}` is not recorded as passed")


def parallel_tickets_blocked(c: Corpus, r: Result) -> None:  # was V11
    per_spec: dict[str, list[dict]] = {}
    for spec, ticket in c.tickets():
        per_spec.setdefault(str(spec.get("id")), []).append(ticket)

    for wid in sorted(per_spec):
        items = per_spec[wid]
        edges = {str(t.get("id")): set(listy(t, "blocked_by")) for t in items}

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
                r.fail("parallel-tickets-blocked", f"{lid} + {rid}",
                       f"share touches {shared} with no blocking edge between them — MUST NOT run "
                       f"in parallel")


def lc_registered(c: Corpus, r: Result) -> None:  # was V12
    """LC registration is checked when a spec CLOSES, not before a ticket is picked up.

    The old shape demanded the answer when the information was thinnest. At spec closing,
    every `touches` already has an area and every boundary already has a name.
    """
    areas = {str(lc.get("area")) for lc in c.lcs if lc.get("area")}
    lcs_per_pc: dict[str, int] = {}
    for lc in c.lcs:
        lcs_per_pc[str(lc.get("component"))] = lcs_per_pc.get(str(lc.get("component")), 0) + 1
    pc_by_id = {str(x.get("id")): x for x in c.pcs}

    seen: set[tuple[str, str]] = set()
    for spec, ticket in c.tickets():
        if str(spec.get("status")) != "closed":
            continue
        for area in listy(ticket, "touches"):
            if area not in areas:
                r.fail("lc-registered", str(ticket.get("id")),
                       f"its spec is already closed, but `{area}` is not registered as an `area` "
                       f"in components.yaml")
        pid = str(ticket.get("component") or "")
        row = pc_by_id.get(pid)
        if row is None or (str(spec.get("id")), pid) in seen:
            continue
        seen.add((str(spec.get("id")), pid))
        if c.mode_of(row) in ("guarded", "deep") and not lcs_per_pc.get(pid):
            r.fail("lc-registered", f"{spec.get('id')} / {pid}",
                   f"spec closed and component with mode `{c.mode_of(row)}` has not one "
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
        r.fail("review-trace", rel, "carries no `reviewed` trace with a date and sha")
        return
    # NOT `block.get("sha") or ""` — for the integer 0 that yields "" and reintroduces the very
    # bug this guards. `.get(key, "")` returns the 0, and str(0) is "0", which is truthy.
    if not str(block.get("sha", "")).strip() or not str(block.get("date", "")).strip():
        r.fail("review-trace", rel, "carries no `reviewed` trace with a date and sha")
        return
    lenses = {str(x) for x in (block.get("lenses") or [])}
    if not lenses:
        r.fail("review-trace", rel, "the `reviewed` trace names not one lens")
    missing = sorted(need - lenses)
    if missing:
        r.fail("review-trace", rel,
               f"lenses {missing} MUST be included — that is what the component's `risk_accepted` demands")


def _only_reviewed_block(diff: str) -> bool:
    """True if a commit's diff on one file ONLY touches the `reviewed:` block.

    This is the OQ-146 fix. The old review-trace compared `sha` against the last commit that changed
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


def review_trace(c: Corpus, r: Result) -> None:  # was V13
    """Review trace follows review INTENSITY, not document depth.

    Narrowed to components with `risk_accepted` `low` or `medium`. At `high` the owner has already
    stated they accept the risk, and demanding a trace there is bookkeeping with no buyer.

    Two narrowings answer the same complaint — that review had become a treadmill:

      ABSENCE still fails. A binding artifact with no trace at all has never been reviewed.
      STALENESS is ADVISORY. A trace has to be fresh at a gate and at spec close, and review-trace cannot see
        a gate; firing on every commit turned every edit into a re-review. G4's fourth star question
        is what holds the gate on a stale review, and it is asked by a human who can see one.
      LENS SET is demanded BEFORE the component's G4 has passed. That is the first review and the
        review that opens the gate — the two the heavy lens is bought for. A re-review after G4 may
        legitimately run structure + prose, so demanding edge-case-hunter there would force either a
        pointless run or a false trace, and a false trace is worse.
    """
    stale_advisory: list[str] = []
    watched = [pc for pc in c.pcs
               if str(pc.get("risk_accepted") or "").strip() in ("low", "medium")]
    if not watched:
        r.skip("review-trace", "no component with risk_accepted low or medium — nothing to guard")
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
        gate_open = passed in ("", "false", "no", "belum")
        # Before G4 passes, the risk-mandated lens set is demanded: that covers the first review and the
        # review that opens the gate. After it passes, a re-review naming any lens satisfies review-trace.
        if not gate_open:
            targets[-1] = (targets[-1][0], set())
        if c.mode_of(pc) != "catalog" and not gate_open:
            targets.append((c.root / f".how/{pid}/SDD-{pid}.md", set()))

    for path, need in targets:
        fm = frontmatter(path)
        if fm is None:
            continue  # not born yet — not review-trace's business
        rel = path.relative_to(c.root).as_posix()
        _reviewed_ok(r, rel, fm.get("reviewed"), need)
        block = fm.get("reviewed")
        if isinstance(block, dict) and block.get("sha"):
            stale = _stale_since(c, rel, str(block["sha"]))
            if stale:
                stale_advisory.append(
                    f"{rel} (changed at {stale[:7]}, reviewed at {str(block['sha'])[:7]})")

    # One trace per SPEC, never one per ticket. Where there is a `SPEC.md` the trace covers it;
    # at size `S` there is none and the trace covers the ticket set as one artifact. Either way the
    # unit reviewed is the spec, which is why the trace lives on the spec row.
    for spec in c.spec_list:
        if not spec.get("tickets"):
            continue
        _reviewed_ok(r, f"specs.yaml:{spec.get('id')}", spec.get("spec_reviewed"),
                     {"edge-case-hunter"})

    if stale_advisory:
        r.skip("review-trace", "advisory — trace stale, re-run before the next gate or spec close: "
               + ", ".join(sorted(stale_advisory)))


def cap_tickets(c: Corpus) -> dict[str, list[dict]]:
    """CAP -> ticket, traced through CAP -> FR -> UC -> ticket. No git, no timeline."""
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
        out[cid] = [t for _, t in c.tickets()
                    if wanted & set(listy(t, "satisfies"))]
    return out


def plan_dates(c: Corpus, r: Result, asof: dt.date) -> None:  # was V14
    """Overdue-ness is computed from the registry itself — the timeline only reinforces, never gates."""
    by_cap = cap_tickets(c)
    timeline = load_yaml(c.root / ".control/generated/timeline.yaml")
    listed = {str(row.get("id")) for row in rows(timeline, "capabilities")
              if str(row.get("state")) == "overdue"} if timeline else None
    if listed is None:
        r.skip("plan-dates", "generated/timeline.yaml does not exist yet — overdue-ness is still computed "
                      "from the registry, but its presence in generated/report is not checked")

    for cap in c.caps:
        cid = str(cap.get("id"))
        end = str(cap.get("planned_end") or "")
        if not end:
            continue
        try:
            due = dt.date.fromisoformat(end)
        except ValueError:
            r.fail("plan-dates", cid, f"`planned_end` `{end}` is not an ISO date")
            continue
        items = by_cap.get(cid, [])
        closed = bool(items) and all(_ticket_status(c, t) == "done" for t in items)
        if closed or due >= asof:
            continue
        late = (asof - due).days
        if listed is not None and cid not in listed:
            r.fail("plan-dates", cid, f"{late} days overdue with nothing delivered, and not flagged "
                               f"`overdue` in generated/timeline")
        else:
            r.fail("plan-dates", cid, f"{late} days overdue with nothing closed")


def chain_links(c: Corpus, r: Result) -> None:  # was V15
    for cap in c.caps:
        if not str(cap.get("goal") or "").strip():
            r.fail("chain-links", str(cap.get("id")), "does not point to a `goal`")
    for fr in c.frs:
        if not str(fr.get("capability") or "").strip():
            r.fail("chain-links", str(fr.get("id")), "does not point to a `capability`")


def memlog_home(c: Corpus, r: Result) -> None:  # was V16
    for path in sorted((c.root / ".control/memlog").glob("*.md")):
        fm = frontmatter(path) or {}
        rel = path.relative_to(c.root).as_posix()
        artifact = str(fm.get("artifact") or "")
        if not artifact:
            r.fail("memlog-home", rel, "has no `artifact:` in frontmatter")
        elif not (c.root / artifact).exists():
            r.fail("memlog-home", rel, f"`artifact:` points to `{artifact}` which does not exist")
    for layer in (".what", ".how"):
        for stray in sorted(c.root.glob(f"{layer}/**/.memlog.md")):
            r.fail("memlog-home", stray.relative_to(c.root).as_posix(),
                   "a memlog MUST NOT live inside the corpus")


def spec_names_release_prd(c: Corpus, r: Result) -> None:  # was V17
    for spec in c.spec_list:
        wid = str(spec.get("id"))
        if not str(spec.get("release") or "").strip():
            r.fail("spec-names-release-prd", wid, "does not name a `release`")
        slugs = listy(spec, "prd")
        if not slugs:
            r.fail("spec-names-release-prd", wid, "does not name a `prd`")
        for slug in slugs:
            if not (c.root / ".what/_prd" / slug).is_dir():
                r.fail("spec-names-release-prd", wid, f"`prd: {slug}` has no folder .what/_prd/{slug}/")


def ticket_status_one_home(c: Corpus, r: Result) -> None:  # was V18
    """A ticket's status has exactly ONE home, and the corpus can point to it.

    That home is the ticket file. `specs.yaml` carries the traceability index — what a ticket
    satisfies, what blocks it, what it touches, what tests it — and a `status` key copied in beside
    them is the second home this validator exists to prevent.

    The file's LOCATION is ours only as far as the root: `{spec_folder}/issues/`. Below that the
    shape belongs to the engine that writes them — one file per ticket, numbered from `01` in
    dependency order — and that number is the tail of the ticket id, which is why `SPEC-3-01`
    finds `issues/01-*.md`.
    """
    for spec, ticket in c.tickets():
        sid = str(ticket.get("id"))
        if str(ticket.get("status") or "").strip():
            r.fail("ticket-status-one-home", sid, "carries a `status` in specs.yaml — status lives in the ticket "
                               "file, and two homes for one fact is how a registry starts lying")
        folder = _spec_folder(spec, ticket)
        if not folder:
            r.fail("ticket-status-one-home", sid, "its spec does not name a `spec_folder`")
            continue
        matches = _ticket_files(c, spec, ticket)
        if not matches:
            r.fail("ticket-status-one-home", sid, f"has no ticket file under {folder}issues/")
            continue
        if _read_status(matches[0]) == "unknown":
            r.fail("ticket-status-one-home", sid, "ticket file states no status — neither a `**Status:**` line nor "
                               "`status:` in frontmatter")


PLATFORM = "_platform"
CROSS_CUTTING = ".how/_platform/cross-cutting.md"
# The section heading entity-one-writer looks for. A heading a SCRIPT matches is a machine-facing key, and
# `language-guide.md` says a key is always English — so the template writes the English one and
# this is what a new corpus carries. The Indonesian form is kept as a READER-side alias, exactly
# like `yes|ya`: a corpus written before this MUST NOT be migrated for a regex.
PLATFORM_DATA_HEADINGS = ("Platform-owned", "Milik platform")
PLATFORM_DATA_HEADING = PLATFORM_DATA_HEADINGS[0]


def entity_one_writer(c: Corpus, r: Result) -> None:  # was V21
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
                r.fail("entity-one-writer", entity,
                       f"claimed as `owns` by both `{owner[entity]}` and `{pid}` — one entity MUST "
                       f"have exactly one owner")
            else:
                owner.setdefault(entity, pid)

    platform = listy(c.components, "platform_owns")
    for entity in platform:
        if entity in owner:
            r.fail("entity-one-writer", entity,
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
                r.fail("entity-one-writer", fid,
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
        r.skip("entity-one-writer", f"`{CROSS_CUTTING}` has no `{PLATFORM_DATA_HEADING}` section yet — "
                      f"{len(entities)} entities with platform_owns are not documented yet: "
                      + ", ".join(sorted(entities)))
        return
    for entity in sorted(entities):
        if entity not in text:
            r.fail("entity-one-writer", entity,
                   f"claimed as `platform_owns` but not named in `{CROSS_CUTTING}` — "
                   f"a platform that owns data MUST document it")


def spec_after_g4(c: Corpus, r: Result) -> None:  # was V22
    """A spec MUST NOT touch a component whose G4 has not passed and whose mode is not catalog.

    `catalog` skips G4 on purpose, so it is not an exception — it is part of the rule.
    """
    pc_by_id = {str(x.get("id")): x for x in c.pcs}
    seen: set[tuple[str, str]] = set()
    for spec, ticket in c.tickets():
        pid = str(ticket.get("component") or "")
        row = pc_by_id.get(pid)
        if row is None:
            continue
        key = (str(spec.get("id")), pid)
        if key in seen:
            continue
        seen.add(key)
        mode = c.mode_of(row)
        if mode == "catalog":
            continue
        if mode not in MODES:
            r.fail("spec-after-g4", pid, f"`mode: {mode}` is not one of {list(MODES)}")
            continue
        passed = row.get("g4_passed")
        if not passed or str(passed).strip().lower() in ("false", "no", "belum"):
            r.fail("spec-after-g4", f"{spec.get('id')} / {pid}",
                   f"spec touches a component with mode `{mode}` whose `g4_passed` has not been set")


def high_risk_named(c: Corpus, r: Result) -> None:  # was V23
    """`risk_accepted: high` on a sensitive component demands a NAMED acceptance in `risk_accepted_by`.

    On a component that touches nothing on that list, `high` is FREE. The control is
    disclosure, not veto — the owner may still choose quickly, just not without knowing what
    they are wagering.

    It used to demand that the record be a `DEC-` file, which made accepting a risk cost a document and
    put the fact in a second home while `components.yaml` already had the field for it. A person and a
    date, written where the risk is set, IS the disclosure. A `DEC-` id is still accepted and still has
    to resolve: a repo pointing at a decision is making a checkable claim, and a pointer to a decision
    that does not exist is worse than no pointer.
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
            r.fail("high-risk-named", pid,
                   f"`risk_accepted: high` while `risk_note` mentions {hits}, and "
                   f"`risk_accepted_by` names nobody — a person and a date is enough")
        elif ref.startswith("DEC-") and ref not in known:
            r.fail("high-risk-named", pid, f"`risk_accepted_by: {ref}` does not exist in decisions.yaml")


def defect_root_cause(c: Corpus, r: Result) -> None:  # was V20
    needs_link = {"requirement", "architecture"}
    for defect in c.defect_list:
        did = str(defect.get("id"))
        cause = str(defect.get("root_cause") or "")
        if cause not in needs_link:
            continue
        if not listy(defect, "violates"):
            r.fail("defect-root-cause", did, f"has `root_cause` `{cause}` but `violates` is empty")
        if str(defect.get("status")) == "fixed" and not str(defect.get("decision") or "").strip():
            r.fail("defect-root-cause", did,
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
DERIVED = (".control/generated/", RENDERED_WHAT + "/", RENDERED_HOW + "/")
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
# one yet. Scanning it made cites-resolve unsatisfiable in both directions: a fresh install went RED on 69
# such lines before G1 had run, and a mature one stayed quiet only by accident. A method guide that
# cites a method file IS checked, but here in the package where it can be fixed — see
# tests/kit-integrity.test.mjs. A product cannot fix a guide `update` overwrites.
#
# The BMad skill trees are the same class under whichever host the installer wrote them to. EVERY
# host MUST be listed, and there are three: `.claude/skills/bmad-` alone left the `.agents/` copy of
# one identical template failing, which reads as a defect in that product rather than an omission
# here. Listing two then left the `.agent/` copy failing the same way — the singular host is a
# separate directory from `.agents/`, not a prefix of it, and a product carrying all three saw the
# same worked example reported once per host it was missing.
#
# `wdi-*` skills are OURS and are deliberately NOT here. They MUST NOT cite a product file that
# does not exist unless the cite is a placeholder.
INSTALLED = (
    ".constitution/method/",
    ".claude/skills/bmad-",
    ".agents/skills/bmad-",
    ".agent/skills/bmad-",
    # The method's own skills are installed by `update` the same way the guides are, and a consumer
    # can no more fix a cite in one than in a guide. Their cites are checked where the fix is made —
    # `kit-integrity` in the package. And one of them, `wdi-upgrade`, deliberately names paths of the
    # OLD shape to probe for them; read as claims, every probe would be a finding.
    ".claude/skills/wdi-",
    ".agents/skills/wdi-",
    ".agent/skills/wdi-",
)

# The extension list is deliberately WIDE. A narrow one does not make cites-resolve safer — it makes it
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


def cites_resolve(c: Corpus, r: Result) -> None:  # was V24
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
                r.fail("cites-resolve", rel, f"cites `{cited}` which does not exist")
    if not scanned:
        r.skip("cites-resolve", "no file was scanned")


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


def container_built(c: Corpus, r: Result) -> None:  # was V25
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
        r.skip("container-built", "`containers:` is not registered yet")
        return

    built: dict[str, bool] = {}
    for ctr in containers:
        cid = str(ctr.get("id") or "").strip()
        if not cid:
            r.fail("container-built", "containers", "a container has no `id`")
            continue
        flag = ctr.get("built")
        if not isinstance(flag, bool):
            r.fail("container-built", cid, "`built` MUST be a bool — true if we write its content, false if someone else implements it")
            continue
        built[cid] = flag

    # (1) code-map heading = EXACTLY a container with `built: true`
    headings = map_container_headings(c.root)
    if headings is None:
        r.fail("container-built", ".control/structure-codebase.md", "the code map does not exist, so container headings cannot be compared")
    else:
        for h in headings:
            if h not in built:
                r.fail("container-built", f"code map §{h}", "heading is not a registered container — register it, or it is not a container")
            elif not built[h]:
                r.fail("container-built", f"code map §{h}", "`built: false` MUST NOT have a heading — there is no code of ours inside it")
        for cid, flag in sorted(built.items()):
            if flag and cid not in headings:
                r.fail("container-built", cid, "`built: true` MUST have a heading in the code map")

    # (2) `built: false` MUST NOT be used by an LC, and (3) MUST NOT appear in a PC's `containers:`
    #
    # An EMPTY container is legal while the answer does not exist yet. Screens are known as soon as
    # DESIGN.md is written at G2; containers are born at G3. Blocking the UX landing until then bought
    # nothing and cost a half-placed artifact somebody had to come back to.
    #
    # The deadline is derived, not scheduled: once the LC's own PC lists containers, the information
    # exists and the answer is owed. Silent before G3, automatic after, and no gate in between.
    pc_containers = {str(pc.get("id")): listy(pc, "containers") for pc in c.pcs}
    for lc in c.lcs:
        ctr = str(lc.get("container") or "").strip()
        lid = str(lc.get("id") or "LC-?")
        if not ctr:
            if pc_containers.get(str(lc.get("component") or "")):
                r.fail("container-built", lid,
                       "has no `container` while its Product Component already lists one — the answer "
                       "exists now, so a screen with no deployable home is a gap rather than a wait")
            continue
        if built.get(ctr) is False:
            r.fail("container-built", lid, f"names container `{ctr}` which is `built: false`")
        elif ctr not in built:
            r.fail("container-built", lid, f"names container `{ctr}` which is not registered")

    # (4) PC x container matrix — this field is its SSOT, and it MUST be complete at G3
    for pc in c.pcs:
        pid = str(pc.get("id") or "?")
        listed = listy(pc, "containers")
        if not listed:
            r.fail("container-built", pid, "`containers:` is empty — every PC MUST live in at least one container (a G3 debt)")
            continue
        for ctr in listed:
            if ctr not in built:
                r.fail("container-built", pid, f"`containers:` names `{ctr}` which is not registered")
            elif not built[ctr]:
                r.fail("container-built", pid, f"`containers:` names `{ctr}` which is `built: false` — the data lives there by definition, so the row tells us nothing")

    # (5) L3 — only for `built: true`, and only ones that hold more than one PC
    pcs_per: dict[str, list[str]] = {}
    for pc in c.pcs:
        for ctr in listy(pc, "containers"):
            pcs_per.setdefault(ctr, []).append(str(pc.get("id") or "?"))
    for path in sorted((c.root / ".how" / "_platform").glob("c4-l3-*.md")):
        cid = path.name[len("c4-l3-"):-len(".md")]
        if cid not in built:
            r.fail("container-built", path.relative_to(c.root).as_posix(),
                   f"L3 for `{cid}` which is not a registered container")
        elif not built[cid]:
            r.fail("container-built", path.relative_to(c.root).as_posix(),
                   f"`{cid}` `built: false` MUST NOT have an L3 — not one box inside it is ours to draw")
    for cid, pids in sorted(pcs_per.items()):
        if built.get(cid) and len(pids) > 1:
            l3 = c.root / ".how" / "_platform" / f"c4-l3-{cid}.md"
            if not l3.exists():
                r.fail("container-built", cid, f"holds {len(pids)} PCs, so `c4-l3-{cid}.md` MUST exist")



# The `critical` column value is machine-matched, so it is machine-facing and its canonical form
# is English `yes`. `ya` is still accepted: a corpus that wrote it before this rule took effect
# MUST NOT be forced to migrate just so a regex can be tidier. The word boundary keeps `ya` from
# matching inside other words.


def custom_room_declared(c: Corpus, r: Result) -> None:  # was V27
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
                                `ratified_by:`, and they are filled by a spec's distillation

    Demanding `scope:` and `purpose:` of those would be demanding a declaration of files whose
    role is already fixed by the layout. What custom-room-declared exists to guard is the file somebody ADDS.

    Only `.md` is looked at. A script in the room — `inventory-readers.py` is the one the package
    seeds — is not an ad-hoc rule and has nowhere to put frontmatter.
    """
    room = c.root / ".constitution" / "project"
    if not room.is_dir():
        r.skip("custom-room-declared", "the `.constitution/project/` room does not exist yet — it is seeded at install")
        return
    structural = {"README.md", "constitution.md"}
    files = [p for p in sorted(room.rglob("*.md"))
             if p.name not in structural and not p.name.startswith("codebase-")]
    if not files:
        r.skip("custom-room-declared", "the `.constitution/project/` room is empty, and that is a valid state — "
                      "a generic rule MUST NOT be moved here just to give the room content")
        return
    dec_ids = {str(d.get("id")) for d in c.decs}
    for path in files:
        rel = path.relative_to(c.root).as_posix()
        fm = frontmatter(path)
        if fm is None:
            r.fail("custom-room-declared", rel, "has no frontmatter")
            continue
        if str(fm.get("scope") or "").strip() != "project":
            r.fail("custom-room-declared", rel, "`scope:` MUST contain exactly `project`")
        if not str(fm.get("purpose") or "").strip():
            r.fail("custom-room-declared", rel, "`purpose:` is empty — one line: what this rule guards")
        over = str(fm.get("overrides") or "").strip()
        dec = str(fm.get("decision") or "").strip()
        if over:
            if not (c.root / over).exists():
                r.fail("custom-room-declared", rel, f"`overrides:` points to `{over}` which does not exist — "
                                   f"the rebutted rule may already be gone")
            if not dec:
                r.fail("custom-room-declared", rel, "rebuts a generic rule without `decision:` — "
                                   "a rebuttal MUST have a `DEC-` that decided it")
            elif dec not in dec_ids:
                r.fail("custom-room-declared", rel, f"`decision: {dec}` is not registered in decisions.yaml")
        elif dec:
            r.fail("custom-room-declared", rel, "`decision:` is set without `overrides:` — "
                               "name which rule is rebutted, or drop `decision:`")


def id_allocated_once(c: Corpus, r: Result) -> None:  # was V28
    """One id, one row — across every file the requirement registry is split into.

    The split into `goals.yaml` plus one `requirements-<slug>.yaml` per PRD bought
    one writer per file, and cost exactly one new failure mode: two initiatives written in parallel
    can both allocate `FR-12`. Nothing before this saw it. refs-resolve builds its `defined` set as a SET, so
    a duplicate id silently collapsed into one entry and every reference to it still resolved.

    The id sequence is global to the product — that is what lets a ticket say `satisfies: [FR-12]`
    without also naming which PRD it came from. This is the check that keeps it true now that the
    rows live in more than one file.
    """
    where: dict[str, list[str]] = {}
    for name, doc in sorted(c.requirement_files.items()):
        for key in REQUIREMENT_KEYS:
            for row in rows(doc, key):
                rid = str(row.get("id") or "").strip()
                if rid:
                    where.setdefault(rid, []).append(name)
    for rid, sources in sorted(where.items()):
        if len(sources) > 1:
            r.fail("id-allocated-once", rid, "is declared in " + ", ".join(f"`{s}.yaml`" for s in sources)
                   + " — an id is allocated ONCE, and the sequence is global to the product")
    if not where:
        r.skip("id-allocated-once", "no requirement row in any registry file yet")


def run_checks(c: Corpus, asof: dt.date) -> Result:
    r = Result()
    # uc-catalogue-matches (was V26) is RETIRED: it compared the SRS's hand-written UC table with
    # `usecases.yaml`. The table is a pointer now and the rendered SRS shows the rows, so there are
    # no two copies left to compare.
    # V19 is REPEALED. It checked one line item — an `RTR-` file in .control/reports/ — and the
    # retrospective it archived was the only thing spec size `L` ever decided. Both went together.
    for fn in (goal_has_fr, fr_has_uc, uc_scheduled, ticket_has_test, nfr_has_enforcer, refs_resolve, no_cycles, applied_dec_touches, locked_gate_passed, parallel_tickets_blocked, lc_registered, review_trace, chain_links, memlog_home, spec_names_release_prd, ticket_status_one_home, defect_root_cause, entity_one_writer, spec_after_g4, high_risk_named, cites_resolve, container_built, custom_room_declared, id_allocated_once):
        fn(c, r)
    plan_dates(c, r, asof)
    return r


# ------------------------------------------------------------------ generator


def _spec_folder(spec: dict, ticket: dict) -> str:
    """`spec_folder` belongs to the SPEC — one per spec, not one per spec x component.

    A ticket row is still read as a fallback, because that is where a repo written before the
    rename put it, and a validator that reports every one of those rows as missing a folder is
    reporting the migration, not a defect.
    """
    return str(spec.get("spec_folder") or ticket.get("spec_folder") or "").strip()


def _ticket_files(c: Corpus, spec: dict, ticket: dict) -> list[Path]:
    """`{spec_folder}/issues/<NN>-<slug>.md`, found by the number at the tail of the ticket id.

    The full id is tried too, so a product that names its files after the whole id is not punished
    for a convention this method never demanded of it.
    """
    folder = _spec_folder(spec, ticket)
    if not folder:
        return []
    tid = str(ticket.get("id") or "")
    issues = c.root / folder / "issues"
    for stem in (tid.rsplit("-", 1)[-1], tid):
        if not stem:
            continue
        found = sorted(issues.glob(f"{stem}-*.md"))
        if found:
            return found
    return []


def status_in(text: str) -> str:
    """Two spellings, one home.

    The engine writes `**Status:** ready-for-agent` as a body line, because a ticket file is a
    tracker payload and trackers do not read YAML frontmatter. A product that keeps `status:` in
    frontmatter instead is not wrong, so both are read. Reading two spellings of one field in one
    file is not two homes; it is one home written two ways.

    Takes TEXT, not a path, because timeline.py asks the same question of historical revisions
    pulled out of git, where there is no file to open.
    """
    m = FM.match(text)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            fm = {}
        if isinstance(fm, dict) and str(fm.get("status") or "").strip():
            return str(fm["status"]).strip()
    m = re.search(r"^\*\*Status:\*\*\s*(.+?)\s*$", text, re.M)
    return m.group(1).strip() if m else "unknown"


def _read_status(path: Path) -> str:
    try:
        return status_in(path.read_text(encoding="utf-8"))
    except OSError:
        return "unknown"


def _ticket_status(c: Corpus, spec: dict, ticket: dict) -> str:
    matches = _ticket_files(c, spec, ticket)
    return _read_status(matches[0]) if matches else "unknown"


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
    """The frontier, spec by spec: each `parallel` group is what can be started at once."""
    out = []
    per_spec: dict[str, list[dict]] = {}
    for spec, ticket in c.tickets():
        per_spec.setdefault(str(spec.get("id")), []).append(ticket)
    for wid in sorted(per_spec):
        items = per_spec[wid]
        done: set[str] = set()
        pending = {str(t.get("id")): set(listy(t, "blocked_by")) for t in items}
        order = []
        while pending:
            ready = sorted(k for k, deps in pending.items() if not (deps - done))
            if not ready:  # cycle — no-cycles has already reported it
                order.append({"blocked": sorted(pending)})
                break
            order.append({"parallel": ready})
            done |= set(ready)
            for k in ready:
                pending.pop(k)
        out.append({"spec": wid, "order": order})
    return {"dag": out}


def gen_rtm(c: Corpus) -> dict:
    cap_goal = {str(x.get("id")): str(x.get("goal", "")) for x in c.caps}
    ucs_for_fr: dict[str, list[str]] = {}
    for uc in c.ucs:
        for fr in listy(uc, "satisfies"):
            ucs_for_fr.setdefault(fr, []).append(str(uc.get("id")))
    tickets_for_uc: dict[str, list[tuple[dict, dict]]] = {}
    for spec, ticket in c.tickets():
        for uc in listy(ticket, "satisfies"):
            tickets_for_uc.setdefault(uc, []).append((spec, ticket))
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
            lines.append({**base, "UC": "", "ticket": "", "spec": "", "release": "",
                          "test": [], "status": "", "green": False,
                          "exempt": exempt,
                          "broken_at": "no_uc" if exempt else "UC"})
            continue
        for uid in ucs:
            pairs = sorted(tickets_for_uc.get(uid, []), key=lambda p: str(p[1].get("id")))
            if not pairs:
                lines.append({**base, "UC": uid, "ticket": "", "spec": "", "release": "",
                              "test": [], "status": "", "green": False, "exempt": False,
                              "broken_at": "ticket"})
                continue
            for spec, ticket in pairs:
                status = _ticket_status(c, spec, ticket)
                tests = listy(ticket, "tests")
                broken = ""
                if not tests:
                    broken = "test"
                elif status != "done":
                    broken = "status"
                lines.append({**base, "UC": uid, "ticket": str(ticket.get("id")),
                              "spec": str(spec.get("id")), "release": str(spec.get("release", "")),
                              "test": tests, "status": status, "exempt": False,
                              "green": broken == "", "broken_at": broken})
    return {"rtm": lines}


def gen_status(c: Corpus, rtm: dict, result: Result) -> dict:
    lines = rtm.get("rtm") or []
    counted = [line for line in lines if not line.get("exempt")]
    exempt = len(lines) - len(counted)
    green = sum(1 for line in counted if line.get("green"))
    per_spec = []
    for spec in c.spec_list:
        wid = str(spec.get("id"))
        items = [t for sp, t in c.tickets() if str(sp.get("id")) == wid]
        done = sum(1 for t in items if _ticket_status(c, spec, t) == "done")
        per_spec.append({"spec": wid, "status": spec.get("status"),
                         "tickets_done": done, "tickets_total": len(items),
                         "work_progress": _pct(done, len(items))})
    applicable = 26  # goal-has-fr..id-allocated-once minus V10 and V19, both repealed
    return {
        "promise_progress": _pct(green, len(counted)),
        "rtm_rows": {"green": green, "counted": len(counted),
                      "excluded_no_uc": exempt},
        "work_progress": per_spec,
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
    # `Whose` splits the open rows by who can act, and whether anyone may act yet. A flat "25 open"
    # is what made a six-item list read as twenty-five items of homework; the owner's number is the
    # only one they can do anything about. templates/questions.md owns the vocabulary.
    whose: dict[str, int] = {"owner": 0, "run": 0, "frozen": 0, "unstated": 0}
    for name in ("blocking", "assumptions", "external", "answered"):
        path = c.root / ".control/questions" / f"{name}.md"
        rows_n = 0
        if path.exists():
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.startswith("| OQ-"):
                    continue
                rows_n += 1
                # `answered` is closed; `external` needs no `Whose` — sitting in that file already
                # says who acts, and it is reported as its own line rather than folded in.
                if name in ("answered", "external"):
                    continue
                cells = [x.strip() for x in line.strip().strip("|").split("|")]
                key = "unstated"
                for cell in cells:
                    low = cell.lower()
                    if low == "owner":
                        key = "owner"
                    elif low.startswith("run:"):
                        key = "run"
                    elif low.startswith("frozen:"):
                        key = "frozen"
                    else:
                        continue
                    break
                whose[key] += 1
        out[name] = rows_n
    out["open_by_whose"] = whose
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


def _hname(heading: str) -> str:
    """A heading's NAME: lower-cased, with any leading `3.` / `4.2` / `§5` numbering dropped. Section
    numbers moved between kits (Non-Goals was §7 in one, §5 in the next) and a migrated document may
    keep its old ones — a page that keyed on the number went blind on exactly those corpora."""
    return re.sub(r"^\s*(?:§\s*)?\d+(?:\.\d+)*\.?\s*", "", heading.strip().lower())


def _section(path: Path, heading: str) -> str:
    """Extract one `## <heading>` section from a markdown file, as-is. Matched by name, not number."""
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out: list[str] = []
    inside = False
    want = _hname(heading)
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = _hname(line[3:]).startswith(want)
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
    """The ONE page read at G3 — and it MUST answer all seven of G3's questions, or the owner is
    back to opening files. Before this it answered four: the actor list, the UC catalogue, the
    domain model, and the inventories. The three it left to other files were the AD-N invariants,
    the cross-component business rules, and the glossary — questions 5, 6, and 7.

    Every table here is a VIEW. The UC catalogue's home is `usecases.yaml`; the invariants' home is
    the spine; the PC x container matrix's home is `components.yaml`. One fact, one home, one view.
    """
    parts = ["# blueprint\n", PAGE_HEADER,
             "\nThis is what the owner reads at **G3 Blueprint** — one page, every one of the gate's "
             "seven questions answerable from it. Its content is affected by neither `mode` nor "
             "`risk_accepted`.\n"]

    crit = sum(1 for uc in c.ucs if uc.get("critical"))
    parts.append(f"\n## Use case catalogue\n\n**{len(c.ucs)} use cases**, {crit} marked `critical`. "
                 f"Rendered from `usecases.yaml`.\n\n{_uc_table(c.ucs)}")

    parts.append("\n\n## Actor list\n")
    for pc in c.pcs:
        pid = str(pc.get("id"))
        block = _section(c.root / f".what/{pid}/SRS-{pid}.md", "Actor Register")
        name = str(pc.get("name") or "").strip()
        parts.append(f"\n### {pid} — {name}\n" if name else f"\n### {pid}\n")
        parts.append(_demote(block) if block else "_no § Actor Register in this component's SRS yet._")

    parts.append("\n## Domain model\n")
    for pc in c.pcs:
        pid = str(pc.get("id"))
        block = _body(c.root / f".what/{pid}/03-domain/domain-model.md")
        parts.append(f"\n### {pid}\n")
        parts.append(_demote(block) if block else "_no `03-domain/domain-model.md` yet._")

    parts.append("\n## Business rules binding more than one component\n")
    br = _section(c.root / ".what" / "business-rules.md", "Rules")
    parts.append(f"\n{br}\n" if br else "\n_no `.what/business-rules.md` § Rules yet._\n")

    parts.append("\n## Invariants — the spine\n")
    parts.append("\nRendered from `.how/_platform/ARCHITECTURE-SPINE.md`. G3 asks of every row: does it "
                 "name the concrete failure it prevents, and would breaking it in one component break "
                 "another?\n\n" + _ad_table(_ad_blocks(c.root)))

    parts.append("\n\n## Containers, and which components live in each\n")
    parts.append("\nRendered from `components.yaml` — the table C4 L2 used to carry by hand.\n\n"
                 + _pc_container_table(c))
    c4 = _body(c.root / ".how" / "_platform" / "c4-l2-containers.md")
    if c4:
        parts.append(f"\n\n### C4 L2 — `c4-l2-containers.md`\n\n{_demote(c4)}")

    parts.append("\n\n## Three inventories\n")
    for kind, name in (("db", "table"), ("api", "endpoint"), ("screen", "screen")):
        block = _body(c.root / f".how/_platform/inventory-{kind}.md")
        parts.append(f"\n### List of {name}s — `inventory-{kind}.md`\n")
        parts.append(_demote(block) if block else f"_no `inventory-{kind}.md` yet._")

    parts.append("\n## Error envelope\n")
    cc = c.root / ".how" / "_platform" / "cross-cutting.md"
    env = _section(cc, "Error envelope")
    cat = _section(cc, "Error catalogue")
    parts.append(f"\n{env}\n" if env else "\n_no § Error envelope in `cross-cutting.md` yet._\n")
    if cat:
        parts.append(f"\n### Error catalogue\n\n{cat}\n")

    parts.append("\n## Glossary\n")
    gl = _section(c.root / ".control" / "product-glossary.md", "Entries")
    parts.append(f"\n{gl}\n" if gl.strip() else "\n_no entry in `product-glossary.md` yet._\n")

    return "\n".join(parts) + "\n"


def _cell(value: object, limit: int = 110) -> str:
    """One table row, shortened. The full-length source stays in the registry — this is just a view."""
    text = " ".join(str(value or "").split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _full(value: object, _limit: int = 0) -> str:
    """One table cell on a HUMAN page: whitespace collapsed, pipes escaped, never shortened. The
    rendered trees are the complete document — a cell ending in `…` would send the reader back to
    the registry, which is exactly the trip the page exists to save. `_limit` is accepted and
    ignored so a call site shared with `_cell` reads the same."""
    return " ".join(str(value or "").split()).replace("|", "\\|")


def _by_id(items: list[dict]) -> list[dict]:
    """`FR-2` before `FR-10`. YAML order is whatever the last writer left; a page reads in id order."""
    def key(row: dict) -> tuple:
        m = re.match(r"^([A-Za-z]+)-(\d+)$", str(row.get("id") or ""))
        return (m.group(1), int(m.group(2))) if m else (str(row.get("id") or ""), 0)
    return sorted(items, key=key)


def _doc_title(path: Path, fallback: str) -> str:
    """The working document's own title — frontmatter `title:` first, else its first `# ` line."""
    if not path.exists():
        return fallback
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = FM.match(text)
    if fm:
        m = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", fm.group(0), re.M)
        if m and m.group(1).strip():
            return m.group(1).strip()
    m = re.search(r"^# (.+?)\s*$", text, re.M)
    return m.group(1).strip() if m else fallback


def _req_block(row: dict, level: int = 4) -> str:
    """One requirement, whole: heading, the full statement when the row carries one, then the fields
    a reader checks it by. This is the shape the PRD used to write by hand, rebuilt from the row."""
    rid = str(row.get("id") or "")
    title = _text(row)
    out = [f"{'#' * level} {rid} — {title}", ""]
    statement = " ".join(str(row.get("statement") or "").split())
    if statement and statement.rstrip(".").lower() != title.rstrip(".").lower():
        out += [statement, ""]
    fields = []
    if rid.startswith("FR"):
        proof = _proof(row)
        fields.append(("Proof of done", proof or "—"))
        if row.get("capability"):
            fields.append(("Capability", f"`{row.get('capability')}`"))
    elif rid.startswith("NFR"):
        enforced = listy(row, "enforced_by") or ([row.get("enforced_by")] if row.get("enforced_by") else [])
        fields.append(("Enforced by", ", ".join(str(x) for x in enforced) or "—"))
        if row.get("goal"):
            fields.append(("Serves", f"`{row.get('goal')}`"))
    if row.get("component"):
        fields.append(("Component", f"`{row.get('component')}`"))
    out += [f"**{k}:** {v}  " for k, v in fields]
    return "\n".join(out).rstrip() + "\n"


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
    """Table of CANDIDATE tasks. One row per `FR`, since that is a spec's ideal shape."""
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
             "task; the spec in `specs.yaml` is the real one. One row MAY become one spec, and three "
             "neighboring rows MAY be merged into one — that merge is a human decision made when the "
             "spec is opened.\n"]
    if not have_mandays:
        parts.append("\n**With no `estimate_mandays` on a single `CAP`**, the Load column is empty and "
                     "this output is only as good as a T-shirt-size estimate. It MUST be reported as such.\n")

    parts.append("\n| Task | FR | Component | mode | Exposure | Load | Priority | Depends on | Release |")
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


ID_CITE_RE = re.compile(r"\b(?:CAP|FR|NFR)-\d+\b")


def _cited_ids(text: str) -> list[str]:
    """Every CAP-N / FR-N / NFR-N cited in TEXT, in first-seen order, no repeats."""
    seen: set[str] = set()
    out: list[str] = []
    for m in ID_CITE_RE.finditer(text):
        if m.group(0) not in seen:
            seen.add(m.group(0))
            out.append(m.group(0))
    return out


def _subsection(path: Path, parent: str, sub: str) -> str:
    """Extract one `### <sub>` subsection from within a `## <parent>` block, as-is."""
    block = _section(path, parent)
    if not block:
        return ""
    lines = block.splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("### "):
            if inside:
                break
            inside = _hname(line[4:]).startswith(_hname(sub))
            continue
        if inside:
            out.append(line)
    return "\n".join(out).strip("\n")


def _has_rows(block: str) -> bool:
    """True if a `## Open` table has a real data row — not just header, separator, and the
    scaffold's own `| — | — | ... |` placeholder for "nothing here yet"."""
    lines = [ln.strip() for ln in block.splitlines() if ln.strip().startswith("|")]
    for line in lines[2:]:
        first = line.strip("|").split("|", 1)[0].strip()
        if first and first not in ("—", "-"):
            return True
    return False


def _filtered_rows(block: str, needles: list[str]) -> str:
    """A markdown table, kept whole for its header and separator, with only the DATA rows that
    mention one of `needles` (case-insensitive substring). Returns "" if nothing matched.

    This is how the brief and PRD deliverables show only the open questions and assumptions that
    are actually theirs, without `.control/questions/` carrying a field that says so.
    """
    if not block.strip():
        return ""
    lines = block.splitlines()
    out: list[str] = []
    header_seen = 0
    kept_any = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and header_seen < 2:
            out.append(line)
            header_seen += 1
            continue
        if stripped.startswith("|"):
            if any(n.lower() in line.lower() for n in needles):
                out.append(line)
                kept_any = True
            continue
        out.append(line)
    return "\n".join(out).strip("\n") if kept_any else ""


def _glossary_terms_used(root: Path, text: str) -> str:
    """`## Entries` bullets from `product-glossary.md` whose term is a whole word somewhere in TEXT."""
    path = root / ".control" / "product-glossary.md"
    entries = _section(path, "Entries")
    if not entries:
        return ""
    out = []
    for line in entries.splitlines():
        m = re.match(r"^-\s*\*\*(.+?)\*\*", line.strip())
        if m and re.search(rf"\b{re.escape(m.group(1))}\b", text, re.I):
            out.append(line)
    return "\n".join(out)


AD_HEAD_RE = re.compile(r"^###\s+(AD-\d+)\s+[—-]+\s+(.*?)\s*$", re.M)


def _ad_blocks(root: Path) -> list[dict]:
    """Every `### AD-N — title` block in the spine, with its Binds / Prevents / Rule lines.

    The spine is the SSOT for an invariant and `AD-` is edited in place — so nothing else may hold
    its text. The rendered SDD gets it from here, which is what made the verbatim quote in the
    working SDD unnecessary, and unsafe.
    """
    text = _body(root / ".how" / "_platform" / "ARCHITECTURE-SPINE.md")
    if not text:
        return []
    heads = list(AD_HEAD_RE.finditer(text))
    out: list[dict] = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        block = text[m.end():end]
        field = lambda name: (re.search(rf"\*\*{name}:\*\*\s*(.*)", block) or [None, ""])[1].strip()
        out.append({"id": m.group(1), "title": m.group(2).strip(),
                    "binds": field("Binds"), "prevents": field("Prevents"), "rule": field("Rule")})
    return out


def _binds_pc(ad: dict, pid: str, lc_ids: set[str]) -> bool:
    b = ad.get("binds", "")
    if not b:
        return False
    if re.search(r"\ball\b", b):
        return True
    return bool(re.search(rf"(?<![\w-]){re.escape(pid)}(?![\w-])", b)) or any(l in b for l in lc_ids)


def _ad_table(ads: list[dict], pid: str | None = None, lc_ids: set[str] | None = None) -> str:
    if not ads:
        return "_no `AD-N` in the spine yet._"
    if pid is None:
        rows_out = ["| id | Invariant | Binds | Prevents | Rule |", "| --- | --- | --- | --- | --- |"]
        for ad in _by_id(ads):
            rows_out.append(f"| `{ad['id']}` | {_full(ad['title'])} | {_full(ad['binds'], 60)} "
                            f"| {_full(ad['prevents'])} | {_full(ad['rule'])} |")
    else:
        rows_out = ["| id | Invariant | Binds this component | Prevents | Rule |",
                    "| --- | --- | --- | --- | --- |"]
        for ad in _by_id(ads):
            hit = "**yes**" if _binds_pc(ad, pid, lc_ids or set()) else "no"
            rows_out.append(f"| `{ad['id']}` | {_full(ad['title'])} | {hit} "
                            f"| {_full(ad['prevents'])} | {_full(ad['rule'])} |")
    return "\n".join(rows_out)


def _uc_table(ucs: list[dict]) -> str:
    if not ucs:
        return "_no use case registered yet._"
    rows_out = ["| id | Use case | Component | Satisfies | critical |",
                "| --- | --- | --- | --- | --- |"]
    for uc in _by_id(ucs):
        sat = ", ".join(f"`{x}`" for x in listy(uc, "satisfies")) or "—"
        rows_out.append(f"| `{uc.get('id')}` | {_full(uc.get('title'))} | `{uc.get('component', '')}` "
                        f"| {sat} | {'yes' if uc.get('critical') else 'no'} |")
    return "\n".join(rows_out)


def _lc_table(lcs: list[dict]) -> str:
    if not lcs:
        return "_no Logical Component registered yet._"
    rows_out = ["| id | Name | Type | Container |", "| --- | --- | --- | --- |"]
    for lc in _by_id(lcs):
        rows_out.append(f"| `{lc.get('id')}` | {_full(lc.get('name'))} | `{lc.get('lc_type', '—')}` "
                        f"| `{lc.get('container') or '—'}` |")
    return "\n".join(rows_out)


def _pc_container_table(c: Corpus) -> str:
    """The PC x container matrix, RENDERED from `components.yaml`. This is the table C4 L2 used to
    carry by hand and `container-built` had to keep honest; rendered, there is nothing to compare."""
    built = [ct for ct in rows(c.components, "containers") if ct.get("built")]
    if not built:
        return "_no `built: true` container registered yet._"
    rows_out = ["| Container | What | Product Components living in it |", "| --- | --- | --- |"]
    for ct in built:
        cid = str(ct.get("id"))
        pcs = [str(pc.get("id")) for pc in c.pcs if cid in listy(pc, "containers")]
        rows_out.append(f"| `{cid}` | {_full(ct.get('what'))} | "
                        f"{', '.join(f'`{x}`' for x in pcs) or '—'} |")
    return "\n".join(rows_out)


def _slot_files(root: Path, layer: str, pid: str, slot: str) -> list[Path]:
    d = root / layer / pid / slot
    return sorted(d.glob("*.md")) if d.is_dir() else []


def _inline(path: Path, level: int = 3) -> str:
    """A whole working file inlined under a heading that names it, its own headings demoted."""
    body = _body(path)
    if not body:
        return ""
    return f"\n{'#' * level} `{path.name}`\n\n{_demote(body, by=level - 1)}\n"


def _text(row: dict) -> str:
    """The one-line text of a registry row. `title` is what every corpus written so far carries; the
    other two are accepted so a row is never rendered blank because of a field name."""
    return str(row.get("title") or row.get("statement") or row.get("text") or "")


def _proof(row: dict) -> str:
    return str(row.get("proof") or row.get("proof_of_done") or "")


def page_brief(c: Corpus) -> str:
    """The brief's own sections verbatim, plus what only the registry and `.control/questions/`
    can complete: Goals rendered from `goals.yaml`, and the open Assumptions and
    Prerequisites rows. The page read at G1. Nobody edits it — it is regenerated from its sources.
    """
    path = c.root / ".what" / "_product-brief" / "brief.md"
    if not path.exists():
        return "# brief\n\n" + PAGE_HEADER + "\n\n_no `.what/_product-brief/brief.md` yet._\n"

    parts = [f"# {_doc_title(path, 'Product Brief')}\n", PAGE_HEADER]
    for heading in ("Why", "The Problem", "The Solution", "What Makes This Different",
                    "Who This Serves"):
        block = _section(path, heading)
        if block:
            parts.append(f"\n## {heading}\n\n{block}\n")

    parts.append("\n## Goals\n")
    if c.goals:
        parts.append("\nRendered from `.control/registry/goals.yaml`.\n")
        for g in _by_id(c.goals):
            title = _text(g)
            parts.append(f"\n### {g.get('id')} — {title}\n")
            statement = " ".join(str(g.get("statement") or "").split())
            if statement and statement.rstrip(".").lower() != title.rstrip(".").lower():
                parts.append(f"\n{statement}\n")
            if g.get("measure"):
                parts.append(f"\n**Measure:** {_full(g.get('measure'))}  ")
            if g.get("why"):
                parts.append(f"**Why:** {_full(g.get('why'))}  ")
    else:
        parts.append("\n_no goal registered yet._")

    success = _section(path, "Success Criteria")
    if success:
        parts.append(f"\n\n## Success Criteria\n\n{success}\n")

    scope = _section(path, "Scope")
    if scope:
        parts.append(f"\n## Scope\n\n{scope}\n")

    constraints = _section(path, "Constraints")
    if constraints:
        parts.append(f"\n## Constraints\n\n{constraints}\n")

    parts.append("\n## Assumptions\n")
    open_assumptions = _section(c.root / ".control" / "questions" / "assumptions.md", "Open")
    parts.append(f"\n{open_assumptions}\n" if _has_rows(open_assumptions)
                 else "\n_none open._\n")

    parts.append("\n## Prerequisites\n")
    open_prereqs = _section(c.root / ".control" / "questions" / "external.md", "Open")
    parts.append(f"\n{open_prereqs}\n" if _has_rows(open_prereqs) else "\n_none open._\n")

    return re.sub(r"\n{3,}", "\n\n", "\n".join(parts)) + "\n"


def page_prd(c: Corpus, slug: str) -> str:
    """This PRD's own sections verbatim, plus what only the brief, the registry, the glossary, and
    `.control/questions/` can complete. Nobody edits this by hand.
    """
    path = c.root / ".what" / "_prd" / slug / "prd.md"
    if not path.exists():
        return (f"# prd-{slug}\n\n" + PAGE_HEADER +
                f"\n\n_no `.what/_prd/{slug}/prd.md` yet._\n")
    text = _body(path)
    brief_path = c.root / ".what" / "_product-brief" / "brief.md"

    parts = [f"# {_doc_title(path, f'PRD — {slug}')}\n", PAGE_HEADER]

    parts.append("\n## Why\n")
    why_brief = _section(brief_path, "Why")
    why_delta = _section(path, "1. Why This Initiative") or _section(path, "Why This Initiative")
    if why_brief:
        parts.append(f"\n{why_brief}\n")
    if why_delta:
        parts.append(f"\n**This initiative:** {why_delta}\n")

    target_user = _section(path, "2. Target User") or _section(path, "Target User")
    if target_user:
        parts.append(f"\n## Target User\n\n{target_user}\n")

    # This initiative's OWN requirement file is the source, not a scan of the prose. That is the
    # whole point of the split: which PRD a promise belongs to is structural now, and a page that
    # guessed it from citations would still be guessing.
    own = c.requirements_of(slug)
    own_caps = _by_id(rows(own, "capabilities"))
    own_frs = _by_id(rows(own, "functional"))
    own_nfrs = _by_id(rows(own, "nonfunctional"))
    own_ujs = _by_id(rows(own, "journeys"))
    by_id = {str(r.get("id")): r for r in own_frs + own_nfrs}

    # § Features, with every `**Realizes:** FR-1, NFR-2` line expanded into the rows it names. That
    # rebuilds the shape the PRD used to write by hand — feature, then its requirements in full —
    # from the registry, so the reader never leaves this page for the text.
    features = _section(path, "3. Features") or _section(path, "Features")
    realized: set[str] = set()
    if features:
        out_lines: list[str] = []
        for line in features.splitlines():
            m = re.match(r"^\*\*Realizes:\*\*\s*(.*)$", line.strip())
            if not m:
                out_lines.append(line)
                continue
            ids = [i for i in re.findall(r"\b(?:FR|NFR)-\d+\b", m.group(1))]
            found = [by_id[i] for i in ids if i in by_id]
            missing = [i for i in ids if i not in by_id]
            if not found:
                out_lines.append(line)
                continue
            realized.update(str(r.get("id")) for r in found)
            out_lines.append("")
            for r in found:
                out_lines.append(_req_block(r, level=4))
            if missing:
                out_lines.append(f"_Also cited, not in `requirements-{slug}.yaml`: "
                                 + ", ".join(f"`{i}`" for i in missing) + "._\n")
        parts.append("\n## Features\n\n" + "\n".join(out_lines).rstrip() + "\n")

    if own_caps:
        parts.append("\n### Capabilities\n")
        parts.append("\n| id | Serves | Capability | Priority | Release | Depends on |"
                     "\n| --- | --- | --- | --- | --- | --- |")
        for cap in own_caps:
            deps = ", ".join(f"`{x}`" for x in listy(cap, "depends_on")) or "—"
            parts.append(f"| `{cap.get('id')}` | `{cap.get('goal', '—')}` "
                         f"| {_full(_text(cap))} | {cap.get('priority', '—')} "
                         f"| {cap.get('target_release', '—')} | {deps} |")
    if own_ujs:
        parts.append("\n\n### User journeys\n")
        parts.append("\n| id | Journey |\n| --- | --- |")
        for uj in own_ujs:
            parts.append(f"| `{uj.get('id')}` | {_full(_text(uj))} |")
    rest_frs = [r for r in own_frs if str(r.get("id")) not in realized]
    rest_nfrs = [r for r in own_nfrs if str(r.get("id")) not in realized]
    if rest_frs:
        note = " not attached to a feature above" if realized else ""
        parts.append(f"\n\n### Functional requirements{note}\n")
        for fr in rest_frs:
            parts.append("\n" + _req_block(fr))
    if rest_nfrs:
        note = " not attached to a feature above" if realized else ""
        parts.append(f"\n\n### Non-functional requirements{note}\n")
        for nfr in rest_nfrs:
            parts.append("\n" + _req_block(nfr))
    if not own and _cited_ids(text):
        parts.append(f"\n_`requirements-{slug}.yaml` does not exist yet — this initiative's `FR` "
                     f"and `NFR` have not been landed in a registry file of their own._\n")

    cited = _cited_ids(text)

    for heading, title in (("4. MVP Scope", "MVP Scope"), ("5. Success Metrics", "Success Metrics"),
                           ("6. Cross-Cutting NFRs", "Cross-Cutting NFRs"),
                           ("7. Constraints and Guardrails", "Constraints and Guardrails")):
        block = _section(path, heading)
        if block:
            parts.append(f"\n\n## {title}\n\n{block}\n")

    # The UX half G2 reads beside the PRD. An EXPERIENCE.md belongs to this initiative when it
    # references one of this initiative's UJ ids — the template requires it to reference them.
    uj_ids = [str(x.get("id")) for x in rows(own, "journeys") if x.get("id")]
    if uj_ids:
        for exp in sorted((c.root / ".what").glob("*/04-usecases/EXPERIENCE.md")):
            etext = _body(exp)
            if not any(re.search(rf"(?<![\w-]){re.escape(u)}(?![\w-])", etext) for u in uj_ids):
                continue
            pcname = exp.parent.parent.name
            parts.append(f"\n\n## Experience — `{pcname}`\n")
            for heading in ("Information architecture", "Journeys", "Behaviour per surface",
                            "Accessibility", "Edge cases"):
                block = _section(exp, heading)
                if block:
                    parts.append(f"\n### {heading}\n\n{block}\n")

    parts.append("\n\n## Non-Goals\n")
    scope_out = _subsection(brief_path, "Scope", "Scope Out")
    if scope_out:
        parts.append(f"\n**Product-wide, from the brief:**\n\n{scope_out}\n")
    else:
        parts.append("\n_none stated in the brief._\n")
    parts.append("\nRelease-specific exclusions are under **MVP Scope → Out of Scope for MVP** "
                 "above.\n")

    glossary = _glossary_terms_used(c.root, text)
    if glossary:
        parts.append(f"\n## Glossary\n\n{glossary}\n")

    needles = cited + [slug]
    q_dir = c.root / ".control" / "questions"
    open_q = "\n\n".join(
        filter(None, (_filtered_rows(_section(q_dir / f"{name}.md", "Open"), needles)
                      for name in ("blocking", "assumptions", "external"))))
    if open_q:
        parts.append(f"\n## Open Questions and Assumptions\n\n{open_q}\n")

    rh = _section(path, "Revision History")
    if rh:
        parts.append(f"\n\n## Revision History\n\n{rh}\n")

    return re.sub(r"\n{3,}", "\n\n", "\n".join(parts)) + "\n"


def page_srs(c: Corpus, pid: str) -> str:
    """One component's SRS, complete: its own kernel prose verbatim, the UC catalogue rendered from
    `usecases.yaml`, and every slot file inlined. For a reader who wants ONE component whole."""
    path = c.root / ".what" / pid / f"SRS-{pid}.md"
    pc = next((x for x in c.pcs if str(x.get("id")) == pid), {})
    parts = [f"# {_doc_title(path, f'SRS — {pid}')}\n", PAGE_HEADER]
    if not path.exists():
        return "\n".join(parts) + f"\n\n_no `.what/{pid}/SRS-{pid}.md` yet._\n"
    parts.append(f"\n`mode: {c.mode_of(pc)}` · `risk_accepted: {pc.get('risk_accepted', '—')}` — "
                 f"from `components.yaml`.\n")
    for heading in ("Decision Summary", "Why", "Actor Register"):
        block = _section(path, heading)
        if block:
            parts.append(f"\n## {heading}\n\n{block}\n")
    own_ucs = [uc for uc in c.ucs if str(uc.get("component") or "") == pid]
    parts.append(f"\n## UC Catalogue\n\nRendered from `usecases.yaml`.\n\n{_uc_table(own_ucs)}\n")
    for heading in ("Constraints", "Non-Goals", "Prerequisite", "Success Signal", "Design Reference"):
        block = _section(path, heading)
        if block:
            parts.append(f"\n## {heading}\n\n{block}\n")
    for slot, title in (("02-rules", "Business rules — local"), ("03-domain", "Domain"),
                        ("04-usecases", "Use cases"), ("05-scenarios", "Scenarios")):
        files = _slot_files(c.root, ".what", pid, slot)
        if files:
            parts.append(f"\n## {title} — `{slot}/`\n")
            for f in files:
                parts.append(_inline(f))
    return "\n".join(parts) + "\n"


def page_sdd(c: Corpus, pid: str) -> str:
    """The ONE page read at G4 for one component. Seven questions, and where each is answered:
    what is staked -> registry; boundaries with no failure answer -> § Failure Behaviour; what
    stops us tomorrow -> questions/; validators + review -> status; vendor lock -> § Decision
    Summary; DAG -> generated/dag; top risk -> risks.yaml. Only two of the seven need SDD prose.

    The AD-N table is rendered from the spine, not quoted. `AD-` is edited in place, so a quote
    goes stale the moment the spine changes and nothing sees it — the working SDD now cites ids.
    """
    path = c.root / ".how" / pid / f"SDD-{pid}.md"
    pc = next((x for x in c.pcs if str(x.get("id")) == pid), {})
    lcs = [lc for lc in c.lcs if str(lc.get("component") or "") == pid]
    lc_ids = {str(lc.get("id")) for lc in lcs}
    parts = [f"# {_doc_title(path, f'SDD — {pid}')}\n", PAGE_HEADER,
             "\nThis is what the owner reads at **G4 Component** for this component.\n"]
    parts.append(f"\n## What is staked\n\n`mode: {c.mode_of(pc)}` · "
                 f"`risk_accepted: {pc.get('risk_accepted', '—')}` · "
                 f"`g4_passed: {pc.get('g4_passed', '—')}`\n\n"
                 f"**risk_note:** {pc.get('risk_note') or '—'}\n\n"
                 f"**owns:** {', '.join(f'`{x}`' for x in listy(pc, 'owns')) or '—'} · "
                 f"**containers:** {', '.join(f'`{x}`' for x in listy(pc, 'containers')) or '—'}\n")
    if not path.exists():
        return "\n".join(parts) + f"\n\n_no `.how/{pid}/SDD-{pid}.md` yet._\n"
    ds = _section(path, "Decision Summary")
    parts.append(f"\n## Decision Summary\n\n{ds}\n" if ds else "\n## Decision Summary\n\n_not written yet._\n")
    parts.append(f"\n## Structure — Logical Components\n\nRendered from `components.yaml`.\n\n{_lc_table(lcs)}\n")
    st = _section(path, "Structure")
    if st:
        parts.append(f"\n### Dependency direction and responsibilities\n\n{_demote(st)}\n")
    parts.append("\n## Inherited Constraints — the spine's invariants\n\nRendered from "
                 "`ARCHITECTURE-SPINE.md`. A row marked **yes** binds this component by `Binds:`; the "
                 "rest are shown so a miss in `Binds:` is visible, not hidden.\n\n"
                 + _ad_table(_ad_blocks(c.root), pid, lc_ids) + "\n")
    for heading in ("Failure Behaviour", "Robustness Analysis", "Design Notes", "Evidence"):
        block = _section(path, heading)
        if block:
            parts.append(f"\n## {heading}\n\n{block}\n")
    for slot, title in (("01-ux", "UX — screens"), ("02-contracts", "Contracts"),
                        ("03-integrations", "Integrations"), ("04-components", "Components"),
                        ("05-model", "Data model"), ("06-flows", "Flows")):
        files = _slot_files(c.root, ".how", pid, slot)
        if files:
            parts.append(f"\n## {title} — `{slot}/`\n")
            for f in files:
                parts.append(_inline(f))
    return "\n".join(parts) + "\n"


def generate(c: Corpus, result: Result) -> list[Path]:
    """Machine tables into `.control/generated/`; every page a human reads into the two rendered
    trees, at the mirror path of the working document it projects."""
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

    # Two indexes that are tables for both readers, and stay beside the machine ones.
    for name, render in (("decisions", page_decisions), ("estimate", page_estimate)):
        page = out_dir / f"{name}.md"
        page.write_text(render(c), encoding="utf-8")
        written.append(page)

    # The pages a HUMAN reads: one per gate, at the mirror path of the working document.
    def emit(rel: Path, text: str) -> None:
        rel.parent.mkdir(parents=True, exist_ok=True)
        rel.write_text(text, encoding="utf-8")
        written.append(rel)

    what_r = c.root / RENDERED_WHAT
    how_r = c.root / RENDERED_HOW
    emit(what_r / "_product-brief" / "brief.md", page_brief(c))                      # G1
    for prd_path in sorted((c.root / ".what" / "_prd").glob("*/prd.md")):
        slug = prd_path.parent.name
        emit(what_r / "_prd" / slug / "prd.md", page_prd(c, slug))                   # G2
    emit(how_r / "blueprint.md", page_blueprint(c))                                  # G3
    for pc in c.pcs:
        pid = str(pc.get("id"))
        emit(what_r / pid / f"SRS-{pid}.md", page_srs(c, pid))
        if c.mode_of(pc) != "catalog":
            emit(how_r / pid / f"SDD-{pid}.md", page_sdd(c, pid))                    # G4

    # These used to be written here before the rendered trees existed. A stale copy left behind
    # would be the one home too many this whole design removes, so it is cleared, not kept.
    for stale in ["brief.md", "blueprint.md", *[p.name for p in out_dir.glob("prd-*.md")]]:
        (out_dir / stale).unlink(missing_ok=True)
    return written


# ------------------------------------------------------------------------ CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate", description="goal-has-fr..id-allocated-once and the .control/generated/ generator")
    parser.add_argument("--check", action="store_true",
                        help="check only; exit non-zero if anything is red")
    parser.add_argument("--generate", action="store_true",
                        help="rewrite .control/generated/ (still runs the check first)")
    parser.add_argument("--root", default=".", help="repo root (default: current directory)")
    parser.add_argument("--asof", default=None,
                        help="reference date for plan-dates, format YYYY-MM-DD (default: today). "
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
            print(f"  {finding.vid:<26} {finding.subject}: {finding.message}")
    else:
        print("\nGREEN — no findings")

    if result.skipped:
        print("\nSkipped:")
        for vid, why in sorted(result.skipped.items()):
            print(f"  {vid:<26} {why}")

    print(f"\nV14 reference date: {asof.isoformat()}")
    return 1 if result.findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

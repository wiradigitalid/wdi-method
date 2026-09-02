#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""timeline — the time dimension: generated/timeline, generated/report, .control/reports/<period>.md.

The corpus can state what is true. It cannot state WHEN that became true, because not one
delivery date is stored — and indeed MUST NOT be stored. This script supplies that missing
dimension by reading git.

    timeline.py --generate              write .control/generated/timeline.* and report.*
    timeline.py --publish weekly        freeze .control/reports/2026-W34.md
    timeline.py --publish monthly       freeze .control/reports/2026-08.md
    timeline.py --refresh --generate    run validate --generate first

The division of labor stays as in 08-project-management.md: whatever can be computed from the
registry alone belongs to validate.py; only what needs git stays here. That is why Corpus, dump,
and friends are imported, not copied — one fact MUST NOT have two homes.

A delivery date MUST NOT be written back to any registry. It is re-derived on every run; a stored
copy is a copy that will go stale.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import yaml

from validate import (FM, Corpus, _ticket_files, _ticket_status, cap_tickets, dump, git,
                      listy, load_yaml, status_in)

# Statuses that do not yet mean "in progress". A ticket still in this set has no
# actual_start, no matter how old the file is. `ready-for-agent` is the engine's own opening
# state — a ticket published and not yet picked up — so it belongs here too.
NOT_STARTED = {"", "unknown", "draft", "backlog", "todo", "planned", "ready-for-agent"}

TIMELINE_COLUMNS = [
    "id", "text", "size", "priority", "owner", "target_release",
    "planned_start", "planned_end", "estimate_mandays",
    "actual_start", "actual_end", "delta_days", "state",
]


# ------------------------------------------------------------------ git history


_HIST: dict[tuple[str, str], list[tuple[str, str, str]]] = {}


def history(root: Path, rel: str) -> list[tuple[str, str, str]]:
    """[(sha, date, content)] in chronological order for one file. Empty if never committed."""
    key = (str(root), rel)
    if key in _HIST:
        return _HIST[key]
    out = git(root, "log", "--reverse", "--format=%H|%ad", "--date=short", "--", rel)
    revs: list[tuple[str, str, str]] = []
    for line in (out or "").splitlines():
        sha, _, date = line.partition("|")
        if not sha or not date:
            continue
        text = git(root, "show", f"{sha}:./{rel}")
        if text is not None:
            revs.append((sha, date, text))
    _HIST[key] = revs
    return revs


def fm_of(text: str) -> dict:
    match = FM.match(text)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else {}


def yaml_of(text: str) -> dict:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


# ------------------------------------------------------------- time derivation


def ticket_path(c: Corpus, spec: dict, ticket: dict) -> str | None:
    matches = _ticket_files(c, spec, ticket)
    return matches[0].relative_to(c.root).as_posix() if matches else None


def ticket_span(c: Corpus, spec: dict, ticket: dict) -> dict:
    """When a ticket started being worked on and when it went `done`, read from its file history.

    A file that exists on disk but has never been committed is marked `uncommitted` instead
    of being given a made-up date. A finished ticket that has not been committed is a state that
    MUST be visible, not one that gets patched over.
    """
    rel = ticket_path(c, spec, ticket)
    if rel is None:
        return {"start": None, "end": None, "uncommitted": False, "path": None}
    revs = history(c.root, rel)
    if not revs:
        return {"start": None, "end": None, "uncommitted": True, "path": rel}
    start = end = None
    for _sha, date, text in revs:
        status = status_in(text).lower()
        if start is None and status not in NOT_STARTED:
            start = date
        if status == "done":
            end = date
            break
    return {"start": start, "end": end, "uncommitted": False, "path": rel}


def fr_tickets(c: Corpus) -> dict[str, list[dict]]:
    """FR -> ticket, through its UCs. cap_tickets()'s twin, one level down."""
    ucs_of: dict[str, list[str]] = {}
    for uc in c.ucs:
        for fid in listy(uc, "satisfies"):
            ucs_of.setdefault(fid, []).append(str(uc.get("id")))
    all_tickets = [t for _, t in c.tickets()]
    out: dict[str, list[dict]] = {}
    for fr in c.frs:
        fid = str(fr.get("id"))
        wanted = set(ucs_of.get(fid, []))
        out[fid] = [t for t in all_tickets if wanted & set(listy(t, "satisfies"))]
    return out


def span_of(c: Corpus, items: list[dict], spans: dict[str, dict]) -> tuple[str | None, str | None, bool]:
    """(earliest start, latest end, closed). Closed only when ALL are finished."""
    if not items:
        return None, None, False
    starts = [spans[str(t.get("id"))]["start"] for t in items]
    ends = [spans[str(t.get("id"))]["end"] for t in items]
    closed = all(e for e in ends)
    return (min([x for x in starts if x], default=None),
            max([x for x in ends if x], default=None) if closed else None,
            closed)


def days_between(a: str | None, b: str | None) -> int | None:
    if not a or not b:
        return None
    try:
        return (dt.date.fromisoformat(a) - dt.date.fromisoformat(b)).days
    except ValueError:
        return None


def state_of(planned_end: str, actual_start: str | None, closed: bool, asof: dt.date) -> str:
    if closed:
        return "done"
    if planned_end:
        try:
            if dt.date.fromisoformat(planned_end) < asof:
                return "overdue"
        except ValueError:
            pass
    return "in-progress" if actual_start else "not-started"


# ---------------------------------------------------------------- generated/timeline


def gen_timeline(c: Corpus, asof: dt.date) -> dict:
    spans = {str(t.get("id")): ticket_span(c, sp, t) for sp, t in c.tickets()}
    spec_of = {str(t.get("id")): sp for sp, t in c.tickets()}
    by_cap = cap_tickets(c)
    by_fr = fr_tickets(c)
    fr_of_cap: dict[str, list[dict]] = {}
    for fr in c.frs:
        fr_of_cap.setdefault(str(fr.get("capability", "")), []).append(fr)

    out = []
    for cap in c.caps:
        cid = str(cap.get("id"))
        items = by_cap.get(cid, [])
        start, end, closed = span_of(c, items, spans)
        planned_end = str(cap.get("planned_end") or "")
        row = {
            "id": cid,
            "text": str(cap.get("text") or ""),
            "size": str(cap.get("size") or ""),
            "priority": str(cap.get("priority") or ""),
            "owner": str(cap.get("owner") or ""),
            "target_release": str(cap.get("target_release") or ""),
            "planned_start": str(cap.get("planned_start") or ""),
            "planned_end": planned_end,
            "estimate_mandays": cap.get("estimate_mandays", 0),
            "actual_start": start or "",
            "actual_end": end or "",
            "delta_days": days_between(end, planned_end),
            "state": state_of(planned_end, start, closed, asof),
        }
        children = []
        for fr in sorted(fr_of_cap.get(cid, []), key=lambda x: str(x.get("id"))):
            fid = str(fr.get("id"))
            f_items = by_fr.get(fid, [])
            f_start, f_end, f_closed = span_of(c, f_items, spans)
            children.append({
                "id": fid,
                "text": str(fr.get("text") or ""),
                "tickets": sorted(str(t.get("id")) for t in f_items),
                "actual_start": f_start or "",
                "actual_end": f_end or "",
                "state": state_of("", f_start, f_closed, asof),
            })
        row["children"] = children
        row["waiting_on"] = sorted(
            str(t.get("id")) for t in items
            if _ticket_status(c, spec_of.get(str(t.get("id")), {}), t) != "done"
        ) if not closed else []
        out.append(row)

    stray = sorted(sid for sid, span in spans.items() if span["uncommitted"])
    return {"asof": asof.isoformat(), "capabilities": out, "uncommitted_tickets": stray}


# ------------------------------------------------------------------ generated/report


def last_report(c: Corpus, asof: dt.date) -> tuple[str | None, str | None]:
    """(reference date of the last report, its name). Both None if no report exists yet."""
    best: tuple[str, str] | None = None
    for path in sorted((c.root / ".control/reports").glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = fm_of(text)
        stamp = str(fm.get("asof") or "")
        if not stamp or stamp >= asof.isoformat():
            continue
        if best is None or stamp > best[0]:
            best = (stamp, path.stem)
    return best if best else (None, None)


def in_period(date: str | None, since: str | None, asof: dt.date) -> bool:
    if not date:
        return False
    if date > asof.isoformat():
        return False
    return True if since is None else date > since


def first_seen(c: Corpus, rel: str, key: str, pick) -> dict[str, str]:
    """id -> date when `pick` first became true in a registry's history."""
    seen: dict[str, str] = {}
    for _sha, date, text in history(c.root, rel):
        data = yaml_of(text)
        for item in data.get(key) or []:
            ident = pick(item)
            if ident:
                seen.setdefault(str(ident), date)
    return seen


def gen_report(c: Corpus, timeline: dict, asof: dt.date) -> dict:
    since, since_name = last_report(c, asof)
    rtm = (load_yaml(c.root / ".control/generated/rtm.yaml").get("rtm") or [])
    status = load_yaml(c.root / ".control/generated/status.yaml")
    spans = {str(t.get("id")): ticket_span(c, sp, t) for sp, t in c.tickets()}

    proven = []
    for row in rtm:
        sid = str(row.get("ticket") or "")
        end = spans.get(sid, {}).get("end")
        if row.get("green") and in_period(end, since, asof):
            proven.append({"FR": row.get("FR"), "UC": row.get("UC"), "ticket": sid,
                           "test": row.get("test"), "closed": end})
    proven.sort(key=lambda x: (str(x["closed"]), str(x["ticket"])))

    moved = []
    for row in timeline["capabilities"]:
        for field, event in (("actual_start", "started"), ("actual_end", "closed")):
            when = row.get(field) or None
            if in_period(when, since, asof):
                moved.append({"id": row["id"], "kind": "CAP", "event": event, "date": when})
        for child in row["children"]:
            for field, event in (("actual_start", "started"), ("actual_end", "closed")):
                when = child.get(field) or None
                if in_period(when, since, asof):
                    moved.append({"id": child["id"], "kind": "FR", "event": event, "date": when})
    moved.sort(key=lambda x: (x["date"], x["id"], x["event"]))

    late = []
    for row in timeline["capabilities"]:
        if row["state"] != "overdue":
            continue
        overdue_by = days_between(asof.isoformat(), row["planned_end"])
        late.append({"id": row["id"], "text": row["text"], "owner": row["owner"],
                     "planned_end": row["planned_end"], "days_late": overdue_by,
                     "waiting_on": row["waiting_on"] or ["no ticket yet"]})
    late.sort(key=lambda x: (-(x["days_late"] or 0), x["id"]))

    closures = first_seen(c, ".control/registry/defects.yaml", "defects",
                          lambda d: d.get("id") if str(d.get("status")) == "fixed" else None)
    opened, closed_rows = [], []
    for defect in c.defect_list:
        did = str(defect.get("id"))
        entry = {"id": did, "title": str(defect.get("title") or ""),
                 "root_cause": str(defect.get("root_cause") or ""),
                 "violates": listy(defect, "violates")}
        if in_period(str(defect.get("reported") or ""), since, asof):
            opened.append(entry)
        when = closures.get(did)
        if in_period(when, since, asof):
            closed_rows.append({**entry, "closed": when})

    by_cause: dict[str, list[str]] = {}
    for row in closed_rows:
        by_cause.setdefault(row["root_cause"] or "?", []).append(row["id"])

    # An empty `root_cause` is a valid state — the row was opened by someone who has not yet
    # diagnosed it, and `defect-root-cause` does skip it. What MUST NOT happen is it aging unseen, so it is
    # surfaced in the report instead of being held by a validator. The whole period, not just this one.
    undiagnosed = sorted(
        ({"id": str(d.get("id")), "title": str(d.get("title") or ""),
          "reported": str(d.get("reported") or ""),
          "age_days": days_between(asof.isoformat(), str(d.get("reported") or ""))}
         for d in c.defect_list
         if not str(d.get("root_cause") or "").strip() and str(d.get("status")) != "fixed"),
        key=lambda x: (-(x["age_days"] or 0), x["id"]))

    gates = [{"gate": gid, "date": when} for gid, when in sorted(
        first_seen(c, ".control/registry/index.yaml", "gates_passed", lambda g: g).items())
        if in_period(when, since, asof)]

    head = git(c.root, "rev-parse", "HEAD") or ""
    dirty = bool(git(c.root, "status", "--porcelain", "--", ".control/registry"))

    return {
        "asof": asof.isoformat(),
        "since": since or "",
        "since_report": since_name or "",
        "sha": head,
        "registry_dirty": dirty,
        # A done ticket that has not been committed still counts in the RTM — its status is read
        # from the working tree — but it will never appear under "Proven", which needs a date from
        # git. That gap MUST be visible in the report, not only in the timeline.
        "uncommitted_tickets": timeline["uncommitted_tickets"],
        "promise_progress": status.get("promise_progress", "n/a"),
        "rtm_rows": status.get("rtm_rows", {}),
        "work_progress": status.get("work_progress", []),
        "gate_readiness": status.get("gate_readiness", "n/a"),
        "proven": proven,
        "moved": moved,
        "late": late,
        "defects": {"opened": sorted(opened, key=lambda x: x["id"]),
                    "closed": sorted(closed_rows, key=lambda x: x["id"]),
                    "closed_by_root_cause": {k: sorted(v) for k, v in sorted(by_cause.items())},
                    "undiagnosed": undiagnosed},
        "gates": gates,
    }


# -------------------------------------------------------------------- rendering


def cell(value: object) -> str:
    text = ", ".join(str(v) for v in value) if isinstance(value, list) else str(value or "")
    return text.replace("|", "\\|").replace("\n", " ").strip() or "—"


def table(headers: list[str], lines: list[list[object]]) -> str:
    if not lines:
        return "_None._\n"
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(cell(v) for v in line) + " |" for line in lines]
    return "\n".join(out) + "\n"


def safe(text: str, width: int = 44) -> str:
    """Text safe to put into mermaid: without the `:` and `,` that break its syntax."""
    clean = str(text or "").replace(":", " ").replace(",", " ").replace("#", "").strip()
    return (clean[:width].rstrip() + "…") if len(clean) > width else (clean or "untitled")


def gantt(timeline: dict) -> str:
    """Mermaid Gantt: planned and actual side by side, so the gap is visible."""
    lines = ["```mermaid", "gantt", "    dateFormat YYYY-MM-DD", "    axisFormat %d %b",
             "    title Planned vs actual per CAP", ""]
    by_release: dict[str, list[dict]] = {}
    for row in timeline["capabilities"]:
        by_release.setdefault(row["target_release"] or "no release", []).append(row)
    drawn = 0
    for release in sorted(by_release):
        rows_ = by_release[release]
        drawable = [r for r in rows_ if (r["planned_start"] and r["planned_end"])
                    or (r["actual_start"] and r["actual_end"])]
        if not drawable:
            continue
        lines.append(f"    section {safe(release, 24)}")
        for row in drawable:
            slug = row["id"].replace("-", "").lower()
            label = f"{row['id']} {safe(row['text'])}"
            if row["planned_start"] and row["planned_end"]:
                mark = "crit, " if row["state"] == "overdue" else ""
                lines.append(f"    {label} planned :{mark}{slug}p, "
                             f"{row['planned_start']}, {row['planned_end']}")
            if row["actual_start"]:
                end = row["actual_end"] or timeline["asof"]
                mark = "done, " if row["state"] == "done" else "active, "
                lines.append(f"    {label} actual :{mark}{slug}a, {row['actual_start']}, {end}")
            drawn += 1
        lines.append("")
    lines.append("```")
    if drawn == 0:
        return ("_No CAP has a planned or actual date yet — "
                "the gantt is not drawn._\n")
    return "\n".join(lines) + "\n"


HEADER = ("> Generated by `.constitution/method/scripts/timeline.py --generate`. "
          "MUST NOT be hand-edited.\n")


def with_header(rendered: str) -> str:
    """Insert the warning right below the title — not above it, so the title stays H1."""
    title, _, body = rendered.partition("\n")
    return f"{title}\n\n{HEADER}{body}"


def render_timeline(timeline: dict) -> str:
    out = ["# Timeline\n", f"\nAs of: **{timeline['asof']}**\n\n"]
    out.append(gantt(timeline))
    out.append("\n## Per CAP\n\n")
    out.append(table(
        ["CAP", "Title", "Release", "Size", "Priority", "Owner",
         "Planned", "Actual", "Δ days", "State"],
        [[r["id"], r["text"], r["target_release"], r["size"], r["priority"], r["owner"],
          f"{r['planned_start'] or '—'} → {r['planned_end'] or '—'}",
          f"{r['actual_start'] or '—'} → {r['actual_end'] or '—'}",
          "—" if r["delta_days"] is None else f"{r['delta_days']:+d}",
          r["state"]] for r in timeline["capabilities"]]))

    children = [[r["id"], ch["id"], ch["text"], ch["tickets"],
                 f"{ch['actual_start'] or '—'} → {ch['actual_end'] or '—'}", ch["state"]]
                for r in timeline["capabilities"] if r["size"] == "L" for ch in r["children"]]
    if children:
        out.append("\n## FR detail for CAPs sized L\n\n")
        out.append("A CAP sized `L` is drawn as one summary bar; this is what is inside it.\n\n")
        out.append(table(["CAP", "FR", "Title", "Ticket", "Actual", "State"], children))

    if timeline["uncommitted_tickets"]:
        out.append("\n## Tickets with no git history\n\n")
        out.append("The file exists on disk but has never been committed, so its date "
                   "MUST NOT be derived. Commit it first, then run again.\n\n")
        out.append("".join(f"- `{sid}`\n" for sid in timeline["uncommitted_tickets"]))
    return "".join(out)


def render_report(report: dict, title: str = "Report") -> str:
    since = report["since"] or "the project's start"
    edge = ("This period has no left bound — there is no earlier report yet."
            if not report["since"] else
            f"Since `{report['since_report']}` ({report['since']}).")
    out = [f"# {title}\n\n"]
    out.append(f"Period: **{since} → {report['asof']}**. {edge}\n\n")
    out.append(f"Freshness: commit `{(report['sha'] or '?')[:12]}`.")
    if report["registry_dirty"]:
        out.append(" **The registry has uncommitted changes — the numbers below "
                   "may not reflect what is on `main`.**")
    out.append("\n\n")
    if report["uncommitted_tickets"]:
        out.append("> **Warning.** The following tickets have a status read from the working "
                   "tree but have never been committed: "
                   + ", ".join(f"`{s}`" for s in report["uncommitted_tickets"])
                   + ". They still count toward promise progress, but MUST NOT appear in the "
                     "Proven section — there, the date must come from git. Commit them first, "
                     "then run again.\n\n")

    out.append(f"## Promise progress — {report['promise_progress']}\n\n")
    counts = report["rtm_rows"] or {}
    out.append(f"This is the number that counts: green RTM rows divided by counted rows "
               f"({counts.get('green', 0)} out of {counts.get('counted', 0)}; "
               f"{counts.get('excluded_no_uc', 0)} excluded for having `no_uc`). "
               f"It measures what is **proven**, not what has been worked on.\n\n")
    out.append(table(["Other measure", "Value", "Answers"], [
        ["Work progress", ", ".join(f"{w.get('spec')} {w.get('work_progress')}"
                                    for w in report["work_progress"]) or "n/a",
         "how much has been worked on"],
        ["Gate readiness", report["gate_readiness"], "whether the next gate can open"],
    ]))

    out.append("\n## 1. Proven\n\n")
    out.append("RTM rows that turned green within this period.\n\n")
    out.append(table(["FR", "UC", "Ticket", "Test", "Date"],
                     [[p["FR"], p["UC"], p["ticket"], p["test"], p["closed"]]
                      for p in report["proven"]]))

    out.append("\n## 2. Moved\n\n")
    out.append(table(["ID", "Layer", "Event", "Date"],
                     [[m["id"], m["kind"], m["event"], m["date"]] for m in report["moved"]]))

    out.append("\n## 3. Late\n\n")
    if report["late"]:
        out.append("Named one by one. Summarizing it into a count is how a plan that missed "
                   "keeps feeling comfortable.\n\n")
    out.append(table(["CAP", "Title", "Owner", "Planned end", "Late (days)", "Waiting on"],
                     [[l["id"], l["text"], l["owner"], l["planned_end"],
                       l["days_late"], l["waiting_on"]] for l in report["late"]]))

    out.append("\n## 4. Defects\n\n")
    defects = report["defects"]
    out.append("**Opened**\n\n")
    out.append(table(["ID", "Title", "Root cause", "Violates"],
                     [[d["id"], d["title"], d["root_cause"], d["violates"]]
                      for d in defects["opened"]]))
    out.append("\n**Closed, grouped by root cause**\n\n")
    out.append(table(["Root cause", "Defects", "Count"],
                     [[cause, ids, len(ids)]
                      for cause, ids in defects["closed_by_root_cause"].items()]))
    if defects["closed_by_root_cause"]:
        out.append("\nThe `requirement` and `architecture` rows are worth reading twice: "
                   "both count defects that turned out not to be bad code.\n")
    if defects["undiagnosed"]:
        out.append("\n**Not yet diagnosed** — open with no `root_cause`, the whole period\n\n")
        out.append(table(["ID", "Title", "Reported", "Age (days)"],
                         [[d["id"], d["title"], d["reported"], d["age_days"]]
                          for d in defects["undiagnosed"]]))
        out.append("\nA row with no `root_cause` violates nothing — it means no one has run "
                   "`wdi-systematic-debugging` on it yet. While that holds it also does not "
                   "count toward the ratio above, so that ratio applies only to defects that "
                   "have already been diagnosed.\n")

    out.append("\n## 5. Gates\n\n")
    out.append(table(["Gate", "Date"], [[g["gate"], g["date"]] for g in report["gates"]]))
    return "".join(out)


# ---------------------------------------------------------------------- publish


def period_name(kind: str, asof: dt.date) -> str:
    if kind == "weekly":
        return asof.strftime("%G-W%V")
    if kind == "monthly":
        return asof.strftime("%Y-%m")
    return kind


NOTE = """
## Notes

<!-- Written by a human once, at publish time. MUST cite the cause (ADR, OQ-, risk, or
     defect), not retell it — a second telling will drift from the first.
     Leave empty if there is truly nothing to add. -->
"""


def publish(c: Corpus, report: dict, kind: str, asof: dt.date) -> tuple[Path, str | None]:
    name = period_name(kind, asof)
    path = c.root / ".control" / "reports" / f"{name}.md"
    if path.exists():
        return path, (f"{path.name} has already been published. A published report is FROZEN — "
                      f"if it turns out to be wrong, the next report is what corrects it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    front = dump({
        "period": name,
        "asof": report["asof"],
        "since": report["since"],
        "sha": report["sha"],
        "promise_progress": report["promise_progress"],
        "generated_by": ".constitution/method/scripts/timeline.py",
    })
    path.write_text(f"---\n{front}---\n\n{render_report(report, f'Report {name}')}{NOTE}",
                    encoding="utf-8")
    return path, None


# -------------------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="timeline", description="the time dimension from git: timeline, report, period report")
    parser.add_argument("--generate", action="store_true",
                        help="write .control/generated/timeline.* and report.*")
    parser.add_argument("--publish", metavar="PERIOD",
                        help="freeze .control/reports/<period>.md — weekly | monthly | <name>")
    parser.add_argument("--refresh", action="store_true",
                        help="run validate --generate first so the tables are fresh")
    parser.add_argument("--root", default=".", help="repo root (default: current directory)")
    parser.add_argument("--asof", default=None,
                        help="reference date, YYYY-MM-DD (default: today)")
    args = parser.parse_args(argv)

    if not args.generate and not args.publish:
        args.generate = True

    root = Path(args.root).resolve()
    if not (root / ".control" / "registry").is_dir():
        print(f"timeline: {root} has no .control/registry/ — wrong repo root?", file=sys.stderr)
        return 2

    asof = dt.date.fromisoformat(args.asof) if args.asof else dt.date.today()
    corpus = Corpus.load(root)

    if git(root, "rev-parse", "HEAD") is None:
        print("timeline: git did not respond at this root. Every delivery date is derived "
              "from git, so with no git there is nothing that can be reported — and making "
              "one up MUST NOT be done.", file=sys.stderr)
        return 3

    if args.refresh:
        import validate
        result = validate.run_checks(corpus, asof)
        validate.generate(corpus, result)
        print(f"  refreshed .control/generated/ — {len(result.findings)} validator findings")

    generated = root / ".control" / "generated"
    missing = [n for n in ("rtm", "status") if not (generated / f"{n}.yaml").exists()]
    if missing:
        print(f"timeline: {', '.join(missing)} does not exist yet in .control/generated/. A "
              f"report on top of a stale table is worse than no report — run "
              f"`validate.py --generate`, or repeat with `--refresh`.", file=sys.stderr)
        return 3

    timeline = gen_timeline(corpus, asof)
    report = gen_report(corpus, timeline, asof)

    if args.generate:
        generated.mkdir(parents=True, exist_ok=True)
        for name, payload, rendered in (
            ("timeline", timeline, render_timeline(timeline)),
            ("report", report, render_report(report)),
        ):
            (generated / f"{name}.yaml").write_text(dump(payload), encoding="utf-8")
            (generated / f"{name}.md").write_text(with_header(rendered), encoding="utf-8")
            print(f"  wrote .control/generated/{name}.yaml")
            print(f"  wrote .control/generated/{name}.md")

    if args.publish:
        path, refusal = publish(corpus, report, args.publish, asof)
        if refusal:
            print(f"\ntimeline: {refusal}", file=sys.stderr)
            return 4
        print(f"  published {path.relative_to(root).as_posix()}")

    overdue = [r for r in timeline["capabilities"] if r["state"] == "overdue"]
    print(f"\npromise progress: {report['promise_progress']}"
          f"   ·   CAP overdue: {len(overdue)}"
          f"   ·   as of: {asof.isoformat()}")
    for row in overdue:
        print(f"  LATE  {row['id']} — planned end {row['planned_end']}, "
              f"waiting on {', '.join(row['waiting_on']) or 'no ticket yet'}")
    if report["registry_dirty"]:
        print("\nthe registry has uncommitted changes — the numbers above may not "
              "reflect what is on main")
    if timeline["uncommitted_tickets"]:
        print(f"tickets with no git history: {', '.join(timeline['uncommitted_tickets'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

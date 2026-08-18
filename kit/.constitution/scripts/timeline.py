#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""timeline — dimensi waktu: generated/timeline, generated/report, .control/reports/<periode>.md.

Korpus bisa menyatakan apa yang benar. Ia tidak bisa menyatakan KAPAN itu jadi benar, karena
tidak ada satu pun tanggal realisasi yang disimpan — dan memang MUST NOT disimpan. Skrip ini
memasok dimensi yang hilang itu dengan membaca git.

    timeline.py --generate              tulis .control/generated/timeline.* dan report.*
    timeline.py --publish weekly        bekukan .control/reports/2026-W34.md
    timeline.py --publish monthly       bekukan .control/reports/2026-08.md
    timeline.py --refresh --generate    jalankan validate --generate lebih dulu

Pembagian kerjanya tetap seperti di 08-project-management.md: yang bisa dihitung dari registry
saja milik validate.py; hanya yang butuh git yang tinggal di sini. Karena itu Corpus, dump, dan
kawan-kawannya diimpor, bukan disalin — satu fakta MUST NOT punya dua rumah.

Tanggal realisasi MUST NOT ditulis balik ke registry mana pun. Ia diturunkan tiap run; salinan
yang disimpan adalah salinan yang akan salah.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import yaml

from validate import (FM, Corpus, _story_status, cap_stories, dump, git,
                      listy, load_yaml)

# Status frontmatter yang belum berarti "dikerjakan". Story yang masih di sini belum punya
# actual_start, betapapun tuanya berkasnya.
BELUM_MULAI = {"", "draft", "backlog", "todo", "planned"}

TIMELINE_COLUMNS = [
    "id", "text", "size", "priority", "owner", "target_release",
    "planned_start", "planned_end", "estimate_mandays",
    "actual_start", "actual_end", "delta_days", "state",
]


# ------------------------------------------------------------------ riwayat git


_HIST: dict[tuple[str, str], list[tuple[str, str, str]]] = {}


def history(root: Path, rel: str) -> list[tuple[str, str, str]]:
    """[(sha, tanggal, isi)] kronologis untuk satu berkas. Kosong bila belum pernah dicommit."""
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


# ------------------------------------------------------------- penurunan waktu


def story_path(c: Corpus, story: dict) -> str | None:
    folder = str(story.get("spec_folder") or "").strip()
    if not folder:
        return None
    matches = sorted((c.root / folder / "stories").glob(f"{story.get('id')}-*.md"))
    if not matches:
        return None
    return matches[0].relative_to(c.root).as_posix()


def story_span(c: Corpus, story: dict) -> dict:
    """Kapan story mulai dikerjakan dan kapan ia `done`, dibaca dari riwayat berkasnya.

    Berkas yang ada di disk tetapi belum pernah dicommit ditandai `uncommitted` alih-alih
    diberi tanggal karangan. Story selesai yang belum dicommit adalah keadaan yang MUST
    terlihat, bukan yang ditambal.
    """
    rel = story_path(c, story)
    if rel is None:
        return {"start": None, "end": None, "uncommitted": False, "path": None}
    revs = history(c.root, rel)
    if not revs:
        return {"start": None, "end": None, "uncommitted": True, "path": rel}
    start = end = None
    for _sha, date, text in revs:
        status = str(fm_of(text).get("status") or "").strip().lower()
        if start is None and status not in BELUM_MULAI:
            start = date
        if status == "done":
            end = date
            break
    return {"start": start, "end": end, "uncommitted": False, "path": rel}


def fr_stories(c: Corpus) -> dict[str, list[dict]]:
    """FR -> story, lewat UC-nya. Kembaran cap_stories() satu tingkat di bawahnya."""
    ucs_of: dict[str, list[str]] = {}
    for uc in c.ucs:
        for fid in listy(uc, "satisfies"):
            ucs_of.setdefault(fid, []).append(str(uc.get("id")))
    all_stories = [s for _, _, s in c.stories()]
    out: dict[str, list[dict]] = {}
    for fr in c.frs:
        fid = str(fr.get("id"))
        wanted = set(ucs_of.get(fid, []))
        out[fid] = [s for s in all_stories if wanted & set(listy(s, "satisfies"))]
    return out


def span_of(c: Corpus, items: list[dict], spans: dict[str, dict]) -> tuple[str | None, str | None, bool]:
    """(mulai paling awal, selesai paling akhir, tertutup). Tertutup hanya bila SEMUA selesai."""
    if not items:
        return None, None, False
    starts = [spans[str(s.get("id"))]["start"] for s in items]
    ends = [spans[str(s.get("id"))]["end"] for s in items]
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
    spans = {str(s.get("id")): story_span(c, s) for _, _, s in c.stories()}
    by_cap = cap_stories(c)
    by_fr = fr_stories(c)
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
                "stories": sorted(str(s.get("id")) for s in f_items),
                "actual_start": f_start or "",
                "actual_end": f_end or "",
                "state": state_of("", f_start, f_closed, asof),
            })
        row["children"] = children
        row["waiting_on"] = sorted(
            str(s.get("id")) for s in items if _story_status(c, s) != "done"
        ) if not closed else []
        out.append(row)

    stray = sorted(sid for sid, span in spans.items() if span["uncommitted"])
    return {"asof": asof.isoformat(), "capabilities": out, "uncommitted_stories": stray}


# ------------------------------------------------------------------ generated/report


def last_report(c: Corpus, asof: dt.date) -> tuple[str | None, str | None]:
    """(tanggal acuan laporan terakhir, namanya). Keduanya None bila belum ada laporan."""
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
    """id -> tanggal saat `pick` pertama kali benar di riwayat sebuah registry."""
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
    spans = {str(s.get("id")): story_span(c, s) for _, _, s in c.stories()}

    proven = []
    for row in rtm:
        sid = str(row.get("story") or "")
        end = spans.get(sid, {}).get("end")
        if row.get("green") and in_period(end, since, asof):
            proven.append({"FR": row.get("FR"), "UC": row.get("UC"), "story": sid,
                           "test": row.get("test"), "closed": end})
    proven.sort(key=lambda x: (str(x["closed"]), str(x["story"])))

    moved = []
    for row in timeline["capabilities"]:
        for field, event in (("actual_start", "mulai"), ("actual_end", "tertutup")):
            when = row.get(field) or None
            if in_period(when, since, asof):
                moved.append({"id": row["id"], "kind": "CAP", "event": event, "date": when})
        for child in row["children"]:
            for field, event in (("actual_start", "mulai"), ("actual_end", "tertutup")):
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
                     "waiting_on": row["waiting_on"] or ["belum ada story"]})
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

    # `root_cause` kosong adalah keadaan sah — baris itu dibuka orang yang belum mendiagnosisnya,
    # dan V20 memang melewatinya. Yang MUST NOT terjadi adalah ia menua tanpa terlihat, jadi ia
    # disorot di laporan alih-alih ditahan validator. Seluruh periode, bukan cuma yang ini.
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
        # Story done yang belum dicommit tetap dihitung RTM — statusnya dibaca dari working tree —
        # tetapi tidak akan pernah muncul di "Terbukti", yang butuh tanggal dari git. Selisih itu
        # MUST terlihat di laporan, bukan cuma di timeline.
        "uncommitted_stories": timeline["uncommitted_stories"],
        "progres_janji": status.get("progres_janji", "n/a"),
        "baris_rtm": status.get("baris_rtm", {}),
        "progres_kerja": status.get("progres_kerja", []),
        "kesiapan_gate": status.get("kesiapan_gate", "n/a"),
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
        return "_Tidak ada._\n"
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(cell(v) for v in line) + " |" for line in lines]
    return "\n".join(out) + "\n"


def safe(text: str, width: int = 44) -> str:
    """Teks yang aman masuk mermaid: tanpa `:` dan `,` yang memotong sintaksnya."""
    clean = str(text or "").replace(":", " ").replace(",", " ").replace("#", "").strip()
    return (clean[:width].rstrip() + "…") if len(clean) > width else (clean or "tanpa judul")


def gantt(timeline: dict) -> str:
    """Gantt mermaid: rencana dan realisasi berdampingan, supaya selisihnya terlihat."""
    lines = ["```mermaid", "gantt", "    dateFormat YYYY-MM-DD", "    axisFormat %d %b",
             "    title Rencana vs realisasi per CAP", ""]
    by_release: dict[str, list[dict]] = {}
    for row in timeline["capabilities"]:
        by_release.setdefault(row["target_release"] or "tanpa rilis", []).append(row)
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
                lines.append(f"    {label} rencana :{mark}{slug}p, "
                             f"{row['planned_start']}, {row['planned_end']}")
            if row["actual_start"]:
                end = row["actual_end"] or timeline["asof"]
                mark = "done, " if row["state"] == "done" else "active, "
                lines.append(f"    {label} realisasi :{mark}{slug}a, {row['actual_start']}, {end}")
            drawn += 1
        lines.append("")
    lines.append("```")
    if drawn == 0:
        return ("_Belum ada CAP yang punya tanggal rencana maupun realisasi — "
                "gantt tidak digambar._\n")
    return "\n".join(lines) + "\n"


HEADER = ("> Tergenerate oleh `.constitution/scripts/timeline.py --generate`. "
          "MUST NOT diedit tangan.\n")


def with_header(rendered: str) -> str:
    """Sisipkan peringatan tepat di bawah judul — bukan di atasnya, supaya judul tetap H1."""
    title, _, body = rendered.partition("\n")
    return f"{title}\n\n{HEADER}{body}"


def render_timeline(timeline: dict) -> str:
    out = ["# Timeline\n", f"\nAcuan: **{timeline['asof']}**\n\n"]
    out.append(gantt(timeline))
    out.append("\n## Per CAP\n\n")
    out.append(table(
        ["CAP", "Judul", "Rilis", "Ukuran", "Prioritas", "Pemilik",
         "Rencana", "Realisasi", "Δ hari", "Keadaan"],
        [[r["id"], r["text"], r["target_release"], r["size"], r["priority"], r["owner"],
          f"{r['planned_start'] or '—'} → {r['planned_end'] or '—'}",
          f"{r['actual_start'] or '—'} → {r['actual_end'] or '—'}",
          "—" if r["delta_days"] is None else f"{r['delta_days']:+d}",
          r["state"]] for r in timeline["capabilities"]]))

    children = [[r["id"], ch["id"], ch["text"], ch["stories"],
                 f"{ch['actual_start'] or '—'} → {ch['actual_end'] or '—'}", ch["state"]]
                for r in timeline["capabilities"] if r["size"] == "L" for ch in r["children"]]
    if children:
        out.append("\n## Rincian FR untuk CAP berukuran L\n\n")
        out.append("CAP berukuran `L` digambar sebagai batang ringkasan; ini isinya.\n\n")
        out.append(table(["CAP", "FR", "Judul", "Story", "Realisasi", "Keadaan"], children))

    if timeline["uncommitted_stories"]:
        out.append("\n## Story tanpa riwayat git\n\n")
        out.append("Berkasnya ada di disk tetapi belum pernah dicommit, jadi tanggalnya "
                   "MUST NOT diturunkan. Commit dulu, lalu jalankan ulang.\n\n")
        out.append("".join(f"- `{sid}`\n" for sid in timeline["uncommitted_stories"]))
    return "".join(out)


def render_report(report: dict, title: str = "Report") -> str:
    since = report["since"] or "awal proyek"
    edge = ("Periode ini tidak berbatas di kiri — belum ada laporan sebelumnya."
            if not report["since"] else
            f"Sejak `{report['since_report']}` ({report['since']}).")
    out = [f"# {title}\n\n"]
    out.append(f"Periode: **{since} → {report['asof']}**. {edge}\n\n")
    out.append(f"Kesegaran: commit `{(report['sha'] or '?')[:12]}`.")
    if report["registry_dirty"]:
        out.append(" **Registry punya perubahan yang belum dicommit — angka di bawah "
                   "belum tentu menggambarkan apa yang ada di `main`.**")
    out.append("\n\n")
    if report["uncommitted_stories"]:
        out.append("> **Peringatan.** Story berikut berstatus terbaca dari working tree tetapi "
                   "belum pernah dicommit: "
                   + ", ".join(f"`{s}`" for s in report["uncommitted_stories"])
                   + ". Ia ikut menghitung progres janji, tetapi MUST NOT muncul di bagian "
                     "Terbukti — di sana tanggalnya harus datang dari git. Commit dulu, lalu "
                     "jalankan ulang.\n\n")

    out.append(f"## Progres janji — {report['progres_janji']}\n\n")
    counts = report["baris_rtm"] or {}
    out.append(f"Ini angka yang berlaku: baris RTM hijau dibagi baris yang dihitung "
               f"({counts.get('hijau', 0)} dari {counts.get('dihitung', 0)}; "
               f"{counts.get('dikecualikan_no_uc', 0)} dikecualikan karena ber-`no_uc`). "
               f"Ia mengukur yang **terbukti**, bukan yang dikerjakan.\n\n")
    out.append(table(["Ukuran lain", "Nilai", "Menjawab"], [
        ["Progres kerja", ", ".join(f"{w.get('wave')} {w.get('progres_kerja')}"
                                    for w in report["progres_kerja"]) or "n/a",
         "berapa banyak yang dikerjakan"],
        ["Kesiapan gate", report["kesiapan_gate"], "apakah gate berikutnya bisa dibuka"],
    ]))

    out.append("\n## 1. Terbukti\n\n")
    out.append("Baris RTM yang berubah hijau dalam periode ini.\n\n")
    out.append(table(["FR", "UC", "Story", "Test", "Tanggal"],
                     [[p["FR"], p["UC"], p["story"], p["test"], p["closed"]]
                      for p in report["proven"]]))

    out.append("\n## 2. Bergerak\n\n")
    out.append(table(["ID", "Lapis", "Peristiwa", "Tanggal"],
                     [[m["id"], m["kind"], m["event"], m["date"]] for m in report["moved"]]))

    out.append("\n## 3. Telat\n\n")
    if report["late"]:
        out.append("Disebut satu per satu. Meringkasnya jadi hitungan adalah cara rencana "
                   "yang meleset tetap terasa nyaman.\n\n")
    out.append(table(["CAP", "Judul", "Pemilik", "Rencana selesai", "Telat (hari)", "Menunggu"],
                     [[l["id"], l["text"], l["owner"], l["planned_end"],
                       l["days_late"], l["waiting_on"]] for l in report["late"]]))

    out.append("\n## 4. Cacat\n\n")
    defects = report["defects"]
    out.append("**Dibuka**\n\n")
    out.append(table(["ID", "Judul", "Root cause", "Melanggar"],
                     [[d["id"], d["title"], d["root_cause"], d["violates"]]
                      for d in defects["opened"]]))
    out.append("\n**Ditutup, dikelompokkan menurut root cause**\n\n")
    out.append(table(["Root cause", "Cacat", "Jumlah"],
                     [[cause, ids, len(ids)]
                      for cause, ids in defects["closed_by_root_cause"].items()]))
    if defects["closed_by_root_cause"]:
        out.append("\nBaris `requirement` dan `architecture` adalah yang layak dibaca dua kali: "
                   "keduanya menghitung cacat yang ternyata bukan kode yang salah.\n")
    if defects["undiagnosed"]:
        out.append("\n**Belum didiagnosis** — terbuka tanpa `root_cause`, seluruh periode\n\n")
        out.append(table(["ID", "Judul", "Dilaporkan", "Umur (hari)"],
                         [[d["id"], d["title"], d["reported"], d["age_days"]]
                          for d in defects["undiagnosed"]]))
        out.append("\nBaris tanpa `root_cause` tidak melanggar apa pun — ia berarti belum ada yang "
                   "menjalankan `wdi-systematic-debugging` atasnya. Selama begitu ia juga tidak "
                   "ikut menghitung rasio di atas, jadi rasio itu berlaku atas cacat yang sudah "
                   "didiagnosis saja.\n")

    out.append("\n## 5. Gate\n\n")
    out.append(table(["Gate", "Tanggal"], [[g["gate"], g["date"]] for g in report["gates"]]))
    return "".join(out)


# ---------------------------------------------------------------------- publish


def period_name(kind: str, asof: dt.date) -> str:
    if kind == "weekly":
        return asof.strftime("%G-W%V")
    if kind == "monthly":
        return asof.strftime("%Y-%m")
    return kind


CATATAN = """
## Catatan

<!-- Ditulis manusia sekali, saat terbit. MUST mengutip sebabnya (ADR, OQ-, risiko, atau
     cacat), bukan menceritakannya ulang — cerita kedua akan menyimpang dari yang pertama.
     Kosongkan bila memang tidak ada yang perlu ditambahkan. -->
"""


def publish(c: Corpus, report: dict, kind: str, asof: dt.date) -> tuple[Path, str | None]:
    name = period_name(kind, asof)
    path = c.root / ".control" / "reports" / f"{name}.md"
    if path.exists():
        return path, (f"{path.name} sudah terbit. Laporan yang sudah terbit itu BEKU — "
                      f"bila ia keliru, laporan berikutnya yang menyatakannya.")
    path.parent.mkdir(parents=True, exist_ok=True)
    front = dump({
        "period": name,
        "asof": report["asof"],
        "since": report["since"],
        "sha": report["sha"],
        "progres_janji": report["progres_janji"],
        "generated_by": ".constitution/scripts/timeline.py",
    })
    path.write_text(f"---\n{front}---\n\n{render_report(report, f'Laporan {name}')}{CATATAN}",
                    encoding="utf-8")
    return path, None


# -------------------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="timeline", description="dimensi waktu dari git: timeline, report, laporan periode")
    parser.add_argument("--generate", action="store_true",
                        help="tulis .control/generated/timeline.* dan report.*")
    parser.add_argument("--publish", metavar="PERIODE",
                        help="bekukan .control/reports/<periode>.md — weekly | monthly | <nama>")
    parser.add_argument("--refresh", action="store_true",
                        help="jalankan validate --generate lebih dulu supaya tabelnya segar")
    parser.add_argument("--root", default=".", help="akar repo (default: direktori sekarang)")
    parser.add_argument("--asof", default=None,
                        help="tanggal acuan, YYYY-MM-DD (default: hari ini)")
    args = parser.parse_args(argv)

    if not args.generate and not args.publish:
        args.generate = True

    root = Path(args.root).resolve()
    if not (root / ".control" / "registry").is_dir():
        print(f"timeline: {root} tidak punya .control/registry/ — salah akar repo?", file=sys.stderr)
        return 2

    asof = dt.date.fromisoformat(args.asof) if args.asof else dt.date.today()
    corpus = Corpus.load(root)

    if git(root, "rev-parse", "HEAD") is None:
        print("timeline: git tidak menjawab di akar ini. Seluruh tanggal realisasi diturunkan "
              "dari git, jadi tanpa git tidak ada yang bisa dilaporkan — dan mengarangnya "
              "MUST NOT dilakukan.", file=sys.stderr)
        return 3

    if args.refresh:
        import validate
        result = validate.run_checks(corpus, asof)
        validate.generate(corpus, result)
        print(f"  segarkan .control/generated/ — {len(result.findings)} temuan validator")

    generated = root / ".control" / "generated"
    missing = [n for n in ("rtm", "status") if not (generated / f"{n}.yaml").exists()]
    if missing:
        print(f"timeline: {', '.join(missing)} belum ada di .control/generated/. Laporan di atas "
              f"tabel yang basi lebih buruk daripada tidak ada laporan — jalankan "
              f"`validate.py --generate`, atau ulangi dengan `--refresh`.", file=sys.stderr)
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
            print(f"  tulis .control/generated/{name}.yaml")
            print(f"  tulis .control/generated/{name}.md")

    if args.publish:
        path, refusal = publish(corpus, report, args.publish, asof)
        if refusal:
            print(f"\ntimeline: {refusal}", file=sys.stderr)
            return 4
        print(f"  terbit {path.relative_to(root).as_posix()}")

    overdue = [r for r in timeline["capabilities"] if r["state"] == "overdue"]
    print(f"\nprogres janji: {report['progres_janji']}"
          f"   ·   CAP telat: {len(overdue)}"
          f"   ·   acuan: {asof.isoformat()}")
    for row in overdue:
        print(f"  TELAT  {row['id']} — rencana selesai {row['planned_end']}, "
              f"menunggu {', '.join(row['waiting_on']) or 'belum ada story'}")
    if report["registry_dirty"]:
        print("\nregistry punya perubahan yang belum dicommit — angka di atas belum tentu "
              "menggambarkan apa yang ada di main")
    if timeline["uncommitted_stories"]:
        print(f"story tanpa riwayat git: {', '.join(timeline['uncommitted_stories'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

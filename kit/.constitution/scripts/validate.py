#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""validate — V1..V27 plus generator .control/generated/.

Dua mode:
    validate --check      keluar non-zero bila ada yang merah; tidak menulis apa pun
    validate --generate   tulis ulang .control/generated/ (dan tetap menjalankan --check)

Determinisme adalah kontraknya: dua run atas data yang sama MUST memberi hasil yang sama.
Karena itu tidak ada iterasi tak berurut, dan satu-satunya masukan yang bergantung waktu
(--asof, dipakai V14) dinyatakan eksplisit alih-alih diambil diam-diam dari jam dinding.

Yang TIDAK dikerjakan di sini: dimensi waktu dari git. `generated/timeline` dan
`generated/report` milik wdi-report. Lihat 08-project-management.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REGISTRY = "control/registry"  # dirapikan di resolve(); '.control' dipakai sebenarnya
GENERATED_ORDER = ["components", "risks", "dag", "rtm", "status"]

# Halaman yang dibaca MANUSIA, bukan mesin: ditulis sebagai tabel markdown sungguhan, bukan yaml
# dalam fence. Ketiganya disebut §22 dan masing-masing punya satu pembaca yang jelas.
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


# ---------------------------------------------------------------- infrastruktur


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
    """Registry list, selalu terurut menurut id supaya keluaran deterministik."""
    value = data.get(key) or []
    if not isinstance(value, list):
        return []
    items = [v for v in value if isinstance(v, dict)]
    return sorted(items, key=lambda r: str(r.get("id", "")))


FM = re.compile(r"\A---\s*\n(.*?)\n---\s*(\n|\Z)", re.S)


class Dumper(yaml.SafeDumper):
    """Tanpa anchor/alias: keluaran MUST bisa dibaca dan di-diff baris demi baris."""

    def ignore_aliases(self, data) -> bool:  # noqa: ARG002
        return True


def dump(payload: dict) -> str:
    return yaml.dump(payload, Dumper=Dumper, allow_unicode=True, sort_keys=False,
                     default_flow_style=False, width=100)


def frontmatter(path: Path) -> dict | None:
    """None bila berkasnya tidak ada; {} bila ada tetapi tanpa frontmatter."""
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


# ------------------------------------------------------------------- pemuatan


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

    # --- pintasan yang dipakai berulang
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
        """`mode` per komponen menang atas global; tanpa keduanya, default `catalog`."""
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
        """(wave, epic, story) — urut menurut id di tiap tingkat."""
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


# ------------------------------------------------------------------ validator


def v1(c: Corpus, r: Result) -> None:
    """Tiap BG punya >=1 FR lewat CAP-nya, ATAU menyatakan alasannya di `no_fr`.

    Sebuah sasaran MAY dipenuhi oleh **invarian**, bukan oleh fitur. `BG-6` — fondasi data dan
    deployment dapat dilanjutkan tanpa dibongkar — diukur oleh dua sifat arsitektural yang `measure`-nya
    sendiri sebut, dan tidak ada `FR` yang dapat memikulnya tanpa dikarang. Menuntut satu `FR` di sana
    menghasilkan janji palsu, dan janji palsu lebih mahal daripada temuan.

    Escape-nya MUST membawa alasan, bukan boolean — bentuk yang sama dengan `no_uc` pada `FR` (V2).
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
        r.fail("V1", gid, "tidak punya FR lewat CAP-nya dan tidak menyatakan alasan di `no_fr`")


def v2(c: Corpus, r: Result) -> None:
    covered = {fr for uc in c.ucs for fr in listy(uc, "satisfies")}
    for fr in c.frs:
        fid = str(fr.get("id"))
        if fid in covered:
            continue
        if str(fr.get("no_uc") or "").strip():
            continue
        r.fail("V2", fid, "tidak punya UC dan tidak menyatakan alasan di `no_uc`")


def v3(c: Corpus, r: Result) -> None:
    """Sebuah UC pada komponen yang SUDAH disentuh sebuah wave MUST dijadwalkan story.

    Bentuk lama menuntutnya atas SETIAP UC, kapan pun. Sebelum wave pertama itu berarti seluruh
    katalog dilaporkan merah — 56 temuan dari 62, dan ke-56 itu keadaan yang benar, bukan drift:
    story lahir di wave, dan belum ada wave. Sebuah validator yang menenggelamkan enam temuan nyata
    di bawah lima puluh enam yang diharapkan berhenti dibaca, dan validator yang tidak dibaca tidak
    menjaga apa pun.

    Yang dijaga sekarang adalah kelalaian yang sebenarnya: sebuah wave menyentuh komponen, dan sebuah
    UC komponen itu tertinggal tanpa story. Cakupan penuh atas seluruh katalog adalah pertanyaan G5,
    dan `wdi-build` yang memilikinya — sama seperti V12 yang digeser ke penutupan wave.
    """
    scheduled = {uc for _, _, s in c.stories() for uc in listy(s, "satisfies")}
    touched = {str(s.get("component")) for _, _, s in c.stories() if s.get("component")}
    if not c.wave_list:
        r.skip("V3", "belum ada wave, jadi belum ada story — tiap UC tak terjadwal adalah keadaan "
                     "yang benar. Cakupan penuh katalog diperiksa di G5")
        return
    for uc in c.ucs:
        uid = str(uc.get("id"))
        if uid in scheduled or str(uc.get("component")) not in touched:
            continue
        r.fail("V3", uid, f"komponen `{uc.get('component')}` sudah disentuh sebuah wave, "
                          f"tetapi UC ini tidak dijadwalkan story mana pun")


def v4(c: Corpus, r: Result) -> None:
    for _, _, story in c.stories():
        if not [t for t in listy(story, "tests") if t.strip()]:
            r.fail("V4", str(story.get("id")), "tidak punya satu pun test bernama")


def v5(c: Corpus, r: Result) -> None:
    """Tiap NFR punya penegak, ATAU menyatakan alasannya di `no_enforcer`.

    Dua NFR di repo ini tidak dapat punya penegak, dan keduanya sah: satu sudah **dicabut**, dan satu
    lagi menyatakan sendiri bahwa ia **ukuran perancangan, bukan pagar**. Menuntut test untuk keduanya
    menghasilkan test yang tidak mungkin gagal, dan test yang tidak mungkin gagal adalah teater.
    """
    for nfr in c.nfrs:
        if [e for e in listy(nfr, "enforced_by") if e.strip()]:
            continue
        if str(nfr.get("no_enforcer") or "").strip():
            continue
        r.fail("V5", str(nfr.get("id")),
               "tidak punya penegak di `enforced_by` dan tidak menyatakan alasan di `no_enforcer`")


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
            r.fail("V6", owner, f"menunjuk `{target}` yang tidak ada di registry mana pun")


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
        r.fail("V7", node, "ikut dalam siklus `depends_on` antar-CAP")
    stories = {str(s.get("id")): listy(s, "depends_on") for _, _, s in c.stories()}
    for node in _cycles(stories):
        r.fail("V7", node, "ikut dalam siklus `depends_on` antar-story")


def v8(c: Corpus, r: Result) -> None:
    """Tiap keputusan `applied` menyebut `touches` yang tidak kosong.

    Menggantikan bentuk lama "tiap keputusan accepted melayani >=1 FR/NFR". Keputusan seperti
    "filter harus begini" tidak melayani FR mana pun, dan itu SAH — justru keputusan seperti itu
    yang paling perlu diingat, dan aturan lama menyingkirkannya.
    """
    for dec in c.decs:
        if str(dec.get("status")) != "applied":
            continue
        if not [x for x in listy(dec, "touches") if str(x).strip()]:
            r.fail("V8", str(dec.get("id")),
                   "berstatus applied tetapi `touches` kosong — penerapan tanpa jejak berkas")


def v9(c: Corpus, r: Result) -> None:
    passed = {str(g) for g in (c.index.get("gates_passed") or [])}
    for path in sorted(c.root.glob(".what/**/*.md")) + sorted(c.root.glob(".how/**/*.md")):
        fm = frontmatter(path) or {}
        if str(fm.get("status")) != "locked":
            continue
        gate = str(fm.get("locked_at_gate") or "")
        if gate not in passed:
            rel = path.relative_to(c.root).as_posix()
            r.fail("V9", rel, f"berstatus locked tetapi gate `{gate or '?'}` tidak tercatat lulus")


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
                       f"berbagi touches {shared} tanpa relasi depends_on — MUST NOT paralel")


def v12(c: Corpus, r: Result) -> None:
    """Pendaftaran LC diperiksa saat wave DITUTUP, bukan sebelum story `ready-for-dev`.

    Bentuk lama menuntut jawabannya pada saat informasinya paling tipis. Di penutupan wave,
    tiap `touches` sudah punya wilayah dan tiap boundary sudah punya nama.
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
                       f"wave-nya sudah ditutup, tetapi `{area}` tidak terdaftar sebagai `area` "
                       f"di components.yaml")
        pid = str(story.get("component") or "")
        row = pc_by_id.get(pid)
        if row is None or (str(wave.get("id")), pid) in seen:
            continue
        seen.add((str(wave.get("id")), pid))
        if c.mode_of(row) in ("guarded", "deep") and not lcs_per_pc.get(pid):
            r.fail("V12", f"{wave.get('id')} / {pid}",
                   f"wave tertutup dan komponen ber-mode `{c.mode_of(row)}` belum punya satu pun "
                   f"`LC` terdaftar")


LENS_BY_RISK = {
    "low": {"edge-case-hunter"},
    "medium": {"edge-case-hunter"},
    "high": set(),
}
FRONTMATTER_KEYS = ("reviewed:", "date:", "sha:", "lenses:", "updated:")


def _reviewed_ok(r: Result, rel: str, block: object, need: set[str]) -> None:
    if not isinstance(block, dict) or not block.get("sha") or not block.get("date"):
        r.fail("V13", rel, "tidak membawa jejak `reviewed` berisi date dan sha")
        return
    lenses = {str(x) for x in (block.get("lenses") or [])}
    if not lenses:
        r.fail("V13", rel, "jejak `reviewed` tidak menyebut satu lensa pun")
    missing = sorted(need - lenses)
    if missing:
        r.fail("V13", rel,
               f"lensa {missing} MUST ikut — itu yang dituntut `risk_accepted` komponennya")


def _only_reviewed_block(diff: str) -> bool:
    """True bila diff sebuah commit atas satu berkas HANYA menyentuh blok `reviewed:`.

    Inilah perbaikan OQ-146. V13 lama membandingkan `sha` dengan commit terakhir yang mengubah
    berkasnya — tetapi commit yang MENULISKAN blok `reviewed:` selalu mengubah berkasnya, dan
    menulis hash diri sendiri ke dalam sebuah commit git mustahil secara kriptografis. Akibatnya
    setiap artefak yang baru distempel langsung terbaca "review basi", selamanya.
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
    """Commit pertama sesudah `sha` yang mengubah berkas ini karena alasan selain stempel review."""
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
    """Jejak review mengikuti INTENSITAS review, bukan kedalaman dokumen.

    Dipersempit ke komponen ber-`risk_accepted` `low` atau `medium`. Pada `high` pemilik sudah
    menyatakan menerima risikonya, dan menuntut jejak di situ adalah pembukuan tanpa pembeli.
    """
    watched = [pc for pc in c.pcs
               if str(pc.get("risk_accepted") or "").strip() in ("low", "medium")]
    if not watched:
        r.skip("V13", "tidak ada komponen ber-risk_accepted low atau medium — tidak ada yang dijaga")
    targets: list[tuple[Path, set[str]]] = []
    if watched:
        targets.append((c.root / ".how/_platform/ARCHITECTURE-SPINE.md", set()))
    for pc in watched:
        pid = str(pc.get("id"))
        need = LENS_BY_RISK.get(str(pc.get("risk_accepted")).strip(), set())
        # SRS ada dan bermakna pada SETIAP mode: ia membawa Actor Register dan UC Catalogue, dan
        # keduanya lahir di G3 yang tidak disentuh knob kedalaman.
        targets.append((c.root / f".what/{pid}/SRS-{pid}.md", need))
        # SDD hanya dijaga ketika ia PUNYA ISI untuk dijaga. Dua keadaan mengecualikannya, dan
        # keduanya keadaan SELESAI bukan keadaan tertinggal:
        #   mode: catalog        skeleton adalah bentuk akhirnya; G4 dilewati di situ
        #   g4_passed belum ada  G4 belum dijalankan, jadi tidak ada satu bagian pun yang tertulis
        # Menuntut jejak review atas berkas yang isinya 13 baris komentar template adalah teater —
        # persis upacara yang rancang ulang ini cabut, dan review yang tidak mungkin gagal tidak
        # membuktikan apa pun. Begitu G4 lewat, tuntutannya kembali dan ia bermakna.
        passed = str(pc.get("g4_passed") or "").strip().lower()
        if c.mode_of(pc) != "catalog" and passed not in ("", "false", "no", "belum"):
            targets.append((c.root / f".how/{pid}/SDD-{pid}.md", need))

    for path, need in targets:
        fm = frontmatter(path)
        if fm is None:
            continue  # belum lahir — bukan urusan V13
        rel = path.relative_to(c.root).as_posix()
        _reviewed_ok(r, rel, fm.get("reviewed"), need)
        block = fm.get("reviewed")
        if isinstance(block, dict) and block.get("sha"):
            stale = _stale_since(c, rel, str(block["sha"]))
            if stale:
                r.fail("V13", rel,
                       f"berubah di {stale[:7]} sesudah direview di {str(block['sha'])[:7]} — "
                       f"review basi")

    for wave in c.wave_list:
        if not wave.get("epics"):
            continue
        _reviewed_ok(r, f"waves.yaml:{wave.get('id')}", wave.get("spec_reviewed"),
                     {"edge-case-hunter"})


def cap_stories(c: Corpus) -> dict[str, list[dict]]:
    """CAP -> story, ditelusuri CAP -> FR -> UC -> story. Tanpa git, tanpa timeline."""
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
    """Keterlambatan dihitung dari registry sendiri — timeline hanya memperkuat, bukan syarat."""
    by_cap = cap_stories(c)
    timeline = load_yaml(c.root / ".control/generated/timeline.yaml")
    listed = {str(row.get("id")) for row in rows(timeline, "capabilities")
              if str(row.get("state")) == "overdue"} if timeline else None
    if listed is None:
        r.skip("V14", "generated/timeline.yaml belum ada — keterlambatan tetap dihitung "
                      "dari registry, tetapi kehadirannya di generated/report tidak diperiksa")

    for cap in c.caps:
        cid = str(cap.get("id"))
        end = str(cap.get("planned_end") or "")
        if not end:
            continue
        try:
            due = dt.date.fromisoformat(end)
        except ValueError:
            r.fail("V14", cid, f"`planned_end` `{end}` bukan tanggal ISO")
            continue
        items = by_cap.get(cid, [])
        closed = bool(items) and all(_story_status(c, s) == "done" for s in items)
        if closed or due >= asof:
            continue
        late = (asof - due).days
        if listed is not None and cid not in listed:
            r.fail("V14", cid, f"lewat {late} hari tanpa realisasi, dan tidak disebut "
                               f"`overdue` di generated/timeline")
        else:
            r.fail("V14", cid, f"lewat {late} hari tanpa realisasi tertutup")


def v15(c: Corpus, r: Result) -> None:
    for cap in c.caps:
        if not str(cap.get("goal") or "").strip():
            r.fail("V15", str(cap.get("id")), "tidak menunjuk `goal`")
    for fr in c.frs:
        if not str(fr.get("capability") or "").strip():
            r.fail("V15", str(fr.get("id")), "tidak menunjuk `capability`")


def v16(c: Corpus, r: Result) -> None:
    for path in sorted((c.root / ".control/memlog").glob("*.md")):
        fm = frontmatter(path) or {}
        rel = path.relative_to(c.root).as_posix()
        artifact = str(fm.get("artifact") or "")
        if not artifact:
            r.fail("V16", rel, "tidak punya `artifact:` di frontmatter")
        elif not (c.root / artifact).exists():
            r.fail("V16", rel, f"`artifact:` menunjuk `{artifact}` yang tidak ada")
    for layer in (".what", ".how"):
        for stray in sorted(c.root.glob(f"{layer}/**/.memlog.md")):
            r.fail("V16", stray.relative_to(c.root).as_posix(),
                   "memlog MUST NOT tinggal di dalam korpus")


def v17(c: Corpus, r: Result) -> None:
    for wave in c.wave_list:
        wid = str(wave.get("id"))
        if not str(wave.get("release") or "").strip():
            r.fail("V17", wid, "tidak menyebut `release`")
        slugs = listy(wave, "prd")
        if not slugs:
            r.fail("V17", wid, "tidak menyebut `prd`")
        for slug in slugs:
            if not (c.root / ".what/_prd" / slug).is_dir():
                r.fail("V17", wid, f"`prd: {slug}` tidak punya folder .what/_prd/{slug}/")


def v18(c: Corpus, r: Result) -> None:
    for _, _, story in c.stories():
        sid = str(story.get("id"))
        folder = str(story.get("spec_folder") or "").strip()
        if not folder:
            r.fail("V18", sid, "tidak menyebut `spec_folder`")
            continue
        matches = sorted((c.root / folder / "stories").glob(f"{sid}-*.md"))
        if not matches:
            r.fail("V18", sid, f"tidak punya story file di {folder}stories/")
            continue
        fm = frontmatter(matches[0]) or {}
        if not str(fm.get("status") or "").strip():
            r.fail("V18", sid, "story file tidak punya `status` di frontmatter")


def v19(c: Corpus, r: Result) -> None:
    """Arsip retrospektif diikatkan ke UKURAN WAVE, bukan ke `mode`.

    Wajib pada wave `L`; advisory pada `S` dan `M`. Kedalaman dokumen dan volume kerja adalah dua
    hal berbeda, dan menuntut retrospektif atas wave tiga story adalah upacara.
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
            r.fail("V19", wid, "wave `L` tertutup tanpa `RTR-` di .control/reports/")
        else:
            advisory.append(wid)
    if advisory:
        r.skip("V19", "advisory — wave S/M tertutup tanpa RTR-: " + ", ".join(sorted(advisory)))
    else:
        r.skip("V19", "hanya baris RTR- yang diperiksa mekanis; sisa distilasi dijaga wdi-build")


PLATFORM = "_platform"
CROSS_CUTTING = ".how/_platform/cross-cutting.md"
PLATFORM_DATA_HEADING = "Milik platform"


def v21(c: Corpus, r: Result) -> None:
    """Satu entitas domain punya TEPAT SATU pemilik yang berwenang menulisnya.

    Pemiliknya sebuah Product Component, ATAU `_platform` untuk entitas yang tidak ada satu pun
    janji komponen di belakangnya. Bentrokan semantik antar-PRD sudah pernah terjadi sungguhan: satu
    komponen mengambil rentang penomoran business rule dari deret global milik bersama. Dua `FR`
    yang mengklaim wewenang tulis atas entitas yang sama, tanpa salah satunya menunjuk yang lain,
    adalah defect saat ditulis.

    `_platform` BUKAN Product Component dan karena itu tidak punya `mode`, `risk_accepted`, SRS,
    maupun G4. Ia rumah kepemilikan, bukan irisan domain — dan supaya ia tidak jadi tempat
    pembuangan, tiap entitas yang ia klaim MUST dijelaskan di `cross-cutting.md`: kalau platform
    memiliki data, platform yang mendokumentasikannya.
    """
    owner: dict[str, str] = {}
    for pc in c.pcs:
        pid = str(pc.get("id"))
        for entity in listy(pc, "owns"):
            if entity in owner and owner[entity] != pid:
                r.fail("V21", entity,
                       f"diklaim `owns` oleh `{owner[entity]}` dan `{pid}` — satu entitas MUST "
                       f"punya tepat satu pemilik")
            else:
                owner.setdefault(entity, pid)

    platform = listy(c.components, "platform_owns")
    for entity in platform:
        if entity in owner:
            r.fail("V21", entity,
                   f"diklaim `platform_owns` dan juga `owns` milik `{owner[entity]}` — "
                   f"`{PLATFORM}` bukan jalan kedua bagi entitas yang sudah punya pemilik")
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
                # Platform tidak punya `FR`, jadi tidak ada yang bisa ditunjuk `defers_to`. Yang
                # menggantikan "satu penulis" di sini adalah SATU BENTUK YANG TERDOKUMENTASI, dan
                # itu diperiksa _platform_documented di atas.
                continue
            if not [d for d in listy(fr, "defers_to") if str(d).strip()]:
                r.fail("V21", fid,
                       f"menjanjikan penulisan `{entity}` yang dimiliki `{own}`, tanpa `defers_to` "
                       f"menunjuk `FR` milik pemiliknya")


def _platform_inventory_rows(c: Corpus) -> list[str]:
    """Baris inventaris yang dimiliki `_platform`, dibaca dari `platform_rows:` tiap inventaris.

    `_platform` adalah nilai sah di SETIAP posisi kepemilikan, jadi penjaganya berlaku di setiap
    posisi juga: apa pun yang ia miliki MUST terdokumentasi di `cross-cutting.md`.
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
    """Tiap entitas ber-`platform_owns` MUST disebut di `cross-cutting.md`.

    Dilewati selama berkasnya belum memuat bagian itu: `cross-cutting.md` adalah keluaran G3, dan
    artefak yang gate berikutnya lahirkan MUST NOT dilaporkan hilang.
    """
    if not entities:
        return
    path = c.root / CROSS_CUTTING
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    if PLATFORM_DATA_HEADING.lower() not in text.lower():
        r.skip("V21", f"`{CROSS_CUTTING}` belum punya bagian `{PLATFORM_DATA_HEADING}` — "
                      f"{len(entities)} entitas ber-platform_owns belum terdokumentasi: "
                      + ", ".join(sorted(entities)))
        return
    for entity in sorted(entities):
        if entity not in text:
            r.fail("V21", entity,
                   f"diklaim `platform_owns` tetapi tidak disebut di `{CROSS_CUTTING}` — "
                   f"platform yang memiliki data MUST mendokumentasikannya")


def v22(c: Corpus, r: Result) -> None:
    """Sebuah wave MUST NOT menyentuh komponen yang G4-nya belum lewat dan mode-nya bukan catalog.

    `catalog` melewati G4 dengan sengaja, jadi ia bukan pengecualian — ia bagian aturannya.
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
            r.fail("V22", pid, f"`mode: {mode}` bukan salah satu dari {list(MODES)}")
            continue
        passed = row.get("g4_passed")
        if not passed or str(passed).strip().lower() in ("false", "no", "belum"):
            r.fail("V22", f"{wave.get('id')} / {pid}",
                   f"wave menyentuh komponen ber-mode `{mode}` yang `g4_passed`-nya belum diisi")


def v23(c: Corpus, r: Result) -> None:
    """`risk_accepted: high` pada komponen sensitif menuntut sebuah `DEC-` di `risk_accepted_by`.

    Pada komponen yang tidak menyentuh apa pun dari daftar itu, `high` GRATIS. Kontrolnya
    pengungkapan, bukan veto — pemilik tetap boleh memilih cepat, tapi tidak tanpa tahu apa yang ia
    taruhkan.
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
                   f"`risk_accepted: high` sementara `risk_note` menyebut {hits}, tanpa "
                   f"`risk_accepted_by` menunjuk sebuah `DEC-` bertipe risk-acceptance")
        elif ref not in known:
            r.fail("V23", pid, f"`risk_accepted_by: {ref}` tidak ada di decisions.yaml")


def v20(c: Corpus, r: Result) -> None:
    needs_link = {"requirement", "architecture"}
    for defect in c.defect_list:
        did = str(defect.get("id"))
        cause = str(defect.get("root_cause") or "")
        if cause not in needs_link:
            continue
        if not listy(defect, "violates"):
            r.fail("V20", did, f"ber-root_cause `{cause}` tetapi `violates` kosong")
        if str(defect.get("status")) == "fixed" and not str(defect.get("decision") or "").strip():
            r.fail("V20", did,
                   f"ditutup sebagai fixed dengan root_cause `{cause}` tanpa `DEC-` yang menyertainya")


# Berkas yang MENGGAMBARKAN masa lalu, bukan MENYATAKAN apa yang berlaku. Kutipan menggantung di sini
# bukan temuan — corpus-guide.md memiliki aturannya, dan menulisnya ulang akan memalsukan riwayat.
PAST_RECORD = (
    ".control/memlog/",
    ".control/decisions/",
    ".control/questions/answered.md",
    ".control/reports/",
)
# Korpus yang §25 bekukan apa adanya. Kutipannya ke prototipe yang sudah dipensiunkan disahkan DEC-016.
FROZEN = (".what/",)
# Path yang sebuah run LAHIRKAN, bukan yang sebuah dokumen kutip. Aturan yang menyatakan "memlog pass
# ini mendarat di X" menyebut TUJUAN; menuntut X sudah ada berarti menuntut run-nya sudah jalan.
DESTINATION = (
    ".control/memlog/",
    ".control/meetings/",
    ".control/reports/",
    "_bmad-output/",
)

CITE_RE = re.compile(
    r"`((?:\.constitution|\.control|\.what|\.how|_bmad-output|\.work|src|web|public|deploy)"
    r"/[A-Za-z0-9_./-]+\.(?:md|yaml|yml|py|go|tsx|ts|js|mjs|sql|html|css|json))`")


def v24(c: Corpus, r: Result) -> None:
    """Kutipan path di dalam dokumen yang MENYATAKAN apa yang berlaku MUST resolve.

    Ini paruh mekanis dari Evidence check `wdi-reconcile`, dan ia satu-satunya cara mengetahui bahwa
    sebuah migrasi tetap tuntas. Kelas kegagalannya khas: sebuah berkas dihapus atau dipindahkan,
    sementara baris routing yang menunjuk ke arahnya tinggal — tidak ada satu pun validator lain yang
    melihatnya, sebab tidak ada id yang bergerak.

    Yang DILEWATI dengan sengaja: berkas yang menggambarkan masa lalu, dan korpus yang dibekukan.
    Sebuah Trace `DEC-` yang menyebut bahan yang sudah dipensiunkan menggambarkan apa yang dibaca pada
    tanggal itu; melaporkannya akan menuntut riwayat ditulis ulang agar cocok dengan masa kini.
    """
    scanned = 0
    for path in sorted(c.root.rglob("*.md")) + sorted(c.root.rglob("*.yaml")):
        rel = path.relative_to(c.root).as_posix()
        if rel.startswith((".git/", "node_modules/", "_bmad-output/", ".claude/skills/bmad-")):
            continue
        if rel.startswith(PAST_RECORD) or rel.startswith(FROZEN):
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for cited in sorted(set(CITE_RE.findall(text))):
            if "<" in cited or "{" in cited:
                continue  # placeholder, bukan path
            if cited.startswith(DESTINATION):
                continue
            if not (c.root / cited).exists():
                r.fail("V24", rel, f"mengutip `{cited}` yang tidak ada")
    if not scanned:
        r.skip("V24", "tidak ada berkas yang dipindai")


CTR_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.M)


def map_container_headings(root: Path) -> list[str] | None:
    """Heading `### x` di bawah `## Containers` pada peta kode. None bila petanya tidak ada."""
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
    """`built` sebuah container dan keempat konsekuensinya, plus matriks PC x container.

    Sebuah container ADA di dalam boundary entah kita yang menulis isinya atau bukan, dan itulah yang
    dulu membuat aturannya tak bisa dipenuhi: `structure-guide.md` menuntut tiap heading peta kode cocok
    dengan registry, sementara basis data dan web server MUST terdaftar dan MUST NOT punya heading.
    `built` memisahkan keduanya, dan pemeriksaan ini yang membuat pemisahan itu berlaku alih-alih
    diulang argumennya tiap proyek. `DEC-017` merekam definisinya.

    Yang runtime-nya bukan kita yang deploy adalah external system: ia hidup di C4 L1 dan MUST NOT
    terdaftar di sini sama sekali — ketiadaannya di registry itulah pemeriksaannya.
    """
    containers = rows(c.components, "containers")
    if not containers:
        r.skip("V25", "`containers:` belum terdaftar")
        return

    built: dict[str, bool] = {}
    for ctr in containers:
        cid = str(ctr.get("id") or "").strip()
        if not cid:
            r.fail("V25", "containers", "ada container tanpa `id`")
            continue
        flag = ctr.get("built")
        if not isinstance(flag, bool):
            r.fail("V25", cid, "`built` MUST bool — true bila isinya kita tulis, false bila implementasinya orang lain")
            continue
        built[cid] = flag

    # (1) heading peta kode = TEPAT container `built: true`
    headings = map_container_headings(c.root)
    if headings is None:
        r.fail("V25", ".control/structure-codebase.md", "peta kode tidak ada, jadi heading container tidak dapat diadu")
    else:
        for h in headings:
            if h not in built:
                r.fail("V25", f"peta kode §{h}", "heading bukan container terdaftar — daftarkan, atau ia bukan container")
            elif not built[h]:
                r.fail("V25", f"peta kode §{h}", "`built: false` MUST NOT punya heading — tidak ada kode kita di dalamnya")
        for cid, flag in sorted(built.items()):
            if flag and cid not in headings:
                r.fail("V25", cid, "`built: true` MUST punya heading di peta kode")

    # (2) `built: false` MUST NOT dipakai sebuah LC, dan (3) MUST NOT muncul di `containers:` sebuah PC
    for lc in c.lcs:
        ctr = str(lc.get("container") or "").strip()
        if ctr and built.get(ctr) is False:
            r.fail("V25", str(lc.get("id") or "LC-?"), f"menyebut container `{ctr}` yang `built: false`")
        elif ctr and ctr not in built:
            r.fail("V25", str(lc.get("id") or "LC-?"), f"menyebut container `{ctr}` yang tidak terdaftar")

    # (4) matriks PC x container — SSOT-nya field ini, dan ia MUST lengkap di G3
    for pc in c.pcs:
        pid = str(pc.get("id") or "?")
        listed = listy(pc, "containers")
        if not listed:
            r.fail("V25", pid, "`containers:` kosong — tiap PC MUST hidup di setidaknya satu container (utang G3)")
            continue
        for ctr in listed:
            if ctr not in built:
                r.fail("V25", pid, f"`containers:` menyebut `{ctr}` yang tidak terdaftar")
            elif not built[ctr]:
                r.fail("V25", pid, f"`containers:` menyebut `{ctr}` yang `built: false` — data hidup di sana menurut definisi, jadi barisnya tidak memberi tahu apa pun")

    # (5) L3 — hanya untuk `built: true`, dan hanya yang memuat lebih dari satu PC
    pcs_per: dict[str, list[str]] = {}
    for pc in c.pcs:
        for ctr in listy(pc, "containers"):
            pcs_per.setdefault(ctr, []).append(str(pc.get("id") or "?"))
    for path in sorted((c.root / ".how" / "_platform").glob("c4-l3-*.md")):
        cid = path.name[len("c4-l3-"):-len(".md")]
        if cid not in built:
            r.fail("V25", path.relative_to(c.root).as_posix(),
                   f"L3 untuk `{cid}` yang bukan container terdaftar")
        elif not built[cid]:
            r.fail("V25", path.relative_to(c.root).as_posix(),
                   f"`{cid}` `built: false` MUST NOT punya L3 — tak satu kotak di dalamnya kita yang gambar")
    for cid, pids in sorted(pcs_per.items()):
        if built.get(cid) and len(pids) > 1:
            l3 = c.root / ".how" / "_platform" / f"c4-l3-{cid}.md"
            if not l3.exists():
                r.fail("V25", cid, f"memuat {len(pids)} PC, jadi `c4-l3-{cid}.md` MUST ada")


UC_ROW_RE = re.compile(r"^\|\s*(UC-\d+)\s*\|([^\n]*)$", re.M)

# Nilai kolom `critical` dicocokkan mesin, jadi ia machine-facing dan bentuk kanoniknya English `yes`.
# `ya` tetap diterima: sebuah korpus yang menulisnya sebelum aturan ini berlaku MUST NOT dipaksa migrasi
# hanya supaya sebuah regex lebih rapi. Batas kata mencegah `ya` mencocoki kata lain.
CRITICAL_YES = re.compile(r"\b(yes|ya)\b", re.I)


def v26(c: Corpus, r: Result) -> None:
    """Katalog UC di tiap SRS MUST sepakat dengan `usecases.yaml` — id-nya DAN `critical`-nya.

    Ini celah yang paling mahal dari semua yang ditutup lintasan ini, sebab ia satu-satunya yang
    **sudah terjadi dan tidak satu pun validator melihatnya.** Step 16 menurunkan ulang `critical`
    di registry dengan definisi yang dipersempit — uang, data pribadi, tindakan tak-terbalikkan — dan
    ketujuh tabel katalog di SRS tidak ikut. Dua puluh enam baris berselisih, dan selisihnya baru
    ketahuan ketika seorang manusia membaca kalimat "sembilan di antaranya critical" di SRS-admin
    sementara registry menyimpan tiga.

    Registry-nya SSOT. Tabel di SRS adalah rumah permanen katalog untuk seorang pembaca, dan dua rumah
    untuk satu fakta hanya aman kalau ada yang mengadu keduanya. Ini yang mengadu.

    Yang TIDAK diperiksa di sini: judul dan aktor. Keduanya prosa, dan prosa yang berbeda kata bukan
    prosa yang berbeda arti — mengadunya akan melaporkan gaya sebagai cacat.
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
                r.fail("V26", f"{pid}/{uid}", "ada di katalog SRS tetapi tidak di `usecases.yaml`")
                continue
            if reg_pc[uid] != pid:
                r.fail("V26", f"{pid}/{uid}",
                       f"registry menaruhnya di `{reg_pc[uid]}`, bukan di komponen ini")
            marked = CRITICAL_YES.search(cells[3]) is not None
            if marked != reg[uid]:
                r.fail("V26", f"{pid}/{uid}",
                       f"`critical` in the SRS {'yes' if marked else 'no'}, "
                       f"in the registry {'yes' if reg[uid] else 'no'}")
        for uid, owner in sorted(reg_pc.items()):
            if owner == pid and uid not in seen:
                r.fail("V26", f"{pid}/{uid}", "ada di `usecases.yaml` tetapi tidak di katalog SRS")
    if not checked:
        r.skip("V26", "tidak ada SRS yang dapat dibaca")


def v27(c: Corpus, r: Result) -> None:
    """Tiap berkas di kamar custom MUST menyatakan dirinya, dan pembantahan MUST punya keputusan.

    Kamar `.constitution/project/` ada supaya aturan khusus produk punya rumah yang `update` tidak
    timpa dan `promote` tidak terbitkan. Ongkos yang datang bersamanya: ia juga tempat paling mudah
    untuk melanggar aturan generic tanpa jejak. Frontmatter-nya yang menahan itu.

    Sebuah berkas di sini MAY mempersempit atau menambah tanpa menyebut apa pun. Untuk MEMBANTAH
    aturan generic ia MUST menyebutnya di `overrides:` dan membawa `decision:` — sebab metode yang
    boleh dibantah tanpa keputusan berhenti dapat dipercaya di repo berikutnya.

    `README.md` kamar dilewati: ia dikarang di paket, bukan di produk.
    """
    room = c.root / ".constitution" / "project"
    if not room.is_dir():
        r.skip("V27", "kamar `.constitution/project/` belum ada — ia disemai saat install")
        return
    files = [p for p in sorted(room.rglob("*.md")) if p.name != "README.md"]
    if not files:
        r.skip("V27", "kamar `.constitution/project/` kosong, dan itu keadaan yang sah — "
                      "aturan generic MUST NOT dipindahkan ke sini supaya kamarnya terpakai")
        return
    dec_ids = {str(d.get("id")) for d in c.decs}
    for path in files:
        rel = path.relative_to(c.root).as_posix()
        fm = frontmatter(path)
        if fm is None:
            r.fail("V27", rel, "tidak punya frontmatter")
            continue
        if str(fm.get("scope") or "").strip() != "project":
            r.fail("V27", rel, "`scope:` MUST berisi tepat `project`")
        if not str(fm.get("purpose") or "").strip():
            r.fail("V27", rel, "`purpose:` kosong — satu baris: aturan ini menjaga apa")
        over = str(fm.get("overrides") or "").strip()
        dec = str(fm.get("decision") or "").strip()
        if over:
            if not (c.root / over).exists():
                r.fail("V27", rel, f"`overrides:` menunjuk `{over}` yang tidak ada — "
                                   f"aturan yang dibantah mungkin sudah hilang")
            if not dec:
                r.fail("V27", rel, "membantah aturan generic tanpa `decision:` — "
                                   "pembantahan MUST punya `DEC-` yang memutuskannya")
            elif dec not in dec_ids:
                r.fail("V27", rel, f"`decision: {dec}` tidak terdaftar di decisions.yaml")
        elif dec:
            r.fail("V27", rel, "`decision:` terisi tanpa `overrides:` — "
                               "sebutkan aturan mana yang dibantah, atau cabut `decision:`")


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
            if not ready:  # siklus — V7 sudah melaporkannya
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
                         "progres_kerja": _pct(done, len(items))})
    applicable = 26  # V1..V27 tanpa V10 yang gugur
    return {
        "progres_janji": _pct(green, len(counted)),
        "baris_rtm": {"hijau": green, "dihitung": len(counted),
                      "dikecualikan_no_uc": exempt},
        "progres_kerja": per_wave,
        "kesiapan_gate": _pct(applicable - len(result.red), applicable),
        "validator_merah": result.red,
        "validator_dilewati": dict(sorted(result.skipped.items())),
        "pertanyaan_terbuka": _question_budget(c),
    }


def _question_budget(c: Corpus) -> dict:
    """Hitungan keempat daftar pertanyaan, diadu dengan jatah di index.yaml.

    Jatahnya BUKAN pagar keras. Ia yang dilaporkan ketika sebuah batch melewatinya, karena batch
    yang lebih besar adalah sinyal tentang lintasannya, bukan tentang korpus.
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
        out["blocking_jatah"] = allowed
        out["blocking_lewat_jatah"] = out["blocking"] > allowed
    cap_assume = budget.get("assumptions_per_gate")
    if cap_assume:
        out["assumptions_jatah_per_gate"] = int(cap_assume)
    return out


def _pct(part: int, total: int) -> str:
    return "n/a" if total == 0 else f"{round(100 * part / total)}%"


def as_markdown(name: str, payload: dict) -> str:
    body = dump(payload)
    return (f"# {name}\n\n"
            f"> Tergenerate oleh `.constitution/scripts/validate --generate`. "
            f"MUST NOT diedit tangan.\n\n"
            f"```yaml\n{body}```\n")


# ------------------------------------------------------- halaman untuk manusia

PAGE_HEADER = ("> Tergenerate oleh `.constitution/scripts/validate --generate`. "
               "MUST NOT diedit tangan.\n")


def _section(path: Path, heading: str) -> str:
    """Ambil satu bagian `## <heading>` dari sebuah berkas markdown, apa adanya."""
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
    """Isi berkas tanpa frontmatter dan tanpa komentar template."""
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
    """Tabel rata seluruh `DEC-`. Ini yang menggantikan mencari keputusan lewat memlog."""
    rows_out = ["| id | Judul | Status | Tipe | Menyentuh | Berkas |",
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
    tally = " · ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "belum ada keputusan"
    return ("# decisions\n\n" + PAGE_HEADER +
            "\nMencari keputusan tidak lagi lewat memlog — memlog kembali jadi log lintasan saja.\n"
            f"\n**{len(c.decs)} keputusan** — {tally}.\n\n" + "\n".join(rows_out) + "\n")


def page_blueprint(c: Corpus) -> str:
    """Roll-up satu halaman yang di-review di G3. Tujuh berkas jadi satu bacaan.

    Katalog UC, daftar aktor, dan model domain tetap tinggal di kernel komponennya masing-masing
    sebagai rumah permanennya. Ini tampilannya. Satu fakta, satu rumah, satu tampilan.
    """
    parts = ["# blueprint\n", PAGE_HEADER,
             "\nIni yang dibaca pemilik di **G3 Blueprint**, bukan tujuh berkas. Isinya tidak "
             "dipengaruhi `mode` maupun `risk_accepted`.\n"]

    crit = sum(1 for uc in c.ucs if uc.get("critical"))
    parts.append(f"\n## Katalog use case\n\n**{len(c.ucs)} use case**, {crit} bertanda "
                 f"`critical`.\n")
    parts.append("| id | Use case | Komponen | Memenuhi | critical |")
    parts.append("| --- | --- | --- | --- | --- |")
    for uc in c.ucs:
        sat = ", ".join(f"`{x}`" for x in listy(uc, "satisfies")) or "—"
        flag = "ya" if uc.get("critical") else "tidak"
        parts.append(f"| `{uc.get('id')}` | {_cell(uc.get('title'))} | "
                     f"`{uc.get('component', '')}` | {sat} | {flag} |")

    parts.append("\n## Daftar aktor\n")
    for pc in c.pcs:
        pid = str(pc.get("id"))
        block = _section(c.root / f".what/{pid}/SRS-{pid}.md", "Actor Register")
        parts.append(f"\n### {pid} — {pc.get('name', '')}\n")
        parts.append(_demote(block) if block
                     else "_belum ada § Actor Register di SRS komponen ini._")

    parts.append("\n## Model domain\n")
    for pc in c.pcs:
        pid = str(pc.get("id"))
        block = _body(c.root / f".what/{pid}/03-domain/domain-model.md")
        parts.append(f"\n### {pid}\n")
        parts.append(_demote(block) if block else "_belum ada `03-domain/domain-model.md`._")

    parts.append("\n## Tiga inventaris\n")
    for kind, name in (("db", "tabel"), ("api", "endpoint"), ("screen", "layar")):
        block = _body(c.root / f".how/_platform/inventory-{kind}.md")
        parts.append(f"\n### Daftar {name} — `inventory-{kind}.md`\n")
        parts.append(_demote(block) if block else f"_belum ada `inventory-{kind}.md`._")

    return "\n".join(parts) + "\n"


def _cell(value: object, limit: int = 110) -> str:
    """Satu baris tabel, dipendekkan. Sumber panjangnya tetap di registry — ini tampilan."""
    text = " ".join(str(value or "").split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _demote(block: str, by: int = 2) -> str:
    """Turunkan tingkat heading isi yang di-inline, supaya ia tidak menabrak kerangka roll-up."""
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
    """Tabel task KANDIDAT. Satu baris per `FR`, karena itu bentuk ideal sebuah wave."""
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
             "\n**INI ESTIMASI, MENGHADAP KE DEPAN.** Tiap baris di bawah adalah task "
             "**kandidat**; wave di `waves.yaml` yang nyata. Satu baris MAY jadi satu wave, dan tiga "
             "baris bertetangga MAY digabung jadi satu — penggabungan itu keputusan manusia saat wave "
             "dibuka.\n"]
    if not have_mandays:
        parts.append("\n**Tanpa `estimate_mandays` pada satu pun `CAP`**, kolom Beban kosong dan "
                     "keluaran ini setara ukuran kelas T-shirt. Ia MUST dilaporkan sebagai itu.\n")

    parts.append("\n| Task | FR | Epic | mode | Paparan | Beban | Prioritas | Bergantung | Rilis |")
    parts.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for fr in c.frs:
        cap_id = str(fr.get("capability", ""))
        cap = cap_by_id.get(cap_id, {})
        pid = str(fr.get("component") or cap.get("component") or "")
        risk, note = risk_of.get(pid, ("—", "—"))
        exposure = "belum disetel" if risk == "—" else f"`{risk}` — {_cell(note, 60)}"
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

    # Tiga halaman untuk MANUSIA: tabel markdown sungguhan, tanpa kembar .yaml. Yang dibaca orang
    # tidak dibungkus fence yaml, dan tidak ada pembaca mesin yang menuntut versi keduanya.
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
        prog="validate", description="V1..V27 dan generator .control/generated/")
    parser.add_argument("--check", action="store_true",
                        help="periksa saja; keluar non-zero bila ada yang merah")
    parser.add_argument("--generate", action="store_true",
                        help="tulis ulang .control/generated/ (tetap memeriksa lebih dulu)")
    parser.add_argument("--root", default=".", help="akar repo (default: direktori sekarang)")
    parser.add_argument("--asof", default=None,
                        help="tanggal acuan V14, format YYYY-MM-DD (default: hari ini). "
                             "Dinyatakan eksplisit supaya run bisa diulang persis")
    args = parser.parse_args(argv)

    if not args.check and not args.generate:
        args.check = True

    root = Path(args.root).resolve()
    if not (root / ".control" / "registry").is_dir():
        print(f"validate: {root} tidak punya .control/registry/ — salah akar repo?", file=sys.stderr)
        return 2

    asof = dt.date.fromisoformat(args.asof) if args.asof else dt.date.today()
    corpus = Corpus.load(root)
    result = run_checks(corpus, asof)

    if args.generate:
        for path in generate(corpus, result):
            print(f"  tulis {path.relative_to(root).as_posix()}")

    if result.findings:
        print(f"\nMERAH — {len(result.findings)} temuan di {len(result.red)} validator\n")
        for finding in sorted(result.findings, key=lambda f: f.sort_key):
            print(f"  {finding.vid:<4} {finding.subject}: {finding.message}")
    else:
        print("\nHIJAU — tidak ada temuan")

    if result.skipped:
        print("\nDilewati:")
        for vid, why in sorted(result.skipped.items()):
            print(f"  {vid:<4} {why}")

    print(f"\nacuan waktu V14: {asof.isoformat()}")
    return 1 if result.findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

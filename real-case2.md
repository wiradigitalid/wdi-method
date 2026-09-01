 kerjakan utang dari enam jawaban tadi

Kukerjakan berurutan, mulai dari penjaga yang menunjuk ruang kosong. Baca dulu semua yang akan kusentuh.

  Searched for 3 patterns, listed 1 directory, ran 3 shell commands

BG-6 sudah ada — dan itu mengubah dua hal. Kubaca daftar tujuan lengkapnya.

  Ran 2 shell commands

Dua koreksi atas kerjaku sendiri sebelum melangkah: tujuan baru itu BG-8, bukan BG-6 — BG-6 dan BG-7 sudah ada, jadi frasa "tujuan keenam" di baris OQ-31 sudah salah bahkan saat ditulis kemarin, dan aku menyalinnya. Dan BG-7-lah yang memikul palang Snagit/Cobalt, bukan tiket 06 saja. Kucatat keduanya nanti.

  Ran 1 shell command

Sebelum menghapus apa pun — tiga berkas kode Rust menyebut web/ui. Kalau salah satunya membacanya saat runtime, penghapusan mematahkan build.

  Searched for 1 pattern

Semua rujukan itu komentar, bukan pembacaan runtime — penghapusan aman untuk cargo test. Tapi satu di antaranya menemukan sesuatu yang mengubah OQ-23.

  Searched for 1 pattern, ran 1 shell command

Semua rujukan lain adalah komentar dan catatan sejarah. Dua temuan yang mengubah rencana: kelas uji komposisi yang diminta OQ-23 sudah ada — apps/desktop/tests/test_annotation_[wiring.rs](http://wiring.rs), dibangun untuk CAP-11 di bawah BUG-72, dengan fungsi the_annotation_component_is_mounted_on_the_canvas. Dan klaim warna di [AGENTS.md](http://AGENTS.md) sudah salah: ia menyebut web/ui/src/styles/tokens.css, padahal palet yang benar-benar dikirim adalah theme.slint.

  Searched for 2 patterns

Cukup. Kueksekusi utangnya, mulai dari penghapusan web/ui dan dua penjaga yang menunjuk ke sana.

  Made 1 scratchpad edit +132, read 1 file, ran 3 shell commands

● Write(.constitution\project\[codebase-conventions-guide.md](http://codebase-conventions-guide.md))

Added 55 lines, removed 10 lines

---

status: Draft            # Article 4: Draft MAY be read as guidanc

e, MUST NOT reject a change

ratified_by: null        # the commit whose content ratifies this

file

status: Accepted         # raised 2026-09-01; see § Provenance

ratified_by: a06a8f3     # the commit whose content ratifies this

file

---

# conventions — codebase guide

**Loaded when:** writing or reviewing code.

&gt; **Born empty on purpose.** This file is filled by the first wave

's distillation — `bmad-spec`'s

&gt; [`conventions.md`](http://conventions.md) companion is promoted here before the wave clos

es.

&gt;

&gt; Writing it up front means guessing at a convention no code has y

et. It MUST NOT be filled before

&gt; code exists that ratifies it.

## Reachability — a component ships with proof that something reac

hes it

&gt; **Status.** While `draft`, its contents MAY be read as guidance

but MUST NOT be used to reject a

&gt; change. It rises to `accepted` when the first wave's distillatio

n fills it from real code, and

&gt; `ratified_by` MUST then carry the commit holding that code.

Every component that a person can see or operate MUST ship with at

 least one test asserting that

**something mounts it** and that **each of its callbacks is bound*

*, in the same change that adds it.

A test proving the component behaves correctly does not satisfy th

is and MUST NOT be offered as if it

did — the two failures look identical from a green suite.

**In Slint that is two questions, and both MUST be asked:**

- Is the component **instantiated** in `apps/desktop/ui/*.slint`?

- Is each of its callbacks **bound** by an `.on_<callback>(` in `a

pps/desktop/src/`?

Either half missing means nobody can reach it. `apps/desktop/tests

/test_annotation_[wiring.rs](http://wiring.rs)` is the

worked example and new tests SHOULD copy its shape, including two

details that are not decoration:

it collapses whitespace before matching, because `rustfmt` decides

 where a method chain breaks and a

guard a reformat turns red is a guard nobody keeps; and it strips

`//` lines before asserting a

string is **absent**, because otherwise the comment explaining a r

emoval makes the assertion fail and

the removal goes unexplained.

`V12` MUST NOT be relied on for this. It checks that an `LC` is *r

egistered*, never that it is

*reached*, and the two are independent.

**Why the tax is worth paying.** One sweep on 2026-08-23 found fou

r components built, unit-tested and

mounted nowhere — `CaptureOverlay` `BUG-4`), `MarkerLayer` (`BUG-

`),` OrphanReportVie `(`BUG-6`)

and `EmptyState` — leaving `FR-1FR-2`, `FR-8` and `FR-15` unmet

 for four waves while every test

passed. [`AGENTS.md`](http://AGENTS.md) names it this repository's signature failure.

## Colour

Colour MUST be defined in `apps/desktop/ui/theme.slint` and nowher

e else, for both themes `AD-10`).

A literal outside it is a defect, not a style choice: a literal ex

ists in exactly one theme, so it

paints correctly under one Windows setting and wrongly under the o

ther.

The theme-invariant group — the overlay scrim, the selection ring,

 the loupe grid — is the one

exception and MUST stay in that same file, each with a comment say

ing why. Those three sit over a

*screenshot* rather than over chrome, and a light scrim on a dark

capture is invisible.

Enforcement is a pair of Rust tests rather than a lint: `test_them

e_[contrast.rs](http://contrast.rs)` measures WCAG

contrast over every token in both themes, and `test_capture_intera

[ction.rs](http://ction.rs)` refuses a literal in the

overlay.

## Provenance

**Born empty on purpose, and filled on 2026-09-01 rather than at a

 wave's distillation.** The file's

own rule was that it MUST NOT be filled before code exists that ra

tifies it, which is why it stood

empty through eight waves. Both sections above are distilled from

code that already runs:

`test_annotation_[wiring.rs](http://wiring.rs)` for reachability, added by `a06a8f3` a

nd carried in `ratified_by`, and

`theme.slint` plus its two guard tests for colour.

The reachability rule is the owner's answer to `OQ-23`, taken on 2

026-09-01. It is **not** recorded as

a `DEC-`: a test convention is cheap to reverse, and this project

records a decision only when the

answer to *why is it like this* cannot be read from the code. Exte

nding [`validate.py`](http://validate.py) was considered

and rejected as the wrong address — that file lives in `.constitut

ion/method/` and is replaced in

full on every `wdi-method update`, so a check added there would no

t survive.

  Made 1 scratchpad edit +80, ran 1 shell command

Sekarang DEC- untuk jangkauan AD-9. Kubaca DEC-012 sebagai cetakan dan keadaan spine sekarang.

  Searched for 1 pattern, ran 1 shell command

● Write(.control\decisions\[DEC-014-ad-9-reaches-agent-paths-not-human-artifacts.md](http://DEC-014-ad-9-reaches-agent-paths-not-human-artifacts.md))

Wrote 124 lines to .control\decisions\[DEC-014-ad-9-reaches-agent-paths-not-human-artifacts.md](http://DEC-014-ad-9-reaches-agent-paths-not-human-artifacts.md)

---

type: decision

id: DEC-014

status: accepted

serves: [CAP-12]

touches:

  - .how/_platform/[ARCHITECTURE-SPINE.md](http://ARCHITECTURE-SPINE.md)

  - .control/questions/[answered.md](http://answered.md)

supersedes: null

superseded_by: null

… +174 lines

  Made 1 scratchpad edit +137, ran 2 shell commands

YAML pecah — :  di dalam skalar polos. Kulihat dan kubetulkan.

  Ran 4 shell commands

[codebase-stack-guide.md](http://codebase-stack-guide.md) ternyata Accepted, bukan Draft — jadi ia mengikat, dan ia menjelaskan stack Tauri+React yang DEC-007 pensiunkan. Catatan yang baru kutulis di [AGENTS.md](http://AGENTS.md) salah dan kubetulkan sekalian.

  Made 1 scratchpad edit +161, ran 4 shell commands

web-ui terdaftar sebagai container built: true — jadi penghapusannya menyentuh registry, bukan cuma peta. Kucek apa yang dikatakan validator.

  Ran 1 shell command

Tujuh berkas mengutip berkas token yang baru kuhapus. Itu tepat utang yang dibawa penghapusan itu. Kulihat cara V24 mendeteksi, lalu kubereskan satu per satu.

  Made 1 scratchpad edit +123, searched for 2 patterns, ran 4 shell commands

Papan bersih lagi: 17 = baseline. Sekarang buktikan penghapusan tak mematahkan kode.

  Ran 4 shell commands

Tebakanku terlalu kasar — itu .pyc bawaan skill, bukan yang dicek penjaga sebenarnya. Kujalankan perintah dari korpus.yml apa adanya.

  Searched for 1 pattern, ran 1 shell command

Semua penjaga lolos, validator sama persis dengan baseline, Rust dan Go hijau. Tersisa satu: peta struktur masih menjelaskan direktori yang sudah tidak ada.

  Made 1 scratchpad edit +94, ran 5 shell commands

Papan bersih, hanya DEC-014 yang belum terlacak. Kudaratkan memlog lalu commit.

  Ran 7 shell commands, wrote 1 memory

Utangnya lunas dan sudah dipush — c3a376a.

Enam utang, keenamnya dikerjakan

┌──────────────────┬─────────────────────────────────────────────────────────┐

│    Jawabanmu     │                      Yang mendarat                      │

├──────────────────┼─────────────────────────────────────────────────────────┤

│                  │ 44 berkas web/ui hilang, job CI shared-ui-check dicabut │

│ OQ-27 hapus      │  bersamanya. Tak ada Node lagi di mana pun di workspace │

│                  │  aktif                                                  │

├──────────────────┼─────────────────────────────────────────────────────────┤

│ OQ-23 konvensi   │ [codebase-conventions-guide.md](http://codebase-conventions-guide.md) terisi dan naik Draft →   │

│                  │ Accepted, ratified_by: a06a8f3                          │

├──────────────────┼─────────────────────────────────────────────────────────┤

│ OQ-33 ya, tak    │ risk_note settings mengakui tindakan yang dulu ia       │

│ terbalikkan      │ sangkal                                                 │

├──────────────────┼─────────────────────────────────────────────────────────┤

│ OQ-34 AD-9 tak   │ DEC-014 ditulis dan diterapkan; spine menyatakan        │

│ menjangkau PDF   │ batasnya sendiri. Blokir spec FR-39 tercabut            │

├──────────────────┼─────────────────────────────────────────────────────────┤

│ OQ-31 tujuan     │ BG-8 lahir; goal: CAP-12 pindah dari BG-2               │

│ baru             │                                                         │

├──────────────────┼─────────────────────────────────────────────────────────┤

│ OQ-20 palang     │ Mendarat di BG-7 di brief, bukan cuma tiket 06          │

│ dibelah          │                                                         │

└──────────────────┴─────────────────────────────────────────────────────────┘

Verifikasi: cargo fmt/clippy/test hijau (nol gagal), go test hijau, ketiga penjaga korpus.yml lolos, validator 17 temuan, identik dengan baseline.

Yang tak kau minta tapi ditemukan saat mengerjakannya

Ini bagian yang lebih berharga dari daftar di atas.

Penjaga komposisi di [AGENTS.md](http://AGENTS.md) sudah tak menunjuk kode apa pun. Ia menyuruh mencari &lt;ComponentName — JSX — di apps/desktop/src yang sudah Rust sejak DEC-007, dan di web/ui yang baru kau hapus. Satu-satunya pertahanan terhadap kegagalan tanda-tangan repo ini menunjuk ruang kosong. Untuk Slint pertanyaannya dua sekaligus: apakah komponen di-instansiasi di ui/*.slint, dan apakah tiap callback-nya diikat oleh .on_&lt;callback&gt;( di src/.

Dan konvensinya tak perlu diciptakan — contohnya sudah ada. apps/desktop/tests/test_annotation_[wiring.rs](http://wiring.rs), dibangun untuk CAP-11 di bawah BUG-72, dibuka dengan kalimat "CAP-11 is REACHABLE, not merely built". Itu yang memungkinkan panduannya diratifikasi, bukan sekadar jadi aspirasi — aturan berkas itu sendiri melarang ia diisi sebelum ada kode yang meratifikasinya.

Warna: tiga berkas menyebut berkas token di web/ui. Palet yang benar-benar dikirim adalah theme.slint, dan sudah begitu berminggu-minggu. enforced_by milik NFR-17 menyebut sebuah lint yang tak pernah menyentuh satu pun berkas Slint — itulah cara sembilan literal warna menumpuk tanpa terdeteksi sampai DEC-009 mencarinya.

[codebase-stack-guide.md](http://codebase-stack-guide.md) ternyata Accepted, jadi ia mengikat — dan ia menjelaskan Tauri v2 + React 19 + Node dengan perintah npm yang semuanya gagal enoent. Kombinasi terburuk yang ada: panduan yang mengikat dan salah. [AGENTS.md](http://AGENTS.md) sendiri mengklaim ketiga panduan proyek masih Draft; hanya [codebase-brownfield-guide.md](http://codebase-brownfield-guide.md) yang begitu.

Dua kesalahan kecil yang kuwariskan sendiri dan kukoreksi: BG-6 tak pernah kosong — baris OQ-31 menulis "tujuan keenam" dan sudah salah saat ditulis, jadi yang lahir BG-8. Dan tak pernah ada job CI bernama web-check — namanya shared-ui-check, satu dari empat; salah itu berasal dari [AGENTS.md](http://AGENTS.md) dan jawaban OQ-27 menyalinnya.

Satu yang sengaja tidak kuselesaikan

web-ui masih terdaftar sebagai container built: true dengan isi nol. Menghapus atau menurunkannya adalah tindakan wdi-blueprint intent platform, ia melayani sharing yang dibekukan DEC-005, dan OQ-22 justru meragukan permukaan itu diinginkan sama sekali. Tiga hal itu bertemu di tiket 06. [structure-codebase.md](http://structure-codebase.md) sekarang mengatakan hal itu di tempat bagian yang dulu ia muat, dan mencatat bahwa derivasi penuh masih terutang.

Papan pertanyaan sekarang: 18 terbuka (6 preferensi milikmu, 6 beku oleh DEC-005, 6 menunggu pengukuran) + 3 di [external.md](http://external.md).

---

Dikerjakan: Enam utang dari jawabanmu diselesaikan penuh — web/ui dihapus beserta job CI-nya, konvensi keterjangkauan diratifikasi, risk_note dikoreksi, DEC-014 ditulis dan diterapkan sehingga FR-39 terbuka, BG-8 lahir, palang BG-7 dibelah — ditambah enam perbaikan yang muncul saat mengerjakannya, semuanya terverifikasi hijau dan dipush di c3a376a.

Terhambat atau belum pasti: web-ui tetap terdaftar sebagai container tanpa isi; menyelesaikannya butuh wdi-blueprint atas komponen yang DEC-005 bekukan, jadi kularang diriku menyentuhnya dan kucatat sebagai drift.

Berikutnya: tiket 06 membuka tiga hal sekaligus — palang G2 yang mencabut DEC-005, enam pertanyaan beku, dan pertanyaan web-ui; atau enam preferensi murah kalau kau mau daftar pertanyaan menyusut lebih dulu.

✻ Cogitated for 20m 5s · done 9:14 AM

❯ bereskan ini: web-ui tetap terdaftar sebagai container tanpa isi; menyelesaikannya butuh /wdi-blueprint atas komponen yang DEC-005 bekukan, jadi kularang diriku menyentuhnya dan kucatat sebagai drift.

Sebelum menyentuhnya aku harus tahu apakah DEC-005 benar-benar melarang ini — registrasi container bukan FR, bukan use case, bukan UX pass. Kubaca teksnya, dan kubaca apa yang benar-benar disajikan Go service.

  Searched for 1 pattern, ran 2 shell commands

DEC-005 tidak melarang ini, dan teksnya sendiri yang mengatakannya: "This decision does not forbid a fix. It forbids new work." Dan yang lebih menentukan — Go service menyajikan halamannya sendiri: fmt.Sprintf sebuah dokumen HTML dengan &lt;pre&gt;%s&lt;/pre&gt;, Content-Type: text/html, dan nol penyajian aset statis. Registrasi container berbunyi "React + Vite single-page application, served as static assets by web-api" — dua-duanya tidak benar. Kupetakan radius ledakannya.

● Searching for 1 pattern, running 1 shell command…
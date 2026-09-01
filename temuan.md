Now landing. [design-system.md](http://design-system.md) is the one half that can land today — but its sibling links must still resolve, so I'll rewrite only the two relative paths, nothing else.

● Write(_bmad-output\ux\.working\[daratkan.py](http://daratkan.py))

Wrote 51 lines to _bmad-output\ux\.working\[daratkan.py](http://daratkan.py)

# -*- coding: utf-8 -*-

 isinya.

w/_platform/,

 di zona

pendaratan. Menulis ulang jalurnya supaya menunjuk berkas yang SAMA

rujukannya, bukan mengubah kalimatnya; membiarkannya menggantung ak

an gagal V24.

Jalur ke .what/ dan .control/ sudah benar apa adanya: .how/_platfor

_bmad-output/ux/ sama-sama dua tingkat di bawah akar.

… +48 lines

  Ran 4 shell commands

Committed as 742d3ad.

wdi-ux — laporan

Mode: run (tidak ada lari sebelumnya) · lingkup: satu inisiatif PRD, brankas-tenggat.

Sembilan pemeriksaan

┌─────┬─────────────────────────────┬────────────────────────────────────────┐

│  #  │         Pemeriksaan         │                 Hasil                  │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 1   │ Zona pendaratan             │ Lolos — lari hanya menulis ke          │

│     │                             │ _bmad-output/ux/                       │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│     │                             │ Lolos setelah perbaikan — lima aturan  │

│ 2   │ Dua dokumen, terbelah benar │ mengikat tadinya punya dua atau tiga   │

│     │                             │ rumah                                  │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 3   │ Perjalanan menunjuk UJ-N    │ Lolos — UJ-1..UJ-4 dirujuk, tidak      │

│     │                             │ diceritakan ulang                      │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 4   │ Tiap layar punya keadaan    │ Lolos, per bentuk (7) + 10 layar yang  │

│     │ kosong &amp; galat              │ ada karena ia sebuah keadaan           │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 5   │ Tiap kata benda ada di      │ GAGAL — delapan absen                  │

│     │ glosarium                   │                                        │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 6   │ Tidak ada kemampuan baru    │ GAGAL — empat alur                     │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 7   │ [ASSUMPTION] terfile        │ Lolos — nol penanda; tiga hal lain     │

│     │                             │ tetap perlu difile                     │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 8   │ Memlog di                   │ Lolos — 20 entri, --path, tidak ada    │

│     │ .control/memlog/[ux.md](http://ux.md)       │ .[memlog.md](http://memlog.md) di korpus                   │

├─────┼─────────────────────────────────────────┤

| `RuleBanner` | informasi · **peringatan** (Cek kesehatan gagal)

 | `[MISSING]` |

| `ProgressBar` | menuju target (SKP) · dua pemicu berdampingan (

servis) | `[MISS

**Implementasi seluruhnya `[MISSING]`**, dan itu satu fakta untuk

 keenam belas ba

fakta: tidak adag sudah ditulis. Rum

ahnya kelak `ui/components/`, dengan

tokennya dari `ui/theme/`.

| Elemen | Keadaan yang MUST didukung |

|---|---|

| `Button` — terisi · tonal · garis tepi · teks · merusak | norma

l · ditekan · fo

| `ListRow` | normal · ditekan · **terpilih** · nonaktif |

| `BigCard` | tetanpa Tenggat) |

| `UrgencyChip` | empat tingkat, masing-masing dengan **ikon + te

ks** |

| `SegmentedSubjrpilih · **tersembun

yi saat segmennya kosong** · digulir mendatar |

| `TypePill` | aktif · tidak aktif. **Tidak pernah** nonaktif ata

u "sudah diisi" |

| `TextField` | kosong · aktif · terisi · **galat** · terkunci |

| `Checkbox` | t + redup** (butir ya

ng tidak dimiliki) |

| `BottomSheet` lembar** (lembar tid

ak tertutup) |

| `EmptyCard` | garis putus-putus: ikon, satu kalimat, tombol ton

al |

| `FullEmptyState` | rata tengah, dengan **kontrol layar tetap ad

a** |

| `Snackbar` | d detik |

| `NavigationBar` | tiga tujuan, satu aktif |

| `TopAppBar` | penuh · menyusut saat digulir |

| `RuleBanner` | informasi · **peringatan** (Cek kesehatan gagal)

 |

| `ProgressBar` emicu berdampingan (

servis) |

Keadaan **terisi** selalu dirancang; kosong, memuat, galat, dan n

onaktif adalah y

keadaan rusak. Itu sebabnya kolom tengah menyebutnya dan bukan me

ngandaikannya.

● Update(_bmad-output\ux\[DESIGN.md](http://DESIGN.md))

Added 7 lines, removed 4 lines

| Memposisikan lapisan melayang dengan jarak tetap dari dasar bin

gkai | Ia mendarat di atas tombol pada layar berkaki lebih tinggi

 |

| Menaruh aksi mIa dijangkau dengan

menggeser genggaman, dan itu tepat saat tangan paling tidak stabi

l |

| Menghadirkan spanduk non-Tenggat di Beranda | Aturan tertua pro

duk ini runtuh, dan Beranda berhenti menjawab satu pertanyaannya

|

| Memakai warna sebagai satu-satunya pembawa makna | Pengguna but

a warna kehilangan seluruh sumbu utama aplikasi |

| Mengunci tinggda ukuran font siste

m 200% |

| Animasi masuk berjenjang, shared-element, splash beranimasi | F

rame drop pada perangkat lantai 2 GB, tanpa manfaat |

| Animasi masuk berjenjang, shared-element, splash beranimasi | F

rame drop pada panfaat. Dinyatakan d

i §13; di sini hanya diringkas |

| Menyunting `dobangkitkan; suntinga

nnya hilang pada pembangkitan berikutnya |

| Menyediakan saallpaper menghapus *

*Hutan**, dan Hutan adalah mereknya |

Dua larangan yang paling sering dilanggar **tidak** ada di tabel

ini, dengan sengaja: memakai warna

sebagai [satu-satXPERIENCE.md](http://satu-satXPERIENCE.md)`](EXPER

[IENCE.md](http://IENCE.md)) §8, dan mengunci tinggi

kartu beserta [sadesign-system.md](http://sadesign-system.md)`](d

[esign-system.md](http://esign-system.md)) §4. Ketiganya

mengikat seluruh ini — dan menyalinn

ya ke sini akan membuat empat rumah

untuk tiga aturan.

---

## 16. Yang dokumen ini sengaja tidak putuskan

● Update(_bmad-output\ux\[DESIGN.md](http://DESIGN.md))

Added 5 lines

`component:` masiComponent belum lahi

r. Kolom `LC` di §3 juga —

sebuah `LC` MUST ntainer lahir di G3.

&gt; **Yang perlu ke bukan di sini: **em

pat alur digambar oleh prototipe

&gt; tanpa satu pun `FR` yang menjanjikannya** — Kabar Tenggat, Arsip

kan, kelas akumul

&gt; gelap. Salah satunya bahkan bertentangan langsung dengan `[prd.md](http://prd.md)

` §6.2. Keempatny

&gt; mendarat sampai diputuskan.

---

## 1. Token khusu

  Ran 1 shell command

● Update(_bmad-output\ux\EX

Added 2 lines, removed 2 lines

### Tiga tujuan,

Perpindahan utamadi ikon pojok atas.

Alasan bentuknya ada di

[`DESIGN.md`](http://DESIGN.md)](DESengguna: ketiga tuju

an selalu dapat dijangkau satu tangan,

sambil berdiri, sambil memegang dokumen yang sedang disalin.

[`DESIGN.md`](http://DESIGN.md)](DESengguna: ketiga tuju

an selalu dapat dijangkau satu

tangan, sambil ben yang sedang disali

n.

| Tujuan | Menjaw

|---|---|---|

  Ran 2 shell commands

Now landing. design-syste land today — but itssibling links must still resolve, so I'll rewrite only the two relative paths, nothing else.

● Write(_bmad-output\ux\.working\[daratkan.py](http://daratkan.py))

Wrote 51 lines to _bmad-output\ux\.working\[daratkan.py](http://daratkan.py)

# -*- coding: utf-

 isinya.

w/_platform/,

 di zona

pendaratan. Menulijuk berkas yang SAMA

rujukannya, bukan mengubah kalimatnya; membiarkannya menggantung ak

an gagal V24.

Jalur ke .what/ dadanya: .how/_platfor

_bmad-output/ux/ sama-sama dua tingkat di bawah akar.

… +48 lines

  Ran 4 shell commands

Committed as 742d3ad.

wdi-ux — laporan

Mode: run (tidak ada lari sebelumnya) · lingkup: satu inisiatif PRD,

brankas-tenggat.

Sembilan pemeriksaan

┌─────┬─────────────────────────────┬────────────────────────────────────────┐

│  #  │         PemeriksaHasil                  │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 1   │ Zona pendaratan             │ Lolos — lari hanya menulis ke          │

│     │                                         │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│     │                             │ Lolos setelah perbaikan — lima aturan  │

│ 2   │ Dua dokumen, terbelah benar │ mengikat tadinya punya dua atau tiga   │

│     │                             │ rumah                                  │

├─────┼─────────────────────────────────────────┤

│ 3   │ Perjalanan menunjuk UJ-N    │ Lolos — UJ-1..UJ-4 dirujuk, tidak      │

│     │                  g                      │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 4   │ Tiap layar punya k (7) + 10 layar yang  │

│     │ kosong &amp; galat              │ ada karena ia sebuah keadaan           │

├─────┼─────────────────────────────────────────┤

│ 5   │ Tiap kata benda ada di      │ GAGAL — delapan absen                  │

│     │ glosarium                   │                                        │

├─────┼─────────────────────────────────────────┤

│ 6   │ Tidak ada kemampuan baru    │ GAGAL — empat alur                     │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 7   │ [ASSUMPTION] terfnda; tiga hal lain     │

│     │                             │ tetap perlu difile                     │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 8   │ Memlog di        , --path, tidak ada    │

│     │ .control/memlog/[ux.md](http://ux.md)       │ .[memlog.md](http://memlog.md) di korpus                   │

├─────┼─────────────────────────────┼────────────────────────────────────────┤

│ 9   │ bmad-review struc, 5 diterapkan, 2      │

│     │ prose                       │ dikembalikan ke Anda                   │

└─────┴─────────────────────────────┴────────────────────────────────────────┘

Dua kegagalan, dan keduanya bukan kecerobohan

Check 6 — empat alur digaemuan lari ini:

┌──────────────┬─────────────────────────────────────────────────────────────┐

│     Alur     │                                │

├──────────────┼─────────────────────────────────────────────────────────────┤

│              │ [Bertentad.md](http://Bertentad.md) §6.2 menaruh      │

│ Kabar        │ kabar terkurasi di luar MVP; docs/06 §6 menuliskan          │

│ Tenggat      │ loncengnya sebagai MUST. Dua dokumen yang sama-sama         │

│              │ diterima                       │

├──────────────┼─────────────────────────────────────────────────────────────┤

│              │ Nol FR. layar arsip-jenis, dan │

│ Arsipkan     │  alur ganti kewarganegaraan. Bukan hal yang sama dengan     │

│              │ kelas ar                       │

├──────────────┼─────────────────────────────────────────────────────────────┤

│ Kelas        │ Nol FR untuk bar kemajuan maupun entri berpoin. FR-16…FR-21 │

│ akumulasi    │  mengurunggal                  │

│ (SKP)        │                                                             │

├──────────────┼────────────────────────────────┤

│ Mode gelap   │ Separuh palet dibangun untuknya, ada layarnya, tidak ada FR │

│              │  maupun                        │

└──────────────┴─────────────────────────────────────────────────────────────┘

Ditandai [NEEDS CONFIRMATng, dan JANGAN ikutmendarat sampai diputuskan. Rutenya wdi-product intent update.

Check 5 — delapan kata benda di luar glosarium: Brankas · Beranda · Kabar Tenggat · Cek kesehatan · Ringkasan pagi · kelas Bebas · kelas arsip · kelas akumulasi.

Empat yang pertama sudah angnya sudah ada sebelumlari ini. Saya tidak mengarang satu pun entri — glosarium milik wdi-blueprint.

Yang mendarat, dan yang tertunda

Mendarat: [design-system.md](http://design-system.md) → .how/_platform/[design-system.md](http://design-system.md). Isinya identik;

hanya empat jalur relatiftulis ulang agar tetapmenunjuk berkas yang sama — dibiarkan menggantung, ia gagal V24. Diverifikasi keenam jalurnya ada.

Tertunda di zona pendaratan: [EXPERIENCE.md](http://EXPERIENCE.md) dan [DESIGN.md](http://DESIGN.md). Tidak ada Product

Component untuk didarati.— sebuah LC MUST menyebutcontainernya, dan container lahir di G3.

Dua temuan tinjauan yang saya kembalikan ke Anda

1. [DESIGN.md](http://DESIGN.md) §15 tumpang 4 — tapi ia satu-satunyadaftar larangan yang bisa dipindai sekali lihat.

2. [EXPERIENCE.md](http://EXPERIENCE.md) §6 mengunci kontrak keadaan pada tujuh nama bentuk visual. Itu

   persis kegagalan yang  janji membeku di sekitarsatu solusi visual. Mengunci ke tujuan permukaan lebih tahan lama, tapi lebih sulit dipakai.

Satu temuan metode

Spine [DESIGN.md](http://DESIGN.md) milik bma visual saja) bertentangandengan [ux-guide.md](http://ux-guide.md), yang menaruh layar dan keadaannya di [DESIGN.md](http://DESIGN.md) dan mengikat

registrasi LC padanya. Saatus: Accepted dan itu yang diuji check 2. Tidak saya tambal di sini — perbaikannya di paket wdi-method.

Dikerjakan: wdi-ux mode run atas 132 layar Hutan — tiga berkas ditulis, tabel layar dibangkitkan skrip dari registri dan diverifikasi 132/11, tinjauan

structure+prose dijalankaapkan, design-system.mdmendarat ke .how/_platform/, commit 742d3ad.

Terhambat/belum pasti: Dungaja — empat alur tanpa FR (satu bertentangan langsung dengan PRD) dan delapan kata benda di luar glosarium. Keduanya bukan saya yang berwenang menutup.

Berikutnya: Sebelum G2 dite untuk keempat alur,wdi-blueprint untuk glosarium, dan wdi-question untuk keadaan "sudah dilepas".

Saya sebut skillnya, tidasan Anda.

✻ Brewed for 21m 54s · done

❯ kerjakan semua poin rekomendasimu.

Semua tiga saya kerjakan. Urutannya penting: wdi-product lebih dulu, karena jawaban atas keempat alur menentukan kata benda mana yang layak masuk glosarium.

  Ran 2 shell commands

Satu hambatan nyata sebelum saya mulai: wdi-blueprint tidak bisa dijalankan

sekarang.

  Ran 1 shell command

Rantainya: glosarium → wdi-blueprint → butuh product_components → butuh wdi-init

component → butuh G2 loloarnya disebut wdi-blueprint sendiri di barisnya: rutekan istilahnya ke wdi-question. Itu yang saya pakai.

Mulai dari wdi-product.

  Ran 2 shell commands

Rantai itu memang buntu squestion dulu, supayajumlah pertanyaan sudah final saat PRD disunting sekali.

  Ran 1 shell command

Dua baris baru, OQ-010 dan OQ-011 (tertinggi yang pernah dipakai adalah OQ-009;

id tidak pernah didaur ul

● Write(_bmad-output\ux\.working\file_[oq.py](http://oq.py))

Wrote 73 lines to *bmad-output\ux\.working\[file](http://fileoq.py)*[oq.py](http://fileoq.py)

# -*- coding: utf-8 -*-

Keduanya gagal ketiga uji [`blocking.md`](http://blocking.md): tidak menyentuh uang, data

 pribadi, maupun

a; dan tidak memaksa

menulis ulang lebi, karena belum ada s

keduanya masuk kelas bawaan: [assumptions.md](http://assumptions.md), dengan jawaban yang sa

ya ambil sendiri

beserta ongkos bil

Keduanya gagal ketiga uji [`blocking.md`](http://blocking.md): tidak menyentuh uang, data

 pribadi, maupun

a; dan tidak memaksa

menulis ulang lebih dari satu Product Component, karena belum ada s

keduanya masuk kelngan jawaban yang sa

ya ambil sendiri

beserta ongkos bil

import io

… +95 lines

  Ran 1 shell command

[assumptions.md](http://assumptions.md) sekarang 7 baris terbuka — masih di bawah pagu 15. Sekarang PRD.

● Skill(bmad-prd)

Successfully loaded skill

Forwarded activation honored — intent update, {user_name} WDI, Bahasa Indonesia. Applying the five edits.

● Write(_bmad-output\ux\.working\prd_[update.py](http://update.py))

Wrote 112 lines to *bmad-output\ux\.working\[prd](http://prdupdate.py)*[update.py](http://prdupdate.py)

# -*- coding: utf-

gan, plus dua penegasan."""

import io

d = [io.open](http://io.open)(P, encoding='utf-8').read()

1. FR-53 sesudah FR-8

JANGKAR8 = (u"**Proof of done:** Menghapus Subjek tidak pernah terj

adi tanpa pengguna

ng terakhir tidak dapat dihapus.\n")

… +153 lines

  Ran 1 shell command

● Write(_bmad-output\ux\.working\addendum_[update.py](http://update.py))

Wrote 45 lines to [*bma*update.py](http://bmaupdate.py)

# -*- coding: utf-8 -*-

"""Mekanisme dan aari pass update 2026

-09-01."""

P = '.what/_prd/br

d = [io.open](http://io.open)(P, encoding='utf-8').read()

BARIS = (u"| `NFR-Skema hanya boleh me

nambah kolom yang boleh `NULL`; "

… +58 lines

  Ran 2 shell commands

Now requirements.yaml. I'll regenerate from [prd.md](http://prd.md) so it can't drift, but

preserve depends_on and t the one block notgenerated.

  Ran 1 shell command

● Write(_bmad-output\ux\.working\bangun_[registri.py](http://registri.py))

Wrote 85 lines to *bmad-output\ux\.working\[bangun](http://bangunregistri.py)*[registri.py](http://bangunregistri.py)

# -*- coding: utf-8 -*-

"""Membangkitkan ulang requirements.yaml DARI [prd.md](http://prd.md), menjaga dua ha

l yang bukan turuna

Yang dijaga: blok komentar kepala, dan `depends_on` pada tiap CAP. K

eduanya tidak punya

sumber di [prd.md](http://prd.md), jadi membangkitkan ulang tanpa menjaganya akan men

ghapusnya diam-diam

"""

import io

import re

… +94 lines

  Ran 2 shell commands

The order check I wrote wd by capability, not bynumber, so FR-53 in CAP-1 legitimately precedes FR-52 in CAP-4. Let me verify the real invariant instead.

  Ran 2 shell commands

My own bug — the UX memloon, the same YAML trap that bit the brief memlog. Fixing it through the script, not by hand.

  Ran 3 shell commands

Two are mine. V16 — artifalidator reads as one path. V24 — my own prose in [design-system.md](http://design-system.md) §1 cites web/[README.md](http://README.md) while saying it doesn't exist; the validator can't hear the negation.

  Ran 1 shell command

V16 and my V24 are gone; what remains is the same premature pair as before (54 × V2 — UCs are born at G3; 12 × V24 — method files citing G3 artifacts, which

[AGENTS.md](http://AGENTS.md) forbids patchin

Three of the four markers are now resolved, so the UX documents must be updated —

and that means re-dispatc.

● Skill(bmad-ux)

Successfully loaded skill

Update mode. Applying the

● Write(_bmad-output\ux\.working\tutup_[penanda.py](http://penanda.py))

Wrote 133 lines to *bmad-output\ux\.working\[tutup](http://tutuppenanda.py)*[penanda.py](http://tutuppenanda.py)

# -*- coding: utf-8 -*-

"""bmad-ux intent RMATION] sudah dijaw

ab, jadi penandanya dicabut."""

import io

E = '_bmad-output/

S = '_bmad-output/ux/[design-system.md](http://design-system.md)'

def sunting(path, pasangan):

… +193 lines

  Ran 2 shell commands

Let me verify the section structure — my §17 rewrite may have left a duplicate.

  Ran 2 shell commands

My §17 rewrite appended a new boundaries section instead of replacing the old one

— [DESIGN.md](http://DESIGN.md) now has §16 aemoving the duplicate Iadded and keeping the numbering contiguous.

  Ran 5 shell commands

Selesai. Dua dari tiga re terhalang urutan gerbang,bukan oleh saya.

1. wdi-product — keempat alur diputuskan

Alur: Mengarsipkan

Putusan: FR-53 di CAP-1. Dibuat bukan karena rapi, tapi karena dua aturan yang

sudah diterima bertumpu padanya tanpa janji — ganti kewarganegaraan MUST

menawarkan mengarsipkan ar titik tiga memuatnya.

Batasnya dinyatakan: FR-7 sudah diurus dan siklus lanjut · FR-8 menghapus dan

hilang · FR-53 mengarsipk

────────────────────────────────────────

Alur: Kelas akumulasi

Putusan: FR-54 di CAP-3, elkan AKUMULASI sebagai

nilai sumbu Perulangan — ia cara kelima mesin menghitung yang terutang

─────────────────────────

Alur: Tema gelap

Putusan: NFR-14, melayani BG-1. Bukan kenyamanan: NFR-4 menjanjikan kegawatan

tidak menumpang warna saja, dan ini separuh lainnya

────────────────────────────────────────

Alur: Kabar Tenggat

Putusan: Tetap di luar MVa bukan ongkos kode

melainkan perawatan konten seumur hidup produk

FR-53 sengaja saya batasi pada Tenggat, bukan Subjek — memperluasnya ke Subjek

adalah persis pertanyaan §9 larang agen putuskan.

2. wdi-question — OQ-010

OQ-010 keadaan "sudah dilepas": yang saya catat bukan jawabannya, melainkan perilaku yang berlaku selama ia belum dijawab — kendaraannya tetap menagih sampai dihapus. OQ-011 delapan kata benda tanpa entri glosarium. Keduanya di

[assumptions.md](http://assumptions.md), yang tidas terbuka, pagu 15.

3. wdi-blueprint — tidak bisa dijalankan, dan itu bukan pilihan saya

Rantainya: glosarium → wdi-blueprint → butuh product_components → butuh wdi-init component → butuh G2 lolos. Buntu sampai gerbangnya dibuka. Jalan keluarnya disebut wdi-blueprint sendiri: "MUST NOT invent a definition — cite a source, or route the term to wdi-question." Itu yang saya pakai. Definisinya ditulis di G3.

Ini pertentangan aturan yang nyata: ux-guide menuntut kata benda baru masuk glosarium "di pass yang sama", padahal lari UX milik G2 dan glosariumnya baru

bisa disentuh sesudahnya.i sini.

Yang ikut dikerjakan

- docs/06 §6 dicabut — atUST hadir di semua varian

  Beranda" akan menyuruh tombol yang tidak membukaapa pun. Kebasian yang menanggung beban.

- requirements.yaml dibangkitkan ulang dari [prd.md](http://prd.md), depends_on kesembilan CAP dan blok komentar kepala dijaga. FR 1..54 dan NFR 1..14 menerus dan unik.

- Ketiga dokumen UX kini [ign-system.md](http://ign-system.md) didaratkan

  ulang.

Dua kesalahan saya sendiri, tertangkap dan diperbaiki: memlog UX punya goal: dengan titik dua tanpa kutip yang membuat [validate.py](http://validate.py) crash; dan penulisan ulang

[DESIGN.md](http://DESIGN.md) §17 menambahkan16, sehingga sempat ada dua bagian berjudul sama.

Commit 35d046f. Validator metode — keduanya prematur seperti sebelumnya, tidak ada temuan baru.

Dikerjakan: Keempat alur diputuskan lewat bmad-prd intent update (FR-53, FR-54,

NFR-14, satu ditolak sadarkan, registri dibangkitkan ulang dengan invarian diverifikasi, docs/06 §6 diperbaiki, penanda UX ditutup, dan [design-system.md](http://design-system.md) didaratkan ulang.

Terhambat/belum pasti: Gli — wdi-blueprint terkuncisampai G2 lolos, dan itu pertentangan aturan di paket metode, bukan kelalaian di repo ini. Dua temuan tinjauan ([DESIGN.md](http://DESIGN.md) §15 tumpang tindih, [EXPERIENCE.md](http://EXPERIENCE.md) §6 terkunci pada nama bentuk visual) masih menunggu putusan Anda.

Berikutnya: G2 layak dibuka — [prd.md](http://prd.md) dan [EXPERIENCE.md](http://EXPERIENCE.md) keduanya ada dan sudah ditinjau. Sesudah gerbangmponent, lalu wdi-blueprint yang sekaligus menutup OQ-011.
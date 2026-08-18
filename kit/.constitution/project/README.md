---
status: Accepted
scope: project-room
---

# `.constitution/project/` — kamar aturan khusus produk ini

**Folder ini milik produk, bukan milik metode.** Ia disemai sekali saat install, dan sesudah itu
`wdi-method update` **tidak pernah** menulis ke dalamnya. `wdi-method promote` **melewatinya**
seluruhnya, jadi apa pun yang Anda tulis di sini tidak mungkin terbit ke paket publik.

Satu-satunya pengecualian adalah berkas ini: README kamar dikarang di paket dan tidak pernah pulang
lewat `promote`. Menyuntingnya MAY dilakukan, tetapi suntingannya akan hilang pada install berikutnya
di repo lain — jadi aturan produk Anda MUST ditulis sebagai berkas **lain** di folder ini.

## Apa yang masuk ke sini

Aturan normatif yang berlaku **hanya di produk ini** dan bukan konvensi kode:

- kebijakan review yang diminta klien
- aturan proses yang lahir dari kontrak
- kebijakan penamaan atau bahasa yang beda dari default metode
- larangan atau kewajiban khusus domain ini

## Apa yang TIDAK masuk ke sini

| Yang | Rumahnya |
|---|---|
| Nama produk atau klien | `.control/registry/index.yaml` → `product:` |
| Konvensi kode, stack, pola brownfield | `.constitution/codebase/*-guide.md` — sudah dilindungi sesudah `Accepted` |
| Lingkup, kepemilikan metode, checklist repo | `constitution.md` Article 1, 2, 5 — sudah dilindungi |
| Instruksi agent khusus produk | `AGENTS.md`, **di luar** blok bertanda `wdi-method` |
| Override BMad khusus produk | `_bmad/custom/*.user.toml` |
| Keadaan, janji, rancangan | `.control/` · `.what/` · `.how/` |

**Sebuah aturan yang generic MUST NOT dipindahkan ke sini.** Kalau ia berlaku di proyek mana pun, ia
milik paket — perbaiki di sana, lalu `promote`. Kamar ini untuk yang **tidak** generic, dan memakainya
sebagai jalan memintas paket adalah cara metode berhenti generic tanpa ada yang memutuskannya.

## Bentuk berkasnya

Frontmatter wajib, dan `V27` memeriksanya:

```yaml
---
scope: project              # WAJIB, dan nilainya persis ini
purpose: ""                 # WAJIB, satu baris: aturan ini menjaga apa
overrides: null             # opsional; path berkas kit yang ia persempit atau bantah
decision: null              # WAJIB bila `overrides:` terisi — DEC- yang memutuskannya
---
```

- Sebuah berkas di sini MAY **mempersempit** atau **menambah** aturan generic tanpa `overrides:`.
- Untuk **membantah** aturan generic ia MUST menyebutnya di `overrides:` dan membawa `decision:`.
  Tanpa keduanya, kamar ini jadi tempat aturan generic dilanggar tanpa jejak — dan itu justru yang
  membuat sebuah metode berhenti dapat dipercaya di repo berikutnya.
- `overrides:` yang menunjuk berkas yang tidak ada adalah temuan, bukan salah tulis: ia berarti
  aturan yang dibantah sudah hilang, dan pembantahannya mungkin sudah tidak punya alasan.

## Kenapa berkas utuh, bukan blok bertanda di dalam guide

`AGENTS.md` memakai blok bertanda karena ia **satu** berkas. `.constitution/` punya lima puluhan, dan
blok bertanda di dalamnya menuntut `update` melakukan operasi bedah di tiap berkas — satu marker yang
rusak berarti aturan produk terhapus, atau aturan generic membeku selamanya.

Berkas utuh di kamar sendiri menghindari keduanya, dan ia membuat aturan produk **terbaca di satu
tempat** alih-alih tersebar di dalam lima puluh berkas milik orang lain.

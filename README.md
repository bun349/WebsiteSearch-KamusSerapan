# Kamus Kata Serapan

Aplikasi pencarian etimologi kata serapan dalam Bahasa Indonesia, dibangun menggunakan teknologi Semantic Web (RDF/SPARQL) dengan Apache Jena Fuseki sebagai backend dan Streamlit sebagai antarmuka pengguna.

---

## Daftar Isi

- [Prasyarat Sistem](#prasyarat-sistem)
- [Panduan Instalasi](#panduan-instalasi)
- [Panduan Penggunaan](#panduan-penggunaan)
- [Contoh Hasil](#contoh-hasil)
- [Troubleshooting](#troubleshooting)

---

## Prasyarat Sistem

Sebelum memulai, pastikan perangkat kamu sudah terinstal perangkat lunak berikut:

- **Python** (versi 3.8 atau lebih baru)
- **Java (JRE atau JDK)** — wajib terinstal karena Apache Jena Fuseki berjalan di atas Java
- **Git** — untuk mengunduh repositori proyek

---

##  Panduan Instalasi

### Langkah 1: Mengunduh Repositori Proyek (GitHub)

Unduh seluruh file proyek aplikasi (termasuk source code Streamlit dan file data RDF/Turtle) dari GitHub ke komputer lokal kamu.

1. Buka Terminal atau Command Prompt (CMD).
2. Jalankan perintah berikut:
```bash
   git clone https://github.com/bun349/WebsiteSearch-KamusSerapan.git
```
3. Masuk ke direktori proyek:
```bash
   cd C:\ProyekSemweb-Kelompok6
```

### Langkah 2: Mengatur Lingkungan Python (Frontend)

Selanjutnya, kita akan menginstal semua library Python yang dibutuhkan oleh aplikasi Streamlit menggunakan file `requirements.txt` yang sudah disediakan.

1. Pastikan kamu berada di dalam direktori folder proyek.
2. Disarankan untuk menggunakan virtual environment agar library proyek ini tidak bentrok dengan proyek Python kamu yang lain:

   **Windows:**
```bash
   python -m venv env
   env\Scripts\activate
```

   **Mac/Linux:**
```bash
   python3 -m venv env
   source env/bin/activate
```
3. Setelah virtual environment aktif (ditandai dengan tulisan `(env)` di terminal), jalankan perintah instalasi berikut:
```bash
   pip install -r requirements.txt
```
   Tunggu hingga proses unduhan dan instalasi ketiga library (Streamlit, SPARQLWrapper, dan Pandas) selesai.

### Langkah 3: Menginstal & Menjalankan Apache Jena Fuseki (Backend)

Apache Jena Fuseki digunakan sebagai SPARQL endpoint untuk menyimpan dan melakukan query pada data ontologi kita.

1. Unduh Apache Jena Fuseki dari situs resmi Apache Jena. Pilih versi binary (biasanya berformat `.zip` atau `.tar.gz`).
2. Ekstrak file yang sudah diunduh ke folder pilihan kamu.
3. Buka Terminal/CMD baru, lalu arahkan (navigate) ke dalam folder Fuseki yang baru saja diekstrak.
4. Jalankan server Fuseki dengan perintah berikut:

   **Windows:**
```bash
   fuseki-server.bat
```

   **Mac/Linux:**
```bash
   ./fuseki-server
```
5. Biarkan terminal ini tetap terbuka. Server sekarang berjalan di `http://localhost:3030`.

### Langkah 4: Konfigurasi Dataset di Fuseki

Setelah server berjalan, kita perlu membuat database khusus untuk menampung data kamus serapan.

1. Buka browser (Chrome/Firefox/dll) dan akses antarmuka Fuseki di: `http://localhost:3030`
2. Pada halaman utama, klik menu **Manage datasets**.
3. Klik tombol **add new dataset**.
4. Pada kolom dataset name, ketikkan persis seperti ini: `kamus-serapan`
   >  Pastikan huruf kecil semua dan menggunakan strip, karena aplikasi akan memanggil nama ini.
5. Pada pilihan Dataset type, pilih **Persistent (TDB2)** agar data tidak hilang ketika server dimatikan.
6. Klik **create dataset**.

### Langkah 5: Mengunggah Data RDF ke Fuseki

Sekarang kita akan memasukkan data etimologi dari GitHub ke dalam dataset yang baru dibuat.

1. Masih di halaman **Manage datasets**, temukan dataset `kamus-serapan` yang baru saja kamu buat, lalu klik tombol **upload data** di sebelahnya.
2. Klik **select files**.
3. Cari dan pilih file data RDF/Turtle (biasanya berakhiran `.ttl` atau `.rdf`) yang ada di dalam folder proyek yang kamu unduh pada Langkah 1.
4. Klik **upload all**. Tunggu hingga muncul notifikasi sukses.

### Langkah 6: Menjalankan Aplikasi Streamlit

Infrastruktur backend sudah siap, dan data sudah tersedia. Sekarang bisa menjalankan aplikasi Streamlit.

1. Kembali ke terminal/CMD pertama (yang berada di dalam folder proyek Python kamu).
2. Jalankan aplikasi dengan perintah:
```bash
   streamlit run app.py
```
3. Secara otomatis, browser akan membuka tab baru dan menampilkan aplikasi Kamus Kata Serapan.

---

## Panduan Penggunaan Aplikasi

Sebelum menjalankan dan mengeksplorasi aplikasi, pastikan Anda telah menyelesaikan tahap instalasi awal. Berikut adalah daftar periksa (checklist) prasyarat sistem Anda:

- [ ] **Unduh File Proyek (GitHub)** — Merujuk pada panduan instalasi sebelumnya, pastikan Anda sudah mengunduh (clone/download) seluruh data proyek dari repositori GitHub, terutama file data RDF/ontologi yang akan digunakan.
- [ ] **Aktifkan Apache Jena Fuseki** — Pastikan server backend Apache Jena Fuseki sudah aktif dan berjalan di komputer (lokal) Anda.
- [ ] **Siapkan Dataset** — Pastikan Anda telah membuat dataset baru di dalam dashboard Fuseki dengan nama persis `kamus-serapan`, dan telah mengunggah (upload) file data dari GitHub ke dalam dataset tersebut sesuai instruksi instalasi.
- [ ] **Verifikasi Endpoint** — Aplikasi Streamlit ini akan mencoba terhubung secara otomatis ke endpoint berikut: `http://localhost:3030/kamus-serapan/query`.

> **Catatan:** Jika server Fuseki dalam keadaan mati, nama dataset salah ketik, atau data dari GitHub belum diunggah, aplikasi akan menampilkan pesan error **"Gagal terhubung ke SPARQL Endpoint"**.

Berikut ini panduan untuk menggunakan aplikasi ini berdasarkan fiturnya:

### Fitur 1: Pencarian Cepat (Tab "Pencarian Kata")

Fitur ini dirancang untuk pengguna umum yang ingin mencari informasi etimologi suatu kata secara instan tanpa perlu memahami bahasa query.

**Cara Penggunaan:**

1. Buka aplikasi di browser Anda. Secara bawaan, Anda akan langsung berada di tab **Pencarian Kata**.
2. Temukan kolom teks pencarian yang bertuliskan *"Ketik kata serapan… contoh: abdomen, kaisar, gratis"*.
3. Masukkan kata kunci yang ingin Anda cari (misalnya: `absen`).
4. Klik tombol emas bertuliskan **Cari Kata**.
5. Tunggu proses pemuatan selesai (ditandai dengan indikator spinner).
6. Hasil akan ditampilkan dalam bentuk tabel yang memuat empat kolom informasi: **Kata Serapan**, **Bahasa Sumber**, **Bentuk Asli**, dan **Makna**.

> **Catatan:** Jika kata yang Anda cari tidak ada di dalam database Fuseki, aplikasi akan memunculkan pesan peringatan berwarna biru (Info) bahwa data tidak ditemukan.

### Fitur 2: Eksekusi Manual (Tab "SPARQL Query")

Fitur ini ditujukan untuk developer atau pengguna tingkat lanjut yang memahami bahasa query Semantic Web (SPARQL) dan ingin mengekstrak data spesifik dari database.

**Cara Penggunaan:**

1. Klik tab **SPARQL Query** di bagian atas halaman aplikasi.
2. Anda akan melihat sebuah area teks berukuran besar (editor) yang sudah terisi dengan query bawaan (default). Query default ini berfungsi untuk menampilkan 10 kata serapan pertama beserta asal bahasa dan bentuk aslinya.
3. Anda dapat menghapus atau memodifikasi query di dalam kotak tersebut sesuai kebutuhan eksplorasi Anda.
4. Setelah query siap, klik tombol **Jalankan Query**.
5. Hasil ekstraksi data mentah (raw data) akan secara otomatis diubah menjadi format tabel yang mudah dibaca.

> **Catatan:** Pastikan penulisan syntax SPARQL (termasuk penulisan PREFIX) sudah tepat. Jika query valid tetapi hasilnya kosong, aplikasi akan menampilkan pesan peringatan berwarna kuning.

---

## Contoh Hasil

### 1. Tampilan Awal Aplikasi

Tampilan default ketika aplikasi pertama kali dibuka, langsung berada di tab **Pencarian Kata**.

![Tampilan Awal Aplikasi](docs/screenshots/01-tampilan-awal.png)

### 2. Pencarian Kata — Hasil Ditemukan

Contoh pencarian kata `"absen"` pada tab **Pencarian Kata**. Hasil ditampilkan dalam tabel berisi empat kolom: Kata Serapan, Bahasa Sumber, Bentuk Asli, dan Makna.

![Hasil Pencarian Kata Absen](docs/screenshots/02-hasil-pencarian-absen.png)

| Kata Serapan | Bahasa Sumber | Bentuk Asli | Makna |
|---|---|---|---|
| absen | Belanda | absent | tidak hadir |

### 3. Pencarian Kata — Data Tidak Ditemukan

Contoh ketika kata yang dicari tidak terdapat di dalam database, aplikasi menampilkan pesan info berwarna biru.

![Data Tidak Ditemukan](docs/screenshots/03-data-tidak-ditemukan.png)

> **Info:** Kata yang Anda cari tidak ditemukan dalam database.

### 4. Eksekusi Manual — Tab SPARQL Query

Tampilan editor query SPARQL dengan query default yang menampilkan 10 kata serapan pertama.

![Editor SPARQL Query](docs/screenshots/04-editor-sparql.png)

```sparql
PREFIX ks: <http://contoh.org/kamus-serapan#>
SELECT ?kata ?bahasaSumber ?bentukAsli
WHERE {
  ?kata ks:bahasaSumber ?bahasaSumber ;
        ks:bentukAsli ?bentukAsli .
}
LIMIT 10
```

### 5. Hasil Eksekusi Query SPARQL

Hasil dari query yang dijalankan, ditampilkan dalam format tabel.

![Hasil Query SPARQL](docs/screenshots/05-hasil-query-sparql.png)

### 6. Query Kosong / Tidak Valid

Contoh tampilan peringatan berwarna kuning saat query valid secara syntax tetapi tidak menghasilkan data.

![Query Hasil Kosong](docs/screenshots/06-query-kosong.png)

> **Peringatan:** Query berhasil dijalankan, namun tidak ada data yang sesuai.

---

## Troubleshooting

| Masalah | Kemungkinan Sebab | Solusi |
|---|---|---|
| "Gagal terhubung ke SPARQL Endpoint" | Server Fuseki tidak aktif | Pastikan `fuseki-server` sedang berjalan di `http://localhost:3030` |
| Error nama dataset | Nama dataset salah ketik | Pastikan nama dataset persis `kamus-serapan` (huruf kecil, pakai strip) |
| Hasil pencarian selalu kosong | Data RDF belum diunggah | Ulangi Langkah 5: upload file `.ttl`/`.rdf` ke dataset |
| `streamlit: command not found` | Virtual environment belum aktif / library belum terinstal | Aktifkan venv, lalu jalankan ulang `pip install -r requirements.txt` |

---

# SIPUSTAKA

**Sistem Informasi Perpustakaan Kampus Berbasis Rekomendasi Buku**

Tugas Besar Mata Kuliah Rekayasa Perangkat Lunak
Dosen Pengampu: Bapak Muhammad Soleh, S.Kom., M.T.
Program Studi Sains Data, Fakultas Sains dan Teknologi
UIN K.H. Abdurrahman Wahid Pekalongan, 2026

## Deskripsi

SIPUSTAKA adalah sistem informasi perpustakaan kampus yang mengintegrasikan pengelolaan data buku, anggota, peminjaman, pengembalian, reservasi, denda, serta laporan dan statistik. Sistem juga memanfaatkan riwayat peminjaman dan aktivitas anggota untuk memberikan rekomendasi buku.

## Anggota Kelompok 6 (Kelas A)

| Nama | NIM | Peran Utama |
|---|---|---|
| Nabil Surya Al Hakim | 60124044 | UI/UX, repo, Login, Cari Buku |
| Devita Rizqi Maulida | 60124007 | Database, Kelola Buku, Kelola Anggota, Laporan |
| Amalia Putri Setya Aryana | 60124040 | Peminjaman, Pengembalian, Denda |
| Nirma Ayu Suryaningtyas | 60124017 | Reservasi, Model Rekomendasi |

## Aktor Sistem

Anggota (Mahasiswa/Dosen), Pustakawan, Administrator, Kepala Perpustakaan, dan Layanan Notifikasi.

## Fitur Utama

| Kode | Fitur |
|---|---|
| FR001 | Autentikasi pengguna dan hak akses |
| FR002 | Pengelolaan data buku |
| FR003 | Pencarian dan informasi ketersediaan buku |
| FR004 | Pengelolaan data anggota |
| FR005 | Peminjaman buku |
| FR006 | Pengembalian buku |
| FR007 | Reservasi buku |
| FR008 | Pengelolaan denda |
| FR009 | Rekomendasi buku |
| FR010 | Laporan dan statistik perpustakaan |

## Tech Stack

- **Backend:** Python, Django
- **Database:** MySQL
- **Model rekomendasi:** pandas, scikit-learn
- **Frontend:** Template Django, Bootstrap 5
- **Desain:** Figma
- **Versi kode:** Git dan GitHub

## Struktur Folder

```
Sipustaka/
├── app/        kode aplikasi (project Django)
├── database/   skema SQL, ERD, dataset
├── design/     aset dan export desain Figma
├── docs/       diagram dan laporan
├── ml/         model rekomendasi
└── README.md
```

## Cara Menjalankan

Bagian ini akan dilengkapi setelah project Django dibuat.

## Aturan Kerja Tim

- Branch `main` hanya untuk kode yang stabil, jangan push langsung.
- Buat branch per fitur, contoh: `fitur/login`, `fitur/cari-buku`, `fitur/peminjaman`.
- Format commit: `feat:` fitur baru, `fix:` perbaikan, `docs:` dokumentasi, `chore:` lainnya.
- Sebelum mulai kerja jalankan `git pull origin main`.
- Setiap perubahan masuk lewat Pull Request dan dicek minimal satu anggota lain.
- Jangan upload file `.env` atau password database.
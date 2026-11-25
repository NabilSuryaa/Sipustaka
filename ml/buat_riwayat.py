"""Membuat riwayat peminjaman simulasi dari data katalog dan pengunjung SIPUSTAKA.

Input  (dari branch devita/buku-anggota, folder data/):
  database buku SIPUSTAKA.csv
  database pengunjung SIPUSTAKA.csv
Output (folder data/):
  buku_bersih.csv          katalog bersih dengan id_buku unik
  riwayat_peminjaman.csv   id_anggota, id_buku, tanggal_pinjam

Cara simulasi (dicatat juga di laporan):
  - id_anggota = kolom "No" pada data pengunjung.
  - Jumlah peminjaman anggota = kolom "Pinjaman", dibatasi maksimal 15.
  - 80% buku diambil dari genre favorit anggota (kolom "Gendre"), 20% dari seluruh katalog.
  - Buku yang lebih sering dipinjam (times_borrowed) lebih besar peluang terpilih.
  - Tanggal pinjam acak antara 2025-01-01 dan 2026-11-20.
Data ini hasil simulasi, bukan catatan peminjaman asli.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
MAKS_PINJAMAN = 15
PERSEN_FAVORIT = 0.8
TANGGAL_AWAL, TANGGAL_AKHIR = "2025-01-01", "2026-11-20"

FILE_BUKU = "database buku SIPUSTAKA.csv"
FILE_PENGUNJUNG = "database pengunjung SIPUSTAKA.csv"

# Pemetaan label "Gendre" anggota ke kondisi pada katalog (genre / section / subjects)
PEMETAAN = {
    "romance": {"genre": ["Romance"]},
    "fantasy": {"genre": ["Fantasy"]},
    "comedi": {"genre": ["Comedy", "Satire"]},
    "sains": {"genre": ["Science", "Science Fiction"]},
    "math": {"genre": ["Science"], "subjects": r"mathemat|geometry|algebra|calculus|statistic"},
    "edukasi": {"genre": ["Philosophy", "Economics & Business", "Self-Help",
                          "Dictionaries & Encyclopedias", "History"],
                "section": ["Reference"], "subjects": r"textbook|education"},
    "cerita rakyat": {"subjects": r"folk|fairy|legend|myth|fable"},
}


def perbaiki_teks(s):
    """Perbaiki karakter rusak (mojibake) seperti 'GrÃƒÂ¨ce' menjadi 'Grèce'."""
    if not isinstance(s, str):
        return s
    for _ in range(2):
        try:
            s = s.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
    return s


def bersihkan_katalog(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(subset=["title"])
    df["title"] = df["title"].astype(str).str.strip()
    df = df[df["title"] != ""].drop_duplicates(subset="title").reset_index(drop=True)

    df["genre"] = df["genre"].fillna("Unknown")
    df["section"] = df["section"].fillna("Unknown")
    df["author"] = df["author"].fillna("Unknown")
    df["subjects"] = df["subjects"].map(perbaiki_teks).fillna("").str.slice(0, 300)
    df["times_borrowed"] = pd.to_numeric(df["times_borrowed"], errors="coerce").fillna(0)
    df["rating_angka"] = pd.to_numeric(
        df["rating"].astype(str).str.extract(r"([\d.]+) out of")[0], errors="coerce")

    df.insert(0, "id_buku", np.arange(1, len(df) + 1))
    return df.rename(columns={"title": "judul", "genre": "kategori", "author": "penulis"})[
        ["id_buku", "judul", "penulis", "kategori", "section", "subjects",
         "times_borrowed", "rating_angka", "year_published"]]


def kolam_buku(buku: pd.DataFrame) -> dict:
    """Daftar id_buku yang cocok untuk tiap label Gendre."""
    kolam = {}
    for label, aturan in PEMETAAN.items():
        cocok = pd.Series(False, index=buku.index)
        if "genre" in aturan:
            cocok |= buku["kategori"].isin(aturan["genre"])
        if "section" in aturan:
            cocok |= buku["section"].isin(aturan["section"])
        if "subjects" in aturan:
            cocok |= buku["subjects"].str.lower().str.contains(aturan["subjects"], regex=True)
        kolam[label] = buku.index[cocok].to_numpy()
    return kolam


def buat_riwayat(buku: pd.DataFrame, anggota: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    bobot_semua = np.log1p(buku["times_borrowed"].to_numpy()) + 1
    kolam = kolam_buku(buku)
    tanggal = pd.date_range(TANGGAL_AWAL, TANGGAL_AKHIR)

    baris = []
    for _, a in anggota.iterrows():
        jumlah = int(min(a["Pinjaman"], MAKS_PINJAMAN))
        if jumlah == 0:
            continue
        favorit = kolam.get(str(a["Gendre"]).strip().lower(), np.array([], dtype=int))
        terpilih = set()
        while len(terpilih) < jumlah:
            if len(favorit) > 0 and rng.random() < PERSEN_FAVORIT:
                sumber = favorit
            else:
                sumber = np.arange(len(buku))
            bobot = bobot_semua[sumber] / bobot_semua[sumber].sum()
            terpilih.add(int(rng.choice(sumber, p=bobot)))
        tgl = np.sort(rng.choice(tanggal, size=jumlah, replace=False))
        for idx, t in zip(terpilih, tgl):
            baris.append({"id_anggota": int(a["No"]),
                          "id_buku": int(buku.loc[idx, "id_buku"]),
                          "tanggal_pinjam": pd.Timestamp(t).strftime("%Y-%m-%d")})
    return pd.DataFrame(baris)


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "data"
    buku = bersihkan_katalog(pd.read_csv(folder / FILE_BUKU, encoding="utf-8-sig"))
    anggota = pd.read_csv(folder / FILE_PENGUNJUNG, encoding="utf-8-sig")

    riwayat = buat_riwayat(buku, anggota)
    buku.to_csv(folder / "buku_bersih.csv", index=False, encoding="utf-8")
    riwayat.to_csv(folder / "riwayat_peminjaman.csv", index=False)

    print(f"Katalog bersih : {len(buku)} buku")
    print(f"Riwayat        : {len(riwayat)} baris, {riwayat['id_anggota'].nunique()} anggota")
    print("Ukuran kolam genre:", {k: len(v) for k, v in kolam_buku(buku).items()})

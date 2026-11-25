"""Preprocessing data katalog buku dan riwayat peminjaman (FR009).

Input berasal dari buat_riwayat.py:
    data/buku_bersih.csv        id_buku, judul, kategori (+ kolom lain, opsional)
    data/riwayat_peminjaman.csv id_anggota, id_buku, tanggal_pinjam
"""
import re
import pandas as pd

KOLOM_BUKU = ["id_buku", "judul", "kategori"]
KOLOM_PINJAM = ["id_anggota", "id_buku", "tanggal_pinjam"]

def _cek_kolom(df: pd.DataFrame, kolom: list, nama: str) -> None:
    hilang = [k for k in kolom if k not in df.columns]
    if hilang:
        raise ValueError(f"Kolom {hilang} tidak ada di data {nama}")

def _token_kategori(teks: str) -> str:
    """'Crime/Thriller' -> 'crimethriller' agar satu genre menjadi satu kata di TF-IDF."""
    return re.sub(r"[^a-z]", "", teks.lower())

def bersihkan_buku(df: pd.DataFrame) -> pd.DataFrame:
    """Hapus duplikat, tangani data kosong, dan buat kolom teks untuk TF-IDF."""
    _cek_kolom(df, KOLOM_BUKU, "buku")
    df = df.drop_duplicates(subset="id_buku").copy()
    for kol in ["judul", "kategori"]:
        df[kol] = df[kol].fillna("").astype(str).str.strip()
    df = df[df["judul"] != ""]
    token = df["kategori"].map(_token_kategori)
    # Genre ditulis dua kali agar bobotnya lebih besar daripada kata di judul
    df["teks"] = (df["judul"].str.lower() + " " + token + " " + token).str.strip()
    return df.reset_index(drop=True)
 
 
def bersihkan_peminjaman(df: pd.DataFrame, buku: pd.DataFrame) -> pd.DataFrame:
    """Hapus data kosong dan duplikat, serta buang buku yang tidak ada di katalog."""
    _cek_kolom(df, KOLOM_PINJAM, "peminjaman")
    df = df.dropna(subset=["id_anggota", "id_buku"]).copy()
    df["tanggal_pinjam"] = pd.to_datetime(df["tanggal_pinjam"], errors="coerce")
    df = df.drop_duplicates(subset=["id_anggota", "id_buku"])
    df = df[df["id_buku"].isin(buku["id_buku"])]
    return df.reset_index(drop=True)
 
 
def load_data(path_buku, path_pinjam):
    buku = bersihkan_buku(pd.read_csv(path_buku))
    pinjam = bersihkan_peminjaman(pd.read_csv(path_pinjam), buku)
    return buku, pinjam
 

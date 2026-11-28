"""Unit Testing FR009 Rekomendasi Buku: data_prep.py dan model.py (data kecil, hasil pasti)."""

import pandas as pd
import pytest

from data_prep import bersihkan_buku, bersihkan_peminjaman
from model import RecommendationService

@pytest.fixture
def buku():
    return bersihkan_buku(pd.DataFrame({
        "id_buku": [1, 2, 3, 4, 5, 6],
        "judul": ["Pemrograman Python Dasar", "Python untuk Analisis Data", "Basis Data MySQL", 
                  "Sejarah Kerajaan Majapahit", "Sejarah Kemerdekaan Indonesia", "Novel Laskar Pelangi"],

        "kategori": ["Komputer", "Komputer", "Komputer", "Sejarah", "Sejarah", "Fiksi"],
         "times_borrowed": [10, 5, 1, 50, 2, 3],
    }))

@pytest.fixture
def pinjam(buku):
    return bersihkan_peminjaman(pd.DataFrame({
        "id_anggota": [1, 2],
        "id_buku": [1, 4],
        "tanggal_pinjam": ["2026-01-01", "2026-01-02"],
    }), buku)

@pytest.fixture
def svc(buku, pinjam):
    return RecommendationService().fit(buku, pinjam)

# --- data_prep ---
def test_u01_buku_duplikat_dan_judul_kosong_dibuang():
    """UT-01: id_buku ganda dan judul kosong dibuang saat preprocessinng katalog."""
    df = pd.DataFrame({"id_buku": [1, 1, 2, 3], "judul": ["A", "A", "", None],
                       "kategori": ["X", "X", "X", "X"]})
    hasil = bersihkan_buku(df)
    assert list(hasil["id_buku"]) == [1]

def test_u02_kolom_wajib_hilang_menimbulkan_error():
    """UT-02: kolom wajib tidak ada -> ValueError dengan pesan jelas."""
    with pytest.raises(ValueError):
        bersihkan_buku(pd.DataFrame({"id_buku": [1], "judul": ["A"]}))

def test_u03_peminjaman_ganda_dan_buku_tak_dikenal_dibuang(buku):
    """UT-03: pinjaman ganda dan buku yang tidak ada di katalog dibuang."""
    df = pd.DataFrame({"id_anggota":  [1, 1, 1], "id_buku": [1, 1, 999],
                       "tanggal_pinjam": ["2026-01-01"] * 3})
    hasil = bersihkan_peminjaman(df, buku)
    assert len(hasil) == 1 and hasil.loc[0, "id_buku"] == 1

#--- RecommendationService ---
def test_u04_rekomendasi_tidak_memuat_buku_yang_sudah_dipinjam(svc):
    """UT-04: buku yang sudah dipinjam anggota tidak direkomendasikan lagi."""
    hasil = svc.rekomendasi(1, n=5)
    assert 1 not in set(hasil["id_buku"])

def test_u05_jumlah_rekomendasi_sesuai_n(svc):
    """UT-05: jumlah baris hasil sama dengan n."""
    assert len(svc.rekomendasi(1, n=3)) == 3

def test_u06_rekomendasi_mengikuti_genre_minat(svc):
    """UT-06: anggota yang meminjam buku komputer mendapat buku komputer di urutan teratas."""
    hasil = svc.rekomendasi(1, n=2)
    assert set(hasil["kategori"]) == {"Komputer"}

def test_u07_anggota_tanpa_riwayat_mendapat_buku_populer(svc):
    """UT-07 (skenario A1): tanpa riwayat -> buku paling sering dipinjam (id 4, 50 kali)."""
    hasil = svc.rekomendasi(999, n=3)
    assert hasil.loc[0, "id_buku"] == 4

def test_u08_buku_populer_mengabaikan_buku_pada_daftar_kecuali(svc):
    """UT-08: buku populer tidak memuat buku pada parameter kecuali."""
    hasil = svc.buku_populer(3, kecuali=[4])
    assert 4 not in set(hasil["id_buku"])

def test_u09_buku_serupa_tidak_memuat_buku_itu_sendiri(svc):
    """UT-09: buku serupa tidak memuat buku acuan dan yang teratas bergenre sama."""
    hasil = svc.buku_serupa(1, n=2)
    assert 1 not in set(hasil["id_buku"])
    assert hasil.loc[0, "kategori"] == "Komputer"

def test_u10_buku_serupa_id_tidak_ada_menimbulkan_error(svc):
    """UT-10: id_buku yang tidak ada -> ValueError."""
    with pytest.raises(ValueError):
        svc.buku_serupa(12345)
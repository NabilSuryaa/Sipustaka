"""Balck-Box Testing FR009: endpoint API rekomendasi (hanya melihat masukan dan keluaran).
"""

import pytest
from django.test import Client

@pytest.fixture(scope="module")
def client():
    return Client()

def test_bb01_rekomendasi_anggota_dengan_riwayat(client):
    """BB-01: GET /api/rekomendasi/1?n=3 -> 200, sumber 'riwayat', 3 buku."""
    r = client.get("/api/rekomendasi/1?n=3")
    d = r.json()
    assert r.status_code == 200
    assert d["sumber"] == "riwayat" and len(d["rekomendasi"]) == 3

def test_bb02_isi_setiap_rekomendasi_lengkap(client):
    """BB-02: tiap rekomendasi memuat id_buku, judul, kategori, skor."""
    item = client.get("/api/rekomendasi/1").json()["rekomendasi"][0]
    assert {"id_buku", "judul", "kategori", "skor"} <= set(item)

def test_bb03_anggota_tanpa_riwayat_memakai_fallback(client):
    """BB-03 (A1): anggota tidak dikenal -> 200, sumber 'populer'."""
    r = client.get("/api/rekomendasi/99999")
    assert r.status_code == 200 and r.json()["sumber"] == "populer"

def test_bb04_n_dibatasi_maksimal_20(client):
    """BB-04: n=500 -> hanya 20 hasil."""
    assert len(client.get("/api/rekomendasi/1?n=500").json()["rekomendasi"]) == 20

def test_bb05_n_nol_dibulatkan_ke_satu(client):
    """BB-05:   n=0 -> minimal 1 hasil."""
    assert len(client.get("/api/rekomendasi/1?n=0").json()["rekomendasi"]) == 1

def test_bb06_buku_serupa_valid(client):
    """BB-06: GET /api/buku-serupa/1 -> 200 dan tidak memuat buku itu sendiri."""
    r = client.get("/api/buku-serupa/1")
    ids = {x["id_buku"] for x in r.json()["serupa"]}
    assert r.status_code == 200 and 1 not in ids

def test_bb07_buku_serupa_id_tidak_ada(client):
    """BB-07: id_buku tidak ada -> 404 dengan pesan error."""
    r = client.get("/api/buku-serupa/999999")
    assert r.status_code == 404 and "error" in r.json()

def test_bb08_id_anggota_bukan_angka(client):
    """BB-08: id anggota berupa huruf -> 404 (alamat tidak dikenali)."""
    assert client.get("/api/rekomendasi/abc").status_code == 404

def test_bb09_metode_selain_get_ditolak(client):
    """BB-09: POST ke endpoint rekomendasi -> 405 (hanya GET ynag diizinkan)."""
    assert client.post("/api/rekomendasi/1").status_code == 405
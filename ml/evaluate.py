"""Evaluasi model rekomendasi dengan Precision@K.

Car: untuk tiap anggota dengan riwayat cukup, simpan N peminjaman terakhir sebagai
data uji.
Model dilatih tanpa data uji itu, lalu Top-K rekomendasi dibandingkan dengan data uji.

Dua ukuran:
- Precision@K (buku tepat): rekomendasi sama persis dengan buku yang dipinjam kemudian.
                            Ukuran ketat, nilainya wajar kecil karena katalog ribuan buku.

- Precision@K (genre sesuai): rekomendasi bergenre sama dengan genre buku data uji
Pembanding (baseline): buku paling populer: buku paling populer yang belum dipinjam anggota.
"""

import sys
from pathlib import Path

from data_prep import load_data
from model import RecommendationService

def bagi_data(pinjam, n_uji=2, min_riwayat=4):
    pinjam = pinjam.sort_values(["id_anggota", "tanggal_pinjam"])
    jumlah = pinjam.groupby("id_anggota")["id_buku"].transform("count")
    layak = pinjam[jumlah >= min_riwayat]
    uji = layak.groupby("id_anggota").tail(n_uji)
    latih = pinjam.drop(uji.index)
    return latih, uji

def _skor(rek, relevan_buku, relevan_genre, k):
    tepat = len(set(rek["id_buku"]) & relevan_buku) / k
    genre = sum(g in relevan_genre for g in rek["kategori"]) / k
    return tepat, genre

def precision_at_k(svc, latih, uji, k):
    kategori = svc.buku.set_index("id_buku")["kategori"]
    hasil = {"model": [], "populer": []}
    for id_anggota, grup in uji.groupby("id_anggota"):
        relevan_buku = set(grup["id_buku"])
        relevan_genre = set(kategori.loc[grup["id_buku"]])
        sudah = latih.loc[latih["id_anggota"] == id_anggota, "id_buku"]
        hasil["model"].append(_skor(svc.rekomendasi(id_anggota, n=k), relevan_buku, relevan_genre, k))
        hasil["populer"].append(_skor(svc.buku_populer(k, kecuali=sudah), relevan_buku, relevan_genre, k))
    n = len(hasil["model"])
    rata = lambda daftar, i: sum(x[i] for x in daftar) / n
    return {nama: (rata(daftar, 0), rata(daftar, 1)) for nama, daftar in hasil.items()}, n

if __name__ == "__main__":
    data = Path(__file__).resolve().parent.parent / "data"
    path_buku = sys.argv[1] if len(sys.argv) > 1 else data / "buku_bersih.csv"
    path_pinjam = sys.argv[2] if len(sys.argv) > 2 else data / "riwayat_peminjaman.csv"

    buku, pinjam = load_data(path_buku, path_pinjam)
    latih, uji = bagi_data(pinjam)
    svc = RecommendationService().fit(buku, latih)

    print(f"Anggota diuji: {uji['id_anggota'].unique()} | Katalog: {len(buku)}buku\n")
    print(f"{'K':<4}{'Tepat (model)':<16}{'Tepat (populer)':<17}{'Genre (model)':<15}{'Genre (populer)':<15}")
    for k in (3, 5, 10):
        h, _ = precision_at_k(svc, latih, uji, k)
        print(f"{k:<4}{h['model'][0]:<16.3f}{h['populer'][0]:<17.3f}{h['model'][1]:<15.3f}{h['populer'][1]:<15.3f}")
        
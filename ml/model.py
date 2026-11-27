"""RecommendationService: content-based filtering (TF-IDF) + fallback buku populer.

Jenis model: custom model (scikit-learn), tanpa pre-trained model.
Skenario AI (UC-12): anggota tanpa riwayat -> tampilkan buku populer.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True)
        self.matriks = None
        self.buku = None
        self.pinjam = None

    def fit(self, buku: pd.DataFrame, pinjam: pd.DataFrame) -> "RecommendationService":
        self.buku = buku.reset_index(drop=True)
        self.pinjam = pinjam
        self.matriks = self.vectorizer.fit_transform(self.buku["teks"])
        return self

    def buku_populer(self, n: int = 5, kecuali=()) -> pd.DataFrame:
        """Buku paling sering dipinjam. Memakai times_borrowed dari katalog bila ada."""
        if "times_borrowed" in self.buku.columns:
            skor = self.buku.set_index("id_buku")["times_borrowed"]
        else:
            skor = self.pinjam["id_buku"].value_counts()
        skor = skor.drop(labels=[i for i in kecuali if i in skor.index]).sort_values(ascending=False)
        top = skor.head(n)
        hasil = self.buku.set_index("id_buku").loc[top.index, ["judul", "kategori"]].reset_index()
        hasil["skor"] = top.to_numpy()
        return hasil

    def rekomendasi(self, id_anggota, n: int = 5) -> pd.DataFrame:
       dipinjam = self.pinjam.loc[self.pinjam["id_anggota"] == id_anggota, "id_buku"].unique()
       if len(dipinjam) == 0:               # skenario A1
            return self.buku_populer(n)
       
       idx = self.buku.index[self.buku["id_buku"].isin(dipinjam)].tolist()
       profil = np.asarray(self.matriks[idx].mean(axis=0)) # profil minat anggota
       skor = cosine_similarity(profil, self.matriks).ravel()
       skor[idx] = -1 # buang buku yang sudah dipinjam

       top = np.argsort(skor)[::-1][:n]
       hasil = self.buku.iloc[top][["id_buku", "judul", "kategori"]].copy()
       hasil["skor"] = skor[top].round(3)
       return hasil.reset_index(drop=True)

    def buku_serupa(self, id_buku, n: int = 5) -> pd.DataFrame:
        """Buku yang lain mirip dengan satu buku (untuk halaman detail buku)."""
        posisi = self.buku.index[self.buku["id_buku"] == id_buku]
        if len(posisi) == 0:
            raise ValueError(f"id_buku {id_buku} tidak ada di katalog")
        skor = cosine_similarity(self.matriks[posisi[0]], self.matriks).ravel()
        skor[posisi[0]] = -1
        top = np.argsort(skor)[::-1][:n]
        hasil = self.buku.iloc[top][["id_buku", "judul", "kategori"]].copy()
        hasil["skor"] = skor[top].round(3)
        return hasil.reset_index(drop=True)

if __name__ == "__main__":
    from data_prep import load_data

    data = Path(__file__).resolve().parent.parent / "data"
    buku, pinjam = load_data(data / "buku_bersih.csv", data / "riwayat_peminjaman.csv")
    svc = RecommendationService().fit(buku, pinjam)

    pd.set_option("display.width", 120)
    pd.set_option("display.max_colwidth", 45)
    print("Rekomendasi untuk anggota 1:\n", svc.rekomendasi(99999, n=5))
    print("\nBuku serupa dengan id_buku 1:\n", svc.buku_serupa(1, n=5))
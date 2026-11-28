"""API rekomendasi buku (FR009) untuk backend Django.

Endpoint (didaftarkan di ml/urls.py):
    GET /api/rekomendasi/<id_anggota>?n=5   rekomendasi untuk anggota
    GET /api/buku-serupa/<id_buku>?n=5      buku yang mirip dengan satu buku
    
"""

from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .data_prep import load_data
from .model import RecommendationService

DATA = Path(__file__).resolve().parent.parent / "data"
N_DEFAULT, N_MAKS = 5, 20
_service = None

def get_service() -> RecommendationService:
    """Model dimuat sekali saja, saat pertama dipakai."""
    global _service
    if _service is None:
        buku, pinjam = load_data(DATA / "buku_bersih.csv", DATA / "riwayat_peminjaman.csv")
        _service = RecommendationService().fit(buku, pinjam)
    return _service

def _json(data, status=200):
    return JsonResponse(data, status=status, json_dumps_params={"ensure_ascii":False})

def _ambil_n(request) -> int:
    try:
        n = int(request.GET.get("n", N_DEFAULT))
    except ValueError:
        n = N_DEFAULT
    return max(1, min(n, N_MAKS))

@require_GET
def rekomendasi(request, id_anggota):
    svc = get_service()
    ada_riwayat = bool((svc.pinjam["id_anggota"] == id_anggota).any())
    hasil = svc.rekomendasi(id_anggota, n=_ambil_n(request))
    return _json({
        "id_anggota": id_anggota,
        "sumber": "riwayat" if ada_riwayat else "populer",      #populer = skenario A1
        "rekomendasi": hasil.to_dict(orient="records"),
    })

@require_GET
def buku_serupa(request, id_buku):
    svc = get_service()
    try:
        hasil = svc.buku_serupa(id_buku, n=_ambil_n(request))
    except ValueError as e:
        return _json({"error":str(e)}, status=404)
    return _json({"id_buku": id_buku, "serupa": hasil.to_dict(orient="records")})
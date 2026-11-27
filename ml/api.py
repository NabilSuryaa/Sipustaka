"""API rekomendasi buku (FR009), dibuat sebagai Flask Blueprint.

Dijalankan sendiri untuk uji coba: python api.py
Digabung ke backend Nabil (Flask): from api import rekomendasi_bp
                                   app.register_blueprint(rekomendasi_bp)

Endpoint:
    GET /api/rekomendasi/<id_anggota>?n=5       rekomendasi untuk anggota
    GET /api/buku-serupa/<id_buku>?n=5          buku yang mirip dengan satu buku
"""

from pathlib import Path

from flask import Blueprint, Flask, jsonify, request

from data_prep import load_data
from model import RecommendationService

DATA = Path(__file__).resolve().parent.parent / "data"
N_DEFAULT, N_MAKS = 5, 20

rekomendasi_bp = Blueprint("rekomendasi", __name__, url_prefix="/api")
_service = None

def get_service() -> RecommendationService:
    """Model dimuat sekali saja, saat pertama dipakai."""
    global _service
    if _service is None:
        buku, pinjam = load_data(DATA / "buku_bersih.csv", DATA / "riwayat_peminjaman.csv")
        _service = RecommendationService().fit(buku, pinjam)
    return _service

def _ambil_n() -> int:
    n = request.args.get("n", default=N_DEFAULT, type=int)
    return max(1, min(n, N_MAKS))

@rekomendasi_bp.get("/rekomendasi/<int:id_anggota>")
def rekomendasi(id_anggota):
    svc = get_service()
    ada_riwayat = bool((svc.pinjam["id_anggota"] == id_anggota).any())
    hasil = svc.rekomendasi(id_anggota, n=_ambil_n())
    return jsonify({
        "id_anggota": id_anggota,
        "sumber": "riwayat" if ada_riwayat else "populer", # populer=skenario A1
        "rekomendasi": hasil.to_dict(orient="records"),
    })

@rekomendasi_bp.get("/buku-serupa/<int:id_buku>")
def buku_serupa(id_buku):
    svc = get_service()
    try:
        hasil = svc.buku_serupa(id_buku, n=_ambil_n())
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({"id_buku": id_buku, "serupa": hasil.to_dict(orient="records")})

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(rekomendasi_bp)
    return app

if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
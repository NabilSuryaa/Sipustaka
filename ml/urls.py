"""Rute API rekomendasi. DI urls.py proyek Nabil cukup tambahkan:

    from django.urls import include, path
    urlpatterns = [..., path("", include("ml.urls))]
"""

from django.urls import path

from . import views

urlpatterns = [
    path("api/rekomendasi/<int:id_anggota>", views.rekomendasi, name="rekomendasi"),
    path("api/buku-serupa/<int:id_buku>", views.buku_serupa, name="buku_serupa"),
]
from django.urls import path
from . import views

urlpatterns = [
    # FR002 — Kelola Data Buku
    path('kelola-buku/', views.kelola_buku, name='kelola_buku'),
    path('kelola-buku/tambah/', views.tambah_buku, name='tambah_buku'),
    path('kelola-buku/edit/<int:id_buku>/', views.edit_buku, name='edit_buku'),
    path('kelola-buku/hapus/<int:id_buku>/', views.hapus_buku, name='hapus_buku'),
    path('kelola-buku/impor-csv/', views.impor_buku_csv, name='impor_buku_csv'),

    # FR004 — Kelola Data Anggota
    path('kelola-anggota/', views.kelola_anggota, name='kelola_anggota'),
    path('kelola-anggota/tambah/', views.tambah_anggota, name='tambah_anggota'),
    path('kelola-anggota/edit/<int:id_anggota>/', views.edit_anggota, name='edit_anggota'),
    path('kelola-anggota/status/<int:id_anggota>/', views.toggle_status_anggota, name='toggle_status_anggota'),

    # FR010 — Laporan dan Statistik
    path('laporan/', views.dashboard_laporan, name='dashboard_laporan'),
    path('laporan/ekspor-csv/', views.ekspor_laporan_csv, name='ekspor_laporan_csv'),
]
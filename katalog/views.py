import pandas as pd
import csv
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.db.models import Count, Sum
from .models import Buku, Users, Anggota, Peminjaman


# ==========================================================
# FR002 — KELOLA DATA BUKU (+ IMPOR CSV)
# ==========================================================

def kelola_buku(request):
    query = request.GET.get('q', '')
    kategori_filter = request.GET.get('kategori', '')

    buku_list = Buku.objects.all().order_by('-id_buku')

    if query:
        buku_list = buku_list.filter(
            Q(judul__icontains=query) |
            Q(penulis__icontains=query) |
            Q(kode_buku__icontains=query) |
            Q(isbn__icontains=query)
        )
    if kategori_filter:
        buku_list = buku_list.filter(kategori=kategori_filter)

    kategori_unik = Buku.objects.values_list('kategori', flat=True).distinct().exclude(kategori__isnull=True)
    paginator = Paginator(buku_list, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'katalog/kelola_buku.html', {
        'page_obj': page_obj,
        'query': query,
        'kategori_filter': kategori_filter,
        'kategori_unik': kategori_unik,
    })

def tambah_buku(request):
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        if not judul:
            messages.error(request, 'Judul buku wajib diisi.')
            return redirect('kelola_buku')

        jumlah_total = int(request.POST.get('jumlah_total') or 5)
        Buku.objects.create(
            kode_buku=request.POST.get('kode_buku') or None,
            isbn=request.POST.get('isbn') or None,
            judul=judul,
            penulis=request.POST.get('penulis', ''),
            kategori=request.POST.get('kategori', ''),
            section=request.POST.get('section', ''),
            lokasi_rak=request.POST.get('lokasi_rak', ''),
            subjects=request.POST.get('subjects', ''),
            deskripsi=request.POST.get('deskripsi', ''),
            year_published=request.POST.get('year_published', ''),
            jumlah_total=jumlah_total,
            jumlah_tersedia=jumlah_total,
        )
        messages.success(request, f'Buku "{judul}" berhasil ditambahkan ke katalog.')
    return redirect('kelola_buku')

def edit_buku(request, id_buku):
    buku = get_object_or_404(Buku, id_buku=id_buku)
    if request.method == 'POST':
        buku.kode_buku = request.POST.get('kode_buku') or None
        buku.isbn = request.POST.get('isbn') or None
        buku.judul = request.POST.get('judul', buku.judul)
        buku.penulis = request.POST.get('penulis', '')
        buku.kategori = request.POST.get('kategori', '')
        buku.section = request.POST.get('section', '')
        buku.lokasi_rak = request.POST.get('lokasi_rak', '')
        buku.subjects = request.POST.get('subjects', '')
        buku.year_published = request.POST.get('year_published', '')

        total_baru = int(request.POST.get('jumlah_total') or buku.jumlah_total)
        selisih = total_baru - buku.jumlah_total
        buku.jumlah_total = total_baru
        buku.jumlah_tersedia = max(0, buku.jumlah_tersedia + selisih)
        buku.save()

        messages.success(request, f'Data buku "{buku.judul}" berhasil diperbarui.')
    return redirect('kelola_buku')

def hapus_buku(request, id_buku):
    buku = get_object_or_404(Buku, id_buku=id_buku)
    if request.method == 'POST':
        if buku.jumlah_tersedia < buku.jumlah_total:
            messages.error(request, f'Buku "{buku.judul}" tidak dapat dihapus karena masih ada eksemplar yang sedang dipinjam.')
            return redirect('kelola_buku')
        judul = buku.judul
        buku.delete()
        messages.success(request, f'Buku "{judul}" berhasil dihapus.')
    return redirect('kelola_buku')

def impor_buku_csv(request):
    if request.method == 'POST' and request.FILES.get('file_csv'):
        file_csv = request.FILES['file_csv']
        if not file_csv.name.endswith('.csv'):
            messages.error(request, 'Format berkas tidak valid. Harap unggah file .csv.')
            return redirect('kelola_buku')

        try:
            df = pd.read_csv(file_csv)
            kolom_wajib = {'judul', 'penulis', 'kategori', 'section', 'subjects'}
            if not kolom_wajib.issubset(set(df.columns)):
                messages.error(request, f'Struktur kolom CSV tidak sesuai. Kolom wajib: {", ".join(kolom_wajib)}')
                return redirect('kelola_buku')

            df = df.fillna({'penulis': '', 'kategori': 'Umum', 'section': '', 'subjects': '', 'times_borrowed': 0, 'year_published': ''})

            objek_buku = []
            for _, row in df.iterrows():
                if not str(row['judul']).strip():
                    continue
                objek_buku.append(Buku(
                    judul=str(row['judul']).strip(),
                    penulis=str(row['penulis']).strip(),
                    kategori=str(row['kategori']).strip(),
                    section=str(row['section']).strip(),
                    subjects=str(row['subjects']).strip(),
                    times_borrowed=int(float(row['times_borrowed'])) if pd.notna(row['times_borrowed']) else 0,
                    rating_angka=float(row['rating_angka']) if 'rating_angka' in df.columns and pd.notna(row['rating_angka']) else None,
                    year_published=str(row['year_published']).replace('.0', '').strip(),
                    jumlah_total=5,
                    jumlah_tersedia=5
                ))

            Buku.objects.bulk_create(objek_buku, batch_size=500)
            messages.success(request, f'Berhasil mengimpor {len(objek_buku)} data buku dari CSV!')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat memproses CSV: {str(e)}')

    return redirect('kelola_buku')


# ==========================================================
# FR004 — KELOLA DATA ANGGOTA
# ==========================================================

def kelola_anggota(request):
    query = request.GET.get('q', '')
    jenis_filter = request.GET.get('jenis', '')

    anggota_list = Anggota.objects.select_related('id_user').all().order_by('-id_anggota')

    if query:
        anggota_list = anggota_list.filter(
            Q(nama__icontains=query) |
            Q(kode_anggota__icontains=query) |
            Q(prodi_unit__icontains=query)
        )
    if jenis_filter:
        anggota_list = anggota_list.filter(jenis_anggota=jenis_filter)

    paginator = Paginator(anggota_list, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'katalog/kelola_anggota.html', {
        'page_obj': page_obj,
        'query': query,
        'jenis_filter': jenis_filter,
    })

def tambah_anggota(request):
    if request.method == 'POST':
        kode_anggota = request.POST.get('kode_anggota', '').strip()
        nama = request.POST.get('nama', '').strip()

        if Anggota.objects.filter(kode_anggota=kode_anggota).exists():
            messages.error(request, f'NIM/NIP "{kode_anggota}" sudah terdaftar.')
            return redirect('kelola_anggota')

        with transaction.atomic():
            user_baru = Users.objects.create(
                username=kode_anggota,
                password_hash=make_password(kode_anggota),  # Password default = NIM/NIP
                role='anggota'
            )
            Anggota.objects.create(
                id_user=user_baru,
                kode_anggota=kode_anggota,
                nama=nama,
                jenis_anggota=request.POST.get('jenis_anggota', 'Mahasiswa'),
                prodi_unit=request.POST.get('prodi_unit', ''),
                jenis_kelamin=request.POST.get('jenis_kelamin', ''),
                email=request.POST.get('email', ''),
                no_hp=request.POST.get('no_hp', ''),
                status_aktif=1
            )
        messages.success(request, f'Anggota "{nama}" berhasil didaftarkan (Password default: {kode_anggota}).')
    return redirect('kelola_anggota')

def edit_anggota(request, id_anggota):
    anggota = get_object_or_404(Anggota, id_anggota=id_anggota)
    if request.method == 'POST':
        anggota.nama = request.POST.get('nama', anggota.nama)
        anggota.jenis_anggota = request.POST.get('jenis_anggota', anggota.jenis_anggota)
        anggota.prodi_unit = request.POST.get('prodi_unit', '')
        anggota.jenis_kelamin = request.POST.get('jenis_kelamin', '')
        anggota.email = request.POST.get('email', '')
        anggota.no_hp = request.POST.get('no_hp', '')
        anggota.save()
        messages.success(request, f'Data anggota "{anggota.nama}" berhasil diperbarui.')
    return redirect('kelola_anggota')

def toggle_status_anggota(request, id_anggota):
    anggota = get_object_or_404(Anggota, id_anggota=id_anggota)
    if request.method == 'POST':
        anggota.status_aktif = 0 if anggota.status_aktif == 1 else 1
        anggota.save()
        status_teks = 'diaktifkan' if anggota.status_aktif == 1 else 'dinonaktifkan'
        messages.success(request, f'Status keanggotaan "{anggota.nama}" berhasil {status_teks}.')
    return redirect('kelola_anggota')

# ==========================================================
# FR010 — LAPORAN DAN STATISTIK
# ==========================================================

def dashboard_laporan(request):
    # Ringkasan KPI Utama
    total_judul_buku = Buku.objects.count()
    total_eksemplar = Buku.objects.aggregate(total=Sum('jumlah_total'))['total'] or 0
    total_anggota_aktif = Anggota.objects.filter(status_aktif=1).count()
    total_dipinjam = Peminjaman.objects.filter(status_transaksi='dipinjam').count()
    total_terlambat = Peminjaman.objects.filter(status_transaksi='terlambat').count()
    total_denda = Peminjaman.objects.aggregate(total=Sum('denda'))['total'] or 0

    # Data Grafik 1: Distribusi Koleksi per Kategori (Top 7)
    kategori_stats = (
        Buku.objects.values('kategori')
        .annotate(jumlah=Count('id_buku'))
        .order_by('-jumlah')[:7]
    )
    label_kategori = [item['kategori'] or 'Lainnya' for item in kategori_stats]
    data_kategori = [item['jumlah'] for item in kategori_stats]

    # Data Grafik 2: Top 5 Buku Paling Sering Dipinjam (berdasarkan times_borrowed)
    buku_populer = Buku.objects.order_by('-times_borrowed')[:5]
    label_populer = [b.judul[:28] + ('...' if len(b.judul) > 28 else '') for b in buku_populer]
    data_populer = [b.times_borrowed for b in buku_populer]

    # Daftar Riwayat Transaksi Terbaru untuk Tabel Laporan
    transaksi_terbaru = Peminjaman.objects.select_related('id_anggota', 'id_buku').order_by('-id_peminjaman')[:15]

    return render(request, 'katalog/dashboard_laporan.html', {
        'total_judul_buku': total_judul_buku,
        'total_eksemplar': total_eksemplar,
        'total_anggota_aktif': total_anggota_aktif,
        'total_dipinjam': total_dipinjam,
        'total_terlambat': total_terlambat,
        'total_denda': total_denda,
        'label_kategori_json': json.dumps(label_kategori),
        'data_kategori_json': json.dumps(data_kategori),
        'label_populer_json': json.dumps(label_populer),
        'data_populer_json': json.dumps(data_populer),
        'buku_populer': buku_populer,
        'transaksi_terbaru': transaksi_terbaru,
    })

def ekspor_laporan_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="laporan_statistik_sipustaka.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Buku', 'Judul Buku', 'Penulis', 'Kategori', 'Section', 'Tahun Terbit', 'Total Dipinjam', 'Stok Tersedia', 'Stok Total'])

    for buku in Buku.objects.all().order_by('-times_borrowed'):
        writer.writerow([
            buku.id_buku,
            buku.judul,
            buku.penulis,
            buku.kategori,
            buku.section,
            buku.year_published,
            buku.times_borrowed,
            buku.jumlah_tersedia,
            buku.jumlah_total,
        ])

    return response
from django.db import models

class Buku(models.Model):
    id_buku = models.AutoField(primary_key=True)
    kode_buku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    judul = models.CharField(max_length=255)
    penulis = models.CharField(max_length=255, null=True, blank=True)
    kategori = models.CharField(max_length=100, null=True, blank=True)
    section = models.CharField(max_length=100, null=True, blank=True)
    lokasi_rak = models.CharField(max_length=100, null=True, blank=True)
    subjects = models.TextField(null=True, blank=True)
    deskripsi = models.TextField(null=True, blank=True)
    thumbnail = models.CharField(max_length=255, null=True, blank=True)
    times_borrowed = models.IntegerField(default=0)
    rating_angka = models.FloatField(null=True, blank=True)
    year_published = models.CharField(max_length=10, null=True, blank=True)
    jumlah_total = models.IntegerField(default=5)
    jumlah_tersedia = models.IntegerField(default=5)

    class Meta:
        db_table = 'buku'
        managed = False  # Menggunakan tabel dari schema.sql MySQL secara langsung

    def __str__(self):
        return f"{self.judul} ({self.penulis})"

class Users(models.Model):
    id_user = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='anggota')
    login_terakhir = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        managed = False

class Anggota(models.Model):
    id_anggota = models.AutoField(primary_key=True)
    id_user = models.OneToOneField(Users, on_delete=models.CASCADE, db_column='id_user', null=True, blank=True)
    kode_anggota = models.CharField(max_length=50, unique=True)
    nama = models.CharField(max_length=255)
    jenis_anggota = models.CharField(max_length=50, null=True, blank=True)
    prodi_unit = models.CharField(max_length=100, null=True, blank=True)
    jenis_kelamin = models.CharField(max_length=20, null=True, blank=True)
    genre_favorit = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    no_hp = models.CharField(max_length=20, null=True, blank=True)
    status_aktif = models.IntegerField(default=1)

    class Meta:
        db_table = 'anggota'
        managed = False

class Peminjaman(models.Model):
    id_peminjaman = models.AutoField(primary_key=True)
    kode_transaksi = models.CharField(max_length=50, unique=True)
    id_anggota = models.ForeignKey(Anggota, on_delete=models.CASCADE, db_column='id_anggota')
    id_buku = models.ForeignKey(Buku, on_delete=models.CASCADE, db_column='id_buku')
    tanggal_pinjam = models.DateField()
    tanggal_jatuh_tempo = models.DateField()
    tanggal_kembali = models.DateField(null=True, blank=True)
    status_transaksi = models.CharField(max_length=50, default='dipinjam')
    denda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'peminjaman'
        managed = False
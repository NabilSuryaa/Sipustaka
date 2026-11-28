CREATE DATABASE IF NOT EXISTS db_sipustaka CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_sipustaka;

CREATE TABLE IF NOT EXISTS users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'anggota',
    login_terakhir DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS anggota (
    id_anggota INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT UNIQUE,
    kode_anggota VARCHAR(50) NOT NULL UNIQUE,
    nama VARCHAR(255) NOT NULL,
    jenis_anggota VARCHAR(50),
    prodi_unit VARCHAR(100),
    jenis_kelamin VARCHAR(20),
    genre_favorit VARCHAR(255),
    email VARCHAR(191),
    no_hp VARCHAR(20),
    status_aktif TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_anggota_user FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS buku (
    id_buku INT AUTO_INCREMENT PRIMARY KEY,
    kode_buku VARCHAR(50) UNIQUE,
    isbn VARCHAR(50) UNIQUE,
    judul VARCHAR(255) NOT NULL,
    penulis VARCHAR(255),
    kategori VARCHAR(100),
    section VARCHAR(100),
    lokasi_rak VARCHAR(100),
    subjects TEXT,
    deskripsi TEXT,
    year_published VARCHAR(20),
    times_borrowed INT NOT NULL DEFAULT 0,
    rating_angka DECIMAL(3,2) NULL,
    jumlah_total INT NOT NULL DEFAULT 5,
    jumlah_tersedia INT NOT NULL DEFAULT 5
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS peminjaman (
    id_peminjaman INT AUTO_INCREMENT PRIMARY KEY,
    kode_transaksi VARCHAR(50) NOT NULL UNIQUE,
    id_anggota INT NOT NULL,
    id_buku INT NOT NULL,
    tanggal_pinjam DATE NOT NULL,
    tanggal_jatuh_tempo DATE NOT NULL,
    tanggal_kembali DATE NULL,
    status_transaksi VARCHAR(50) NOT NULL DEFAULT 'dipinjam',
    denda DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_pinjam_anggota FOREIGN KEY (id_anggota) REFERENCES anggota(id_anggota) ON DELETE CASCADE,
    CONSTRAINT fk_pinjam_buku FOREIGN KEY (id_buku) REFERENCES buku(id_buku) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS konfigurasi_sistem (
    id_konfigurasi INT AUTO_INCREMENT PRIMARY KEY,
    kunci VARCHAR(100) NOT NULL UNIQUE,
    nilai VARCHAR(255) NOT NULL,
    keterangan TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO konfigurasi_sistem (kunci, nilai, keterangan) VALUES
('maks_hari_pinjam', '7', 'Batas maksimal hari peminjaman standar'),
('denda_per_hari', '1000', 'Tarif denda keterlambatan per hari dalam Rupiah');
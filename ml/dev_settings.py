"""Pengaturan minimal agar API rekomendasi bisa dicoba tanpa proyek Django lengkap.

Hanya untuk uji coba sendiri dan pytest. Backend aplikasi memakai settings.py milik Nabil.
Jalankan dari folder utama repo: python -m django runserver --
settings=ml.dev_settings
"""
SECRET_KEY = "dev-only-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "ml.urls"
INSTALLED_APPS = []
USE_TZ = True
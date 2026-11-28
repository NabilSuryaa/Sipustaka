"""Menyiapkan jalur import dan pengaturan Django untuk pytest."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))       # agar "ml.urls" bisa diimpor
sys.path.insert(0, str(ROOT / "ml"))    # agar unit test bisa "from model import..."

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ml.dev_settings")

import django # noqa: E402

django.setup()
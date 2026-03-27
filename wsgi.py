"""
Ponto de entrada WSGI para produção (Gunicorn, Render, Railway, etc.).
SQLite: use apenas 1 worker (ver Procfile).
"""

from app.admin_seed import seed_admin_from_env
from app.extensions import db
from app.factory import create_app
from app.schema_utils import (
    ensure_gift_image_url_column,
    ensure_gift_price_label_column,
    ensure_gift_sort_order_column,
)

app = create_app()

with app.app_context():
    db.create_all()
    ensure_gift_image_url_column()
    ensure_gift_sort_order_column()
    ensure_gift_price_label_column()
    seed_admin_from_env()

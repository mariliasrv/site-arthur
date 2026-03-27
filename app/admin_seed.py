import os

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import AdminUser


def seed_admin_from_env() -> None:
    """
    Dev helper: create the initial admin user from env vars if missing.
    """

    username = os.getenv("ADMIN_USERNAME", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "").strip()

    if not username or not password:
        return

    existing = AdminUser.query.filter_by(username=username).first()
    if existing:
        return

    admin = AdminUser(
        username=username,
        password_hash=generate_password_hash(password),
    )
    db.session.add(admin)
    db.session.commit()


import os
from pathlib import Path


def _database_uri(base_dir: Path) -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        # Heroku/Render às vezes enviam postgres://; SQLAlchemy 2 prefere postgresql://
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        return url
    return f"sqlite:///{base_dir / 'app.db'}"


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    SQLALCHEMY_DATABASE_URI = _database_uri(BASE_DIR)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")


from typing import Optional

from sqlalchemy import text

from app.extensions import db


def ensure_gift_image_url_column() -> None:
    """
    Dev-time schema helper for SQLite:
    if Gift.image_url column doesn't exist yet, add it.
    """

    with db.engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(gift)")).fetchall()
        cols = {row[1] for row in result}  # row[1] = name
        if "image_url" in cols:
            return

        # SQLite supports ALTER TABLE ADD COLUMN (no default).
        conn.execute(text("ALTER TABLE gift ADD COLUMN image_url VARCHAR(800)"))
        conn.commit()


def ensure_gift_sort_order_column() -> None:
    with db.engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(gift)")).fetchall()
        cols = {row[1] for row in result}
        if "sort_order" in cols:
            return
        conn.execute(text("ALTER TABLE gift ADD COLUMN sort_order INTEGER DEFAULT 0"))
        conn.commit()


def ensure_gift_price_label_column() -> None:
    with db.engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(gift)")).fetchall()
        cols = {row[1] for row in result}
        if "price_label" in cols:
            return
        conn.execute(text("ALTER TABLE gift ADD COLUMN price_label VARCHAR(120)"))
        conn.commit()


def ensure_gift_description_column_optional() -> Optional[bool]:
    """
    Placeholder for future schema evolution.
    """

    return None


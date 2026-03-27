from datetime import datetime
from enum import Enum

from app.extensions import db


class GiftStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    HIDDEN = "hidden"


class Gift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    external_url = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(800), nullable=True)
    price_label = db.Column(db.String(120), nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default=GiftStatus.AVAILABLE.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    reservations = db.relationship(
        "Reservation",
        back_populates="gift",
        lazy=True,
        cascade="all, delete-orphan",
    )


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gift_id = db.Column(db.Integer, db.ForeignKey("gift.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    message_opt = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cleared_at = db.Column(db.DateTime, nullable=True)

    gift = db.relationship("Gift", back_populates="reservations")


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


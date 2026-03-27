from datetime import datetime

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models import AdminUser, Gift, GiftStatus, Reservation

def admin_required():
    admin_id = session.get("admin_user_id")
    if not admin_id:
        return False
    return True


@admin_bp.get("/login")
def login_get():
    return render_template("admin/login.html")


@admin_bp.post("/login")
def login_post():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    admin = AdminUser.query.filter_by(username=username).first()
    if not admin or not check_password_hash(admin.password_hash, password):
        flash("Usuário ou senha inválidos.", "error")
        return redirect(url_for("admin.login_get"))

    session["admin_user_id"] = admin.id
    return redirect(url_for("admin.dashboard"))


@admin_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login_get"))


@admin_bp.get("/dashboard")
def dashboard():
    if not admin_required():
        return redirect(url_for("admin.login_get"))

    gifts = Gift.query.order_by(Gift.sort_order.asc(), Gift.created_at.desc()).all()
    active_reservations = {
        r.gift_id: r
        for r in Reservation.query.filter_by(is_active=True).all()
    }
    return render_template("admin/dashboard.html", gifts=gifts, active_reservations=active_reservations)


@admin_bp.post("/gifts/<int:gift_id>/toggle-visibility")
def toggle_visibility(gift_id: int):
    if not admin_required():
        return redirect(url_for("admin.login_get"))

    gift = Gift.query.get_or_404(gift_id)
    active_reservation = Reservation.query.filter_by(gift_id=gift.id, is_active=True).first()

    # If there is an active reservation, we allow hiding, but we block switching to "available"
    # without clearing the reservation first.
    switching_to_available = gift.status == GiftStatus.HIDDEN.value
    if active_reservation and switching_to_available:
        flash("Para tornar este presente disponível novamente, primeiro limpe a reserva ativa.", "error")
        return redirect(url_for("admin.dashboard"))

    if gift.status == GiftStatus.HIDDEN.value:
        gift.status = GiftStatus.AVAILABLE.value
    else:
        gift.status = GiftStatus.HIDDEN.value

    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/gifts/<int:gift_id>/clear-reservation")
def clear_reservation(gift_id: int):
    if not admin_required():
        return redirect(url_for("admin.login_get"))

    gift = Gift.query.get_or_404(gift_id)

    reservation = Reservation.query.filter_by(gift_id=gift.id, is_active=True).first()
    if reservation:
        reservation.is_active = False
        reservation.cleared_at = datetime.utcnow()
        gift.status = GiftStatus.AVAILABLE.value
        db.session.commit()

    return redirect(url_for("admin.dashboard"))


def _coerce_optional_text(value: str | None, *, max_len: int) -> str | None:
    v = (value or "").strip()
    if not v:
        return None
    if len(v) > max_len:
        return None
    return v


def _parse_sort_order(raw: str | None) -> int:
    try:
        n = int((raw or "0").strip())
    except ValueError:
        return 0
    return max(0, min(n, 9999))


@admin_bp.get("/gifts/new")
def gift_new_get():
    if not admin_required():
        return redirect(url_for("admin.login_get"))
    return render_template("admin/gift_form.html", gift=None)


@admin_bp.post("/gifts/new")
def gift_new_post():
    if not admin_required():
        return redirect(url_for("admin.login_get"))

    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    external_url = _coerce_optional_text(request.form.get("external_url"), max_len=500)
    image_url = _coerce_optional_text(request.form.get("image_url"), max_len=800)
    price_label = _coerce_optional_text(request.form.get("price_label"), max_len=120)
    sort_order = _parse_sort_order(request.form.get("sort_order"))

    if not title or len(title) < 2:
        flash("Informe um título válido para o presente.", "error")
        return redirect(url_for("admin.gift_new_get"))

    gift = Gift(
        title=title,
        description=description or None,
        external_url=external_url,
        image_url=image_url,
        price_label=price_label,
        sort_order=sort_order,
        status=GiftStatus.AVAILABLE.value,
    )
    db.session.add(gift)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.get("/gifts/<int:gift_id>/edit")
def gift_edit_get(gift_id: int):
    if not admin_required():
        return redirect(url_for("admin.login_get"))
    gift = Gift.query.get_or_404(gift_id)
    return render_template("admin/gift_form.html", gift=gift)


@admin_bp.post("/gifts/<int:gift_id>/edit")
def gift_edit_post(gift_id: int):
    if not admin_required():
        return redirect(url_for("admin.login_get"))

    gift = Gift.query.get_or_404(gift_id)

    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    external_url = _coerce_optional_text(request.form.get("external_url"), max_len=500)
    image_url = _coerce_optional_text(request.form.get("image_url"), max_len=800)
    price_label = _coerce_optional_text(request.form.get("price_label"), max_len=120)
    sort_order = _parse_sort_order(request.form.get("sort_order"))

    if not title or len(title) < 2:
        flash("Informe um título válido para o presente.", "error")
        return redirect(url_for("admin.gift_edit_get", gift_id=gift_id))

    gift.title = title
    gift.description = description or None
    gift.external_url = external_url
    gift.image_url = image_url
    gift.price_label = price_label
    gift.sort_order = sort_order
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/gifts/<int:gift_id>/delete")
def gift_delete(gift_id: int):
    if not admin_required():
        return redirect(url_for("admin.login_get"))

    gift = Gift.query.get_or_404(gift_id)
    db.session.delete(gift)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


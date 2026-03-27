from flask import jsonify, render_template, request

from sqlalchemy import and_

from app.blueprints.public import public_bp
from app.extensions import db
from app.models import Gift, GiftStatus, Reservation


@public_bp.get("/")
def home():
    return render_template("public/home.html")


@public_bp.get("/gifts")
def gifts():
    items = (
        Gift.query.filter(Gift.status != GiftStatus.HIDDEN.value)
        .order_by(Gift.sort_order.asc(), Gift.created_at.desc())
        .all()
    )
    return render_template("public/gifts.html", gifts=items)


@public_bp.post("/reservations")
def create_reservation():
    payload = request.get_json(silent=True) or {}

    gift_id_raw = payload.get("gift_id")
    name = (payload.get("name") or "").strip()
    phone_raw = (payload.get("phone") or "").strip()
    message_opt = (payload.get("message_opt") or "").strip()

    errors = []

    try:
        gift_id = int(gift_id_raw)
        if gift_id <= 0:
            raise ValueError()
    except Exception:
        errors.append("Presente inválido.")

    if not name or len(name) < 2:
        errors.append("Informe seu nome (mínimo 2 caracteres).")

    # Normalize phone to digits only (simple MVP validation).
    phone_digits = "".join(ch for ch in phone_raw if ch.isdigit())
    if len(phone_digits) < 10 or len(phone_digits) > 15:
        errors.append("Informe um telefone válido (com DDD).")

    if message_opt and len(message_opt) > 500:
        errors.append("A mensagem deve ter no máximo 500 caracteres.")

    if errors:
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "title": "Não foi possível enviar a reserva.",
                        "message": " ".join(errors),
                    },
                }
            ),
            400,
        )

    reserved_status = GiftStatus.RESERVED.value
    available_status = GiftStatus.AVAILABLE.value

    try:
        with db.session.begin():
            updated = (
                Gift.query.filter(
                    and_(
                        Gift.id == gift_id,
                        Gift.status == available_status,
                    )
                )
                .update({"status": reserved_status}, synchronize_session=False)
            )

            # If no row was updated, the gift is not available (reserved/hidden/non-existent).
            if updated != 1:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": {
                                "title": "Presente indisponível.",
                                "message": "Este presente não está mais disponível para reserva.",
                            },
                        }
                    ),
                    409,
                )

            # Extra safety: if a reservation is already active for this gift, refuse.
            # This protects against inconsistent states caused by manual admin actions.
            existing_active = Reservation.query.filter_by(gift_id=gift_id, is_active=True).first()
            if existing_active:
                raise ValueError("RESERVATION_ALREADY_ACTIVE")

            reservation = Reservation(
                gift_id=gift_id,
                name=name,
                phone=phone_digits,
                message_opt=message_opt or None,
                is_active=True,
            )
            db.session.add(reservation)

        return jsonify({"success": True, "message": "Reserva confirmada. Obrigada!"}), 201
    except ValueError as e:
        if str(e) == "RESERVATION_ALREADY_ACTIVE":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": {
                            "title": "Reserva já existe.",
                            "message": "Este presente já possui uma reserva ativa.",
                        },
                    }
                ),
                409,
            )
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "title": "Não foi possível enviar a reserva.",
                        "message": "Verifique os dados e tente novamente.",
                    },
                }
            ),
            400,
        )
    except Exception:
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "title": "Erro ao processar a reserva.",
                        "message": "Tente novamente em instantes.",
                    },
                }
            ),
            500,
        )


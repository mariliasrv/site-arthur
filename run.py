from app import create_app
from app.extensions import db
from app.admin_seed import seed_admin_from_env
from app.schema_utils import (
    ensure_gift_image_url_column,
    ensure_gift_price_label_column,
    ensure_gift_sort_order_column,
)

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"db": db}


if __name__ == "__main__":
    # Debug local; produção vai usar gunicorn/WSGI.
    with app.app_context():
        db.create_all()
        ensure_gift_image_url_column()
        ensure_gift_sort_order_column()
        ensure_gift_price_label_column()
        seed_admin_from_env()
    app.run(host="0.0.0.0", port=5000, debug=True)


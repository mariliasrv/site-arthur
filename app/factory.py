from pathlib import Path

from flask import Flask

from app.blueprints.admin import admin_bp
from app.blueprints.public import public_bp
from app.config import Config
from app.extensions import db, migrate


def create_app(config_class=Config) -> Flask:
    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app


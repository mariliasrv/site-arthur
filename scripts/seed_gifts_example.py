"""
Insere alguns presentes de EXEMPLO no banco (somente se a tabela estiver vazia).

Uso (na pasta do projeto):
  python scripts/seed_gifts_example.py

Edite a lista EXAMPLES abaixo com os seus presentes reais (título, texto, link da loja, URL da imagem).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import Gift, GiftStatus  # noqa: E402
from app.schema_utils import (  # noqa: E402
    ensure_gift_image_url_column,
    ensure_gift_price_label_column,
    ensure_gift_sort_order_column,
)

# Substitua por itens reais da sua lista.
EXAMPLES: list[dict] = [
    {
        "title": "Exemplo: manta de bebê",
        "description": "Tamanho 80x100 cm, algodão. Sugestão de faixa de preço para referência.",
        "price_label": "R$ 70 – R$ 140",
        "external_url": "https://example.com/produto-exemplo-1",
        "image_url": None,
        "sort_order": 10,
    },
    {
        "title": "Exemplo: kit higiene",
        "description": "Itens para o enxoval; link leva a uma sugestão de loja.",
        "price_label": "A partir de R$ 45",
        "external_url": "https://example.com/produto-exemplo-2",
        "image_url": None,
        "sort_order": 20,
    },
    {
        "title": "Exemplo: livro infantil",
        "description": "Para começar a biblioteca do bebê.",
        "price_label": "R$ 29,90",
        "external_url": "https://example.com/produto-exemplo-3",
        "image_url": None,
        "sort_order": 30,
    },
]


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()
        ensure_gift_image_url_column()
        ensure_gift_sort_order_column()
        ensure_gift_price_label_column()

        if Gift.query.count() > 0:
            print(
                "Já existem presentes no banco. Nada foi alterado.\n"
                "Para usar o seed, apague os presentes pelo admin ou use outro arquivo app.db."
            )
            return

        for row in EXAMPLES:
            g = Gift(
                title=row["title"],
                description=row.get("description"),
                price_label=row.get("price_label"),
                external_url=row.get("external_url"),
                image_url=row.get("image_url"),
                sort_order=int(row.get("sort_order", 0)),
                status=GiftStatus.AVAILABLE.value,
            )
            db.session.add(g)
        db.session.commit()
        print(f"Incluídos {len(EXAMPLES)} presentes de exemplo. Confira em /gifts e edite pelo admin.")


if __name__ == "__main__":
    main()

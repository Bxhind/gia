from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.connection import get_session
from models import Material, MaterialType, Partner, PartnerType, Product, ProductType, Sale, User
from services import hash_password


def get_or_create(session, model, defaults=None, **filters):
    item = session.scalar(select(model).filter_by(**filters))
    if item:
        return item
    item = model(**filters, **(defaults or {}))
    session.add(item)
    session.flush()
    return item


def seed_database() -> None:
    try:
        with get_session() as session:
            get_or_create(session, User, username="admin", defaults={
                "password_hash": hash_password("admin123"), "full_name": "Администратор", "role": "admin", "is_active": True
            })

            retail = get_or_create(session, PartnerType, name="Розничный магазин")
            wholesale = get_or_create(session, PartnerType, name="Оптовый клиент")
            agency = get_or_create(session, PartnerType, name="Рекламное агентство")
            poly = get_or_create(session, ProductType, name="Полиграфия", defaults={"coefficient": Decimal("1.1500")})
            pack = get_or_create(session, ProductType, name="Упаковка", defaults={"coefficient": Decimal("1.3000")})
            paper = get_or_create(session, MaterialType, name="Бумага", defaults={"defect_percent": Decimal("1.50")})
            carton = get_or_create(session, MaterialType, name="Картон", defaults={"defect_percent": Decimal("2.00")})

            p1 = get_or_create(session, Partner, name="ООО Альфа Принт", defaults={
                "partner_type_id": wholesale.id, "legal_address": "620000, г. Екатеринбург, ул. Ленина, д. 1",
                "inn": "6671000001", "director_full_name": "Иванов Иван Иванович",
                "phone": "+7 (343) 111-11-11", "email": "alpha@example.com", "rating": 8
            })
            p2 = get_or_create(session, Partner, name="ИП Смирнова", defaults={
                "partner_type_id": retail.id, "legal_address": "620014, г. Екатеринбург, ул. Малышева, д. 25",
                "inn": "6672000002", "director_full_name": "Смирнова Анна Петровна",
                "phone": "+7 (343) 222-22-22", "email": "smirnova@example.com", "rating": 5
            })
            p3 = get_or_create(session, Partner, name="РА Вектор", defaults={
                "partner_type_id": agency.id, "legal_address": "620075, г. Екатеринбург, пр. Мира, д. 10",
                "inn": "6673000003", "director_full_name": "Петров Петр Сергеевич",
                "phone": "+7 (343) 333-33-33", "email": "vector@example.com", "rating": 9
            })
            pr1 = get_or_create(session, Product, article="PP-001", defaults={
                "product_type_id": poly.id, "name": "Буклет А4", "description": "Полноцветный буклет", "min_partner_price": Decimal("18.50")
            })
            pr2 = get_or_create(session, Product, article="PP-002", defaults={
                "product_type_id": pack.id, "name": "Коробка брендированная", "description": "Картонная упаковка с печатью", "min_partner_price": Decimal("42.00")
            })
            get_or_create(session, Material, name="Бумага мелованная 130 г/м2", defaults={
                "material_type_id": paper.id, "unit": "лист", "quantity_in_stock": Decimal("5000"), "min_quantity": Decimal("1000")
            })
            get_or_create(session, Material, name="Картон белый", defaults={
                "material_type_id": carton.id, "unit": "лист", "quantity_in_stock": Decimal("2300"), "min_quantity": Decimal("500")
            })
            if not session.scalar(select(Sale).limit(1)):
                session.add_all([
                    Sale(partner_id=p1.id, product_id=pr1.id, quantity=12000, sale_date=date(2025, 9, 10)),
                    Sale(partner_id=p1.id, product_id=pr2.id, quantity=41000, sale_date=date(2025, 12, 3)),
                    Sale(partner_id=p2.id, product_id=pr1.id, quantity=7500, sale_date=date(2026, 1, 20)),
                    Sale(partner_id=p3.id, product_id=pr1.id, quantity=220000, sale_date=date(2026, 2, 15)),
                    Sale(partner_id=p3.id, product_id=pr2.id, quantity=95000, sale_date=date(2026, 3, 1)),
                ])
            session.commit()
            print("Тестовые данные успешно добавлены.")
    except SQLAlchemyError as error:
        print(f"Ошибка заполнения БД: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    seed_database()

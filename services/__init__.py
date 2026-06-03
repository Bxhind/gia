import math
import re

import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from config.domain_config import DISCOUNT_THRESHOLDS
from models import MaterialType, ProductType, User


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def authenticate(session: Session, username: str, password: str):
    if not username.strip() or not password:
        return None, "Введите логин и пароль."
    user = session.scalar(select(User).where(User.username == username.strip()))
    if not user or not verify_password(password, user.password_hash):
        return None, "Неверный логин или пароль."
    if not user.is_active:
        return None, "Пользователь неактивен."
    return user, ""


def calculate_partner_discount(total_quantity: int) -> int:
    for quantity, discount in DISCOUNT_THRESHOLDS:
        if (total_quantity or 0) >= quantity:
            return discount
    return 0


def validate_partner(data: dict) -> list[str]:
    checks = [
        ("name", "Название партнера не должно быть пустым."),
        ("partner_type_id", "Выберите тип партнера."),
        ("legal_address", "Юридический адрес не должен быть пустым."),
        ("inn", "ИНН не должен быть пустым."),
        ("director_full_name", "ФИО руководителя не должно быть пустым."),
        ("phone", "Телефон не должен быть пустым."),
    ]
    errors = [text for key, text in checks if not str(data.get(key) or "").strip()]
    try:
        if int(data.get("rating", "")) < 0:
            errors.append("Рейтинг должен быть неотрицательным числом.")
    except ValueError:
        errors.append("Рейтинг должен быть целым числом.")
    if not EMAIL_RE.match(data.get("email", "").strip()):
        errors.append("Email должен быть похож на корректный адрес.")
    return errors


def calculate_required_material(product_type_id: int, material_type_id: int, product_quantity: int, param_1: float, param_2: float, session: Session) -> int:
    if product_quantity <= 0 or param_1 <= 0 or param_2 <= 0:
        return -1
    product_type = session.get(ProductType, product_type_id)
    material_type = session.get(MaterialType, material_type_id)
    if not product_type or not material_type:
        return -1
    value = param_1 * param_2 * float(product_type.coefficient) * product_quantity
    return math.ceil(value * (1 + float(material_type.defect_percent) / 100))

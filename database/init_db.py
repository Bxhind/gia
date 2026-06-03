from sqlalchemy.exc import SQLAlchemyError

from database.base import Base
from database.connection import engine, get_database_error_text
import models  # noqa: F401


def init_database() -> None:
    if engine is None:
        print(get_database_error_text())
        raise SystemExit(1)

    try:
        Base.metadata.create_all(engine)
        print("Таблицы успешно созданы.")
    except SQLAlchemyError as error:
        print(f"Ошибка создания таблиц: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    init_database()

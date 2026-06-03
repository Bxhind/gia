import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, future=True) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True) if engine else None
_last_error = ""


def get_database_error_text() -> str:
    return _last_error or "Не задан DATABASE_URL. Создайте .env по примеру .env.example."


def check_database_connection() -> bool:
    global _last_error
    if not engine:
        _last_error = (
            "Не найден DATABASE_URL. Проверьте .env.\n"
            "Пример: DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/gia_printplus"
        )
        return False
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        _last_error = ""
        return True
    except SQLAlchemyError as error:
        _last_error = f"Не удалось подключиться к PostgreSQL.\nОшибка: {error}"
        return False


@contextmanager
def get_session():
    if not SessionLocal:
        raise RuntimeError(get_database_error_text())
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

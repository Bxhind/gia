from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="manager")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PartnerType(Base):
    __tablename__ = "partner_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    partners: Mapped[list["Partner"]] = relationship(back_populates="partner_type")


class Partner(Base):
    __tablename__ = "partners"
    __table_args__ = (
        CheckConstraint("rating >= 0", name="ck_partners_rating_non_negative"),
        Index("ix_partners_name", "name"),
        Index("ix_partners_partner_type_id", "partner_type_id"),
        Index("ix_partners_rating", "rating"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    partner_type_id: Mapped[int] = mapped_column(ForeignKey("partner_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_address: Mapped[str] = mapped_column(Text, nullable=False)
    inn: Mapped[str] = mapped_column(String(20), nullable=False)
    director_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    logo_path: Mapped[str | None] = mapped_column(Text)
    partner_type: Mapped[PartnerType] = relationship(back_populates="partners")
    sales_history: Mapped[list["Sale"]] = relationship(back_populates="partner")


class ProductType(Base):
    __tablename__ = "product_types"
    __table_args__ = (CheckConstraint("coefficient > 0", name="ck_product_types_coefficient_positive"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    coefficient: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    products: Mapped[list["Product"]] = relationship(back_populates="product_type")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    article: Mapped[str | None] = mapped_column(String(100), unique=True)
    product_type_id: Mapped[int] = mapped_column(ForeignKey("product_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    min_partner_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    product_type: Mapped[ProductType] = relationship(back_populates="products")
    sales_history: Mapped[list["Sale"]] = relationship(back_populates="product")


class Sale(Base):
    __tablename__ = "sales_history"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sales_history_quantity_positive"),
        Index("ix_sales_history_partner_id", "partner_id"),
        Index("ix_sales_history_product_id", "product_id"),
        Index("ix_sales_history_sale_date", "sale_date"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    partner: Mapped[Partner] = relationship(back_populates="sales_history")
    product: Mapped[Product] = relationship(back_populates="sales_history")


class MaterialType(Base):
    __tablename__ = "material_types"
    __table_args__ = (CheckConstraint("defect_percent >= 0", name="ck_material_types_defect_non_negative"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    defect_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    materials: Mapped[list["Material"]] = relationship(back_populates="material_type")


class Material(Base):
    __tablename__ = "materials"
    id: Mapped[int] = mapped_column(primary_key=True)
    material_type_id: Mapped[int] = mapped_column(ForeignKey("material_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity_in_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    min_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    material_type: Mapped[MaterialType] = relationship(back_populates="materials")

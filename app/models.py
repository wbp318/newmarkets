from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    category: Mapped[str | None] = mapped_column(String(200))
    image_url: Mapped[str | None] = mapped_column(String(1000))
    price_usd: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(50), default="manual")  # amazon|tiktok|manual
    source_url: Mapped[str | None] = mapped_column(String(1000))
    source_rank: Mapped[int | None] = mapped_column(Integer)
    trend_score: Mapped[float | None] = mapped_column(Float, default=0.0)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    market_checks: Mapped[list["MarketCheck"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    translations: Mapped[list["Translation"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    suppliers: Mapped[list["Supplier"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class MarketCheck(Base):
    __tablename__ = "market_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    market: Mapped[str] = mapped_column(String(10))  # mx|co|br|ar
    found: Mapped[bool] = mapped_column(Boolean, default=False)
    competitor_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_price_local: Mapped[float | None] = mapped_column(Float)
    avg_price_usd: Mapped[float | None] = mapped_column(Float)
    platform: Mapped[str] = mapped_column(String(50), default="mercadolibre")
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    product: Mapped["Product"] = relationship(back_populates="market_checks")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    market: Mapped[str] = mapped_column(String(10))
    gap_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    trend_velocity: Mapped[float | None] = mapped_column(Float)
    estimated_margin: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="new")  # new|researching|launching|active|passed
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    product: Mapped["Product"] = relationship(back_populates="opportunities")


class Translation(Base):
    __tablename__ = "translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    language: Mapped[str] = mapped_column(String(10))  # es|pt
    original_copy: Mapped[str] = mapped_column(Text)
    translated_copy: Mapped[str] = mapped_column(Text)
    ad_type: Mapped[str] = mapped_column(String(50))  # headline|body|cta
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    product: Mapped["Product"] = relationship(back_populates="translations")


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    supplier_name: Mapped[str] = mapped_column(String(500))
    platform: Mapped[str] = mapped_column(String(100), default="aliexpress")
    url: Mapped[str | None] = mapped_column(String(1000))
    unit_price_usd: Mapped[float | None] = mapped_column(Float)
    min_order: Mapped[int | None] = mapped_column(Integer)
    shipping_days: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    product: Mapped["Product"] = relationship(back_populates="suppliers")

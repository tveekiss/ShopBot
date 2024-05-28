import os

from dotenv import load_dotenv

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

load_dotenv()

engine = create_async_engine(os.getenv("SQLALCHEMY_URL"), echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    brands: Mapped[list['Brand']] = relationship(back_populates="category", lazy='joined', cascade='delete')

    def __str__(self):
        return self.name


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'))

    category: Mapped['Category'] = relationship(back_populates='brands', lazy='joined')
    items: Mapped[list['Item']] = relationship(back_populates='brand', lazy='joined', cascade='delete')

    def __str__(self):
        return f'{self.name} ({self.category_id})'


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    photo: Mapped[str]
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete='CASCADE'))

    brand: Mapped['Brand'] = relationship(back_populates='items', lazy='joined')
    baskets: Mapped[list['Basket']] = relationship(back_populates='item', lazy='joined', cascade='delete')


class Basket(Base):
    __tablename__ = "baskets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    quantity: Mapped[int]

    item: Mapped['Item'] = relationship(back_populates='baskets', lazy='joined')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

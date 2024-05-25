from app.database.models import async_session, Brand, Item, Category
from sqlalchemy import select, update


async def get_all_categories():
    async with async_session() as session:
        categories = await session.execute(select(Category))
        categories = categories.scalars().all().unique()
        return categories


async def get_all_brands(category_id):
    async with async_session() as session:
        print(category_id)
        brands = await session.execute(select(Brand).where(Brand.category_id == category_id))
        brands = brands.scalars().all().unique()
        print(brands)
        return brands


async def get_all_items():
    async with async_session() as session:
        items = await session.execute(select(Item))
        items = items.scalars().unique().all()
        return items


# ========== SETTINGS ==========
async def add_category(name):
    async with async_session() as session:
        category = Category(name=name)
        session.add(category)
        await session.commit()


async def update_category(category_id, name):
    async with async_session() as session:
        category = session.get(Category, category_id)
        category.name = name
        await session.refresh(category)
        await session.commit()


async def delete_category(category_id):
    async with async_session() as session:
        category = session.get(Category, category_id)
        await session.delete(category)
        await session.commit()


async def add_brand(name, category_id):
    async with async_session() as session:
        category = await session.execute(select(Category).where(Category.id == category_id))
        category = category.scalars().one_or_none()
        brand = Brand(name=name, category=category)
        session.add(brand)
        await session.commit()


async def update_brand(brand_id, name=None, category_id=None):
    async with async_session() as session:
        brand = await session.get(Brand, brand_id)
        if name is not None:
            brand.name = name
        if category_id is not None:
            brand.category_id = category_id
        await session.refresh(brand)
        await session.commit()


async def delete_brand(brand_id):
    async with async_session() as session:
        brand = await session.execute(select(Brand).where(Brand.id == brand_id))
        brand = brand.scalars().one_or_none()
        await session.delete(brand)
        await session.commit()


async def add_item(name, price, description, brand_id, photo):
    async with async_session() as session:
        item = Item(name=name, price=int(price), description=description, brand_id=brand_id, photo=photo)
        session.add(item)
        await session.commit()


async def update_item(item_id, name, price, description, brand_id):
    async with async_session() as session:
        item = await session.get(Item, item_id)
        if name is not None:
            item.name = name
        if price is not None:
            item.price = int(price)
        if description is not None:
            item.description = description
        if brand_id is not None:
            item.brand_id = brand_id
        await session.refresh(item)
        await session.commit()


async def delete_item(item_id):
    async with async_session() as session:
        item = session.get(Item, item_id)
        await session.delete(item)
        await session.commit()

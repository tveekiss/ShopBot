from app.database.models import async_session, Brand, Item, Category, Basket
from sqlalchemy import select


async def get_all_categories():
    async with async_session() as session:
        categories = await session.execute(select(Category))
        categories = categories.scalars().unique().all()
        return categories


async def get_all_brands(category_id):
    async with async_session() as session:
        print(category_id)
        brands = await session.execute(select(Brand).where(Brand.category_id == category_id))
        brands = brands.scalars().unique().all()
        print(brands)
        return brands


async def get_all_items():
    async with async_session() as session:
        items = await session.execute(select(Item))
        items = items.scalars().unique().all()
        return items


async def get_items_by_category(category_id):
    async with async_session() as session:
        items = await session.execute(select(Item).join(Brand).join(Category).filter(Brand.category_id == category_id))
        items = items.scalars().unique().all()
        return items


# ========== SETTINGS ==========
async def add_category(name):
    async with async_session() as session:
        category = Category(name=name)
        session.add(category)
        await session.commit()


async def get_category(category_id):
    async with async_session() as session:
        category = await session.get(Category, category_id)
        return category


async def update_category(category_id, name):
    async with async_session() as session:
        category = await session.get(Category, category_id)
        category.name = name
        session.refresh(category)
        await session.commit()


async def delete_category(category_id):
    async with async_session() as session:
        category = await session.get(Category, category_id)
        await session.delete(category)
        await session.commit()


async def add_brand(name, category_id):
    async with async_session() as session:
        category = await session.get(Category, category_id)
        brand = Brand(name=name, category=category)
        session.add(brand)
        await session.commit()


async def get_brand(brand_id):
    async with async_session() as session:
        brand = await session.get(Brand, brand_id)
        return brand


async def update_brand(brand_id, name=None, category_id=None):
    async with async_session() as session:
        brand = await session.get(Brand, brand_id)
        if name is not None:
            brand.name = name
        if category_id is not None:
            brand.category_id = category_id
        session.refresh(brand)
        await session.commit()


async def delete_brand(brand_id):
    async with async_session() as session:
        brand = await session.get(Brand, brand_id)
        await session.delete(brand)
        await session.commit()


async def add_item(name, price, description, brand_id, photo):
    async with async_session() as session:
        item = Item(name=name, price=price, description=description, brand_id=brand_id, photo=photo)
        session.add(item)
        await session.commit()


async def get_item(item_id):
    async with async_session() as session:
        item = await session.get(Item, item_id)
        return item


async def update_item(item_id, name=None, price=None, description=None, brand_id=None, photo=None):
    async with async_session() as session:
        item = await session.get(Item, item_id)
        if name is not None:
            item.name = name
        if price is not None:
            item.price = price
        if description is not None:
            item.description = description
        if brand_id is not None:
            brand = await session.get(Brand, brand_id)
            item.brand = brand
        if photo is not None:
            item.photo = photo
        session.refresh(item)
        await session.commit()


async def delete_item(item_id):
    async with async_session() as session:
        item = await session.get(Item, item_id)
        await session.delete(item)
        await session.commit()


async def create_basket(item_id, tg_id, quantity):
    async with async_session() as session:
        basket_check = await session.scalar(select(Basket).
                                            where(Basket.item_id == item_id, Basket.user_id == tg_id))
        if basket_check is None:
            basket = Basket(item_id=item_id, user_id=tg_id, quantity=quantity)
        else:
            basket = basket_check
            basket.quantity += 1
        session.add(basket)
        await session.commit()


async def delete_basket(basket_id):
    async with async_session() as session:
        basket = await session.get(Basket, basket_id)
        await session.delete(basket)
        await session.commit()


async def get_all_baskets(tg_id):
    async with async_session() as session:
        baskets = await session.execute(select(Basket).where(Basket.user_id == tg_id))
        baskets = baskets.scalars().unique().all()
        return baskets


async def get_basket(basket_id):
    async with async_session() as session:
        basket = await session.get(Basket, basket_id)
        return basket


async def edit_quantity(basket_id, quantity):
    async with async_session() as session:
        basket = await session.get(Basket, basket_id)
        basket.quantity = quantity
        await session.commit()

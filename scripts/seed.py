import asyncio
from api.database import AsyncSessionLocal
from api.models import Category, Product

async def seed():
    async with AsyncSessionLocal() as session:
        # Categories
        cat1 = Category(name="Одежда", slug="clothes")
        cat2 = Category(name="Электроника", slug="electronics")
        cat3 = Category(name="Дом", slug="home")
        session.add_all([cat1, cat2, cat3])
        await session.flush()

        # Products
        products = [
            Product(name="Футболка Premium", description="100% хлопок, премиум качество", price=29.99, stock=100, category_id=cat1.id, image_url="https://via.placeholder.com/300"),
            Product(name="Джинсы Classic", description="Классический крой, темно-синий", price=59.99, stock=50, category_id=cat1.id, image_url="https://via.placeholder.com/300"),
            Product(name="Наушники Bluetooth", description="Беспроводные, шумоподавление", price=89.99, stock=30, category_id=cat2.id, image_url="https://via.placeholder.com/300"),
            Product(name="Power Bank 20000", description="Быстрая зарядка, 20000 mAh", price=45.99, stock=40, category_id=cat2.id, image_url="https://via.placeholder.com/300"),
            Product(name="Свеча ароматическая", description="Лаванда, ручная работа", price=12.99, stock=200, category_id=cat3.id, image_url="https://via.placeholder.com/300"),
            Product(name="Кружка керамическая", description="350 мл, ручная роспись", price=15.99, stock=80, category_id=cat3.id, image_url="https://via.placeholder.com/300"),
        ]
        session.add_all(products)
        await session.commit()
        print("✅ Seed data created!")

if __name__ == "__main__":
    asyncio.run(seed())

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db import engine, Base, User, Meal, DailySummary, UserProfile
from sqlalchemy.future import select
import datetime
import hashlib

async def init_models():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

async def create_test_data():
    """Create test data"""
    from db.db import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # create multiple test users
        test_users = [
            User(username="test_user", email="test@example.com", password_hash=hashlib.sha256("test123".encode()).hexdigest()),
            User(username="user2", email="user2@example.com", password_hash=hashlib.sha256("test123".encode()).hexdigest()),
            User(username="user3", email="user3@example.com", password_hash=hashlib.sha256("test123".encode()).hexdigest()),
        ]
        
        for user in test_users:
            session.add(user)
        await session.commit()
        
        for user in test_users:
            await session.refresh(user)
            print(f"Test user created successfully! ID: {user.id}, username: {user.username}")
        
        # create user health profile
        test_profiles = [
            UserProfile(user_id=1, height=170, weight=65, target_weight=60, is_vegetarian=False, allergies="peanut", chronic_diseases="hypertension", age=30, gender="male"),
            UserProfile(user_id=2, height=160, weight=55, target_weight=50, is_vegetarian=True, allergies="", chronic_diseases="", age=28, gender="female"),
            UserProfile(user_id=3, height=175, weight=80, target_weight=70, is_vegetarian=False, allergies="seafood", chronic_diseases="diabetes", age=40, gender="male"),
        ]
        for profile in test_profiles:
            session.add(profile)
        await session.commit()
        print(f"Test user health profile created successfully! Total {len(test_profiles)} records")
        
        # create some test meal records
        test_meals = [
            Meal(
                user_id=1,
                input_text="had a chicken sandwich for lunch today",
                calories=350.0,
                protein=25.0,
                fat=12.0,
                carbohydrates=35.0,
                fiber=3.0,
                sugar=5.0,
                sodium=800.0,
                vitamins='{"vitamin_c": 15, "vitamin_b12": 2.5}',
                minerals='{"iron": 3.2, "calcium": 150}',
                gpt_raw_response='{"calories": 350, "protein": 25, "fat": 12, "carbs": 35}'
            ),
            Meal(
                user_id=1,
                input_text="下午吃了一支雪糕",
                calories=207.0,
                protein=3.5,
                fat=11.0,
                carbohydrates=24.0,
                fiber=0.0,
                sugar=20.0,
                sodium=80.0,
                vitamins='{"vitamin_a": 150}',
                minerals='{"calcium": 120}',
                gpt_raw_response='{"calories": 207, "protein": 3.5, "fat": 11, "carbs": 24}'
            ),
            Meal(
                user_id=2,
                input_text="had some bread for breakfast and went out",
                calories=200.0,
                protein=6.0,
                fat=3.0,
                carbohydrates=35.0,
                fiber=2.0,
                sugar=3.0,
                sodium=400.0,
                vitamins='{"vitamin_b1": 0.2}',
                minerals='{"iron": 1.5}',
                gpt_raw_response='{"calories": 200, "protein": 6, "fat": 3, "carbs": 35}'
            )
        ]
        
        for meal in test_meals:
            session.add(meal)
        await session.commit()
        print(f"Test meal records created successfully! Total {len(test_meals)} records")
        
        # create today's summary record
        today = datetime.date.today()
        daily_summaries = [
            DailySummary(
                user_id=1,
                date=today,
                total_calories=557.0,
                total_protein=28.5,
                total_fat=23.0,
                total_carbs=59.0,
                total_fiber=3.0,
                total_sugar=25.0
            ),
            DailySummary(
                user_id=2,
                date=today,
                total_calories=200.0,
                total_protein=6.0,
                total_fat=3.0,
                total_carbs=35.0,
                total_fiber=2.0,
                total_sugar=3.0
            )
        ]
        
        for summary in daily_summaries:
            session.add(summary)
        await session.commit()
        print(f"Today's summary record created successfully!")

async def show_database_info():
    """显示数据库信息"""
    from db.db import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 统计各表记录数
        tables = [User, UserProfile, Meal, DailySummary]
        table_names = ["user", "health profile", "meal record", "daily summary"]
        
        print("\ndatabase statistics:")
        for table, name in zip(tables, table_names):
            result = await session.execute(select(table))
            count = len(result.scalars().all())
            print(f"  {name} table: {count} records")

if __name__ == "__main__":
    print("start initializing database...")
    asyncio.run(init_models())
    asyncio.run(create_test_data())
    asyncio.run(show_database_info())
    print("\ndatabase initialization completed!") 
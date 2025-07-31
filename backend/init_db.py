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
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建成功！")

async def create_test_data():
    """创建测试数据"""
    from db.db import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 创建多个测试用户
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
            print(f"测试用户创建成功！ID: {user.id}, 用户名: {user.username}")
        
        # 创建用户健康档案
        test_profiles = [
            UserProfile(user_id=1, height=170, weight=65, target_weight=60, is_vegetarian=False, allergies="peanut", chronic_diseases="hypertension", age=30, gender="male"),
            UserProfile(user_id=2, height=160, weight=55, target_weight=50, is_vegetarian=True, allergies="", chronic_diseases="", age=28, gender="female"),
            UserProfile(user_id=3, height=175, weight=80, target_weight=70, is_vegetarian=False, allergies="seafood", chronic_diseases="diabetes", age=40, gender="male"),
        ]
        for profile in test_profiles:
            session.add(profile)
        await session.commit()
        print(f"测试用户健康档案创建成功！共 {len(test_profiles)} 条记录")
        
        # 创建一些测试餐食记录
        test_meals = [
            Meal(
                user_id=1,
                input_text="今天中午吃了一个鸡肉三明治",
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
                input_text="早饭吃了一些面包就出门了",
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
        print(f"测试餐食记录创建成功！共 {len(test_meals)} 条记录")
        
        # 创建今日汇总记录
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
        print(f"今日汇总记录创建成功！")

async def show_database_info():
    """显示数据库信息"""
    from db.db import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 统计各表记录数
        tables = [User, UserProfile, Meal, DailySummary]
        table_names = ["用户", "健康档案", "餐食记录", "每日汇总"]
        
        print("\n数据库统计信息:")
        for table, name in zip(tables, table_names):
            result = await session.execute(select(table))
            count = len(result.scalars().all())
            print(f"  {name}表: {count} 条记录")

if __name__ == "__main__":
    print("开始初始化数据库...")
    asyncio.run(init_models())
    asyncio.run(create_test_data())
    asyncio.run(show_database_info())
    print("\n数据库初始化完成！") 
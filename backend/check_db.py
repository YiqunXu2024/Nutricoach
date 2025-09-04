import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db import AsyncSessionLocal, User, Meal, DailySummary, UserProfile
from sqlalchemy.future import select
import json

async def check_database():
    """check database data"""
    async with AsyncSessionLocal() as session:
        # check users
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"user count: {len(users)}")
        for user in users:
            print(f"  - user id: {user.id}, username: {user.username}, email: {user.email}")
        
        # 检查餐食记录
        result = await session.execute(select(Meal))
        meals = result.scalars().all()
        print(f"\nmeal record count: {len(meals)}")
        for meal in meals:
            print(f"  - record id: {meal.id}")
            print(f"    user id: {meal.user_id}")
            print(f"    input text: {meal.input_text}")
            print(f"    calories: {meal.calories}kcal, protein: {meal.protein}g")
            print(f"    created at: {meal.meal_time}")
            print("    ---")
        
        # 检查每日汇总
        result = await session.execute(select(DailySummary))
        summaries = result.scalars().all()
        print(f"\ndaily summary count: {len(summaries)}")
        for summary in summaries:
            print(f"  - summary id: {summary.id}")
            print(f"    user id: {summary.user_id}")
            print(f"    date: {summary.date}")
            print(f"    total calories: {summary.total_calories}kcal")
            print(f"    total protein: {summary.total_protein}g")
            print("    ---")
        
        # 检查用户档案
        result = await session.execute(select(UserProfile))
        profiles = result.scalars().all()
        print(f"\nuser profile count: {len(profiles)}")
        for profile in profiles:
            print(f"  - profile id: {profile.id}")
            print(f"    user id: {profile.user_id}")
            print(f"    height: {profile.height}cm, weight: {profile.weight}kg")
            print(f"    target weight: {profile.target_weight}kg")
            print(f"    age: {profile.age}, gender: {profile.gender}")
            print(f"    vegetarian: {profile.is_vegetarian}")
            print(f"    allergies: {profile.allergies}")
            print("    ---")

if __name__ == "__main__":
    print("check database content...")
    asyncio.run(check_database())
    print("check completed!") 
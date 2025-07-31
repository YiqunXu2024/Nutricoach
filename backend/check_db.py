import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db import AsyncSessionLocal, User, Meal, DailySummary
from sqlalchemy.future import select
import json

async def check_database():
    """检查数据库中的数据"""
    async with AsyncSessionLocal() as session:
        # 检查用户
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"用户数量: {len(users)}")
        for user in users:
            print(f"  - 用户ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}")
        
        # 检查餐食记录
        result = await session.execute(select(Meal))
        meals = result.scalars().all()
        print(f"\n餐食记录数量: {len(meals)}")
        for meal in meals:
            print(f"  - 记录ID: {meal.id}")
            print(f"    用户ID: {meal.user_id}")
            print(f"    输入描述: {meal.input_text}")
            print(f"    热量: {meal.calories}卡, 蛋白质: {meal.protein}g")
            print(f"    创建时间: {meal.meal_time}")
            print("    ---")
        
        # 检查每日汇总
        result = await session.execute(select(DailySummary))
        summaries = result.scalars().all()
        print(f"\n每日汇总数量: {len(summaries)}")
        for summary in summaries:
            print(f"  - 汇总ID: {summary.id}")
            print(f"    用户ID: {summary.user_id}")
            print(f"    日期: {summary.date}")
            print(f"    总热量: {summary.total_calories}卡")
            print(f"    总蛋白质: {summary.total_protein}g")
            print("    ---")

if __name__ == "__main__":
    print("检查数据库内容...")
    asyncio.run(check_database())
    print("检查完成！") 
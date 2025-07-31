#设计数据库模型
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text, Boolean, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 关联关系
    meals = relationship("Meal", back_populates="user")
    daily_summaries = relationship("DailySummary", back_populates="user")
    profile = relationship("UserProfile", uselist=False, back_populates="user")

class Meal(Base):
    """餐食记录表"""
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_text = Column(Text, nullable=False)  # 用户原始描述
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    sugar = Column(Float, nullable=True)
    sodium = Column(Float, nullable=True)
    vitamins = Column(Text, nullable=True)  # JSON字符串
    minerals = Column(Text, nullable=True)  # JSON字符串
    gpt_raw_response = Column(Text, nullable=True)  # GPT返回的原始JSON
    meal_time = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="meals")

class DailySummary(Base):
    """每日营养汇总表"""
    __tablename__ = "daily_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)  # 日期
    total_calories = Column(Float, default=0.0)
    total_protein = Column(Float, default=0.0)
    total_fat = Column(Float, default=0.0)
    total_carbs = Column(Float, default=0.0)
    total_fiber = Column(Float, default=0.0)
    total_sugar = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="daily_summaries")

class UserProfile(Base):
    """用户健康档案表"""
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    height = Column(Float, nullable=True)  # 身高cm
    weight = Column(Float, nullable=True)  # 体重kg
    target_weight = Column(Float, nullable=True)  # 目标体重kg
    is_vegetarian = Column(Boolean, default=False)  # 是否素食
    allergies = Column(String(255), nullable=True)  # 过敏源，逗号分隔
    chronic_diseases = Column(String(255), nullable=True)  # 基础疾病，逗号分隔
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)  # 'male', 'female', 'other'
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")

#创建数据库引擎，配置数据库连接
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./nutricoach.db"  # 改名为nutricoach.db
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

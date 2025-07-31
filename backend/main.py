from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel
import openai
import os
import requests
import json
from db.db import AsyncSessionLocal, User, Meal, DailySummary
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.future import select
import datetime
import hashlib
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, date
from fastapi import APIRouter
from db.db import UserProfile

# AI 后端配置
AI_BACKEND = os.getenv("AI_BACKEND", "ollama")  # 可选: "openai", "ollama", "huggingface"

# OpenAI 配置
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ollama 配置
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# HuggingFace 配置
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium")

SECRET_KEY = "your_secret_key"  # 建议用更复杂的字符串
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

app = FastAPI(title="NutriCoach API", description="营养分析 API")

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class FoodInput(BaseModel):
    input_text: str  # 用户原始描述

class NutritionResponse(BaseModel):
    calories: float
    protein: float
    fat: float
    carbohydrates: float
    fiber: float
    sugar: float
    sodium: float
    vitamins: dict = {}  # 维生素信息
    minerals: dict = {}  # 矿物质信息

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@app.get("/")
def read_root():
    return {
        "message": "Welcome to NutriCoach API", 
        "docs": "/docs",
        "ai_backend": AI_BACKEND
    }

#获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed

@app.post("/register")
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        result = await db.execute(select(User).where(User.username == user_data.username))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # 创建新用户
        new_user = User(
            username=user_data.username,
            password_hash=hash_password(user_data.password),
            email=user_data.email
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return {
            "message": "Registration successful",
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # OAuth2PasswordRequestForm自动获取username和password字段
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username or password error")
    access_token = create_access_token(data={"user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="无效的认证凭据")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    print("user:", user)#debug
    print("user.password_hash:", user.password_hash)#debug
    print("type(user):", type(user))#debug
    print("type(user.password_hash):", type(user.password_hash))#debug
    return user

def get_ai_response(prompt: str, model: str = "ollama"):
    """
    统一AI调用接口，支持 openai、ollama、huggingface
    """
    if model == "openai":
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API Key not set")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=512
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    elif model == "ollama":
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ollama API error: {str(e)}")
    elif model == "huggingface":
        if not HUGGINGFACE_API_KEY:
            raise HTTPException(status_code=500, detail="HuggingFace API Key not set")
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}",
                headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
                json={"inputs": prompt}
            )
            response.raise_for_status()
            return response.json()[0]["generated_text"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HuggingFace API error: {str(e)}")
    else:
        raise HTTPException(status_code=500, detail=f"Unsupported AI backend: {model}")

@app.post("/analyze_food")
async def analyze_food(
    input: FoodInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 现在 current_user 就是已认证的用户对象
    # 你可以用 current_user.id 作为 user_id
    prompt = f"""
你是一个营养师助手。请根据用户输入的食物描述，分析这顿饭的营养成分。
注意：用户输入可能是自然语言、口语、或结构化描述，请尽量理解并分析。

重要：你必须严格按照以下JSON格式输出，不要添加任何其他文字：

{{
  "calories": 总热量（数字，单位千卡）, 
  "protein": 蛋白质（数字，单位克）, 
  "fat": 脂肪（数字，单位克）, 
  "carbohydrates": 碳水化合物（数字，单位克）, 
  "fiber": 膳食纤维（数字，单位克）, 
  "sugar": 糖分（数字，单位克）, 
  "sodium": 钠（数字，单位毫克）, 
  "vitamins": {{
    "vitamin_a": 数字,
    "vitamin_c": 数字,
    "vitamin_d": 数字,
    "vitamin_e": 数字,
    "vitamin_b12": 数字
  }},
  "minerals": {{
    "iron": 数字,
    "calcium": 数字,
    "zinc": 数字,
    "magnesium": 数字
  }}
}}

用户输入的食物描述：{input.input_text}

请直接输出JSON格式，不要有任何其他文字："""
    
    try:
        content = get_ai_response(prompt, model=AI_BACKEND)
        
        # 调试：打印AI返回的原始内容
        print(f"AI Response: {content}")
        
        # 尝试清理响应内容，提取JSON部分
        content = content.strip()
        
        # 如果响应包含多余的文字，尝试提取JSON部分
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        
        # 查找第一个 { 和最后一个 }
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            content = content[start:end+1]
        
        nutrition_data = json.loads(content)
        
        # 保存到数据库
        try:
            # 检查用户是否存在
            result = await db.execute(select(User).where(User.id == current_user.id))
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # 创建餐食记录
            meal = Meal(
                user_id=current_user.id,
                input_text=input.input_text,
                calories=nutrition_data.get('calories', 0),
                protein=nutrition_data.get('protein', 0),
                fat=nutrition_data.get('fat', 0),
                carbohydrates=nutrition_data.get('carbohydrates', 0),
                fiber=nutrition_data.get('fiber', 0),
                sugar=nutrition_data.get('sugar', 0),
                sodium=nutrition_data.get('sodium', 0),
                vitamins=json.dumps(nutrition_data.get('vitamins', {}), ensure_ascii=False),
                minerals=json.dumps(nutrition_data.get('minerals', {}), ensure_ascii=False),
                gpt_raw_response=content
            )
            db.add(meal)
            await db.commit()
            await db.refresh(meal)
            print(f"数据已保存到数据库，记录ID: {meal.id}")
            
            # 更新或创建每日汇总
            today = date.today()
            await update_daily_summary(db, current_user.id, today, nutrition_data)
            
        except Exception as db_error:
            print(f"数据库保存失败: {db_error}")
            # 即使数据库保存失败，也返回营养分析结果
            return nutrition_data
        
        return nutrition_data
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Raw content: {content}")
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON. Raw response: {content[:200]}...")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_daily_summary(db: AsyncSession, user_id: int, date: date, nutrition_data: dict):
    """更新每日营养汇总"""
    # 查找今日汇总记录
    result = await db.execute(
        select(DailySummary).where(
            DailySummary.user_id == user_id,
            DailySummary.date == date
        )
    )
    daily_summary = result.scalar_one_or_none()
    
    if daily_summary:
        # 更新现有记录
        daily_summary.total_calories += nutrition_data.get('calories', 0)
        daily_summary.total_protein += nutrition_data.get('protein', 0)
        daily_summary.total_fat += nutrition_data.get('fat', 0)
        daily_summary.total_carbs += nutrition_data.get('carbohydrates', 0)
        daily_summary.total_fiber += nutrition_data.get('fiber', 0)
        daily_summary.total_sugar += nutrition_data.get('sugar', 0)
    else:
        # 创建新记录
        daily_summary = DailySummary(
            user_id=user_id,
            date=date,
            total_calories=nutrition_data.get('calories', 0),
            total_protein=nutrition_data.get('protein', 0),
            total_fat=nutrition_data.get('fat', 0),
            total_carbs=nutrition_data.get('carbohydrates', 0),
            total_fiber=nutrition_data.get('fiber', 0),
            total_sugar=nutrition_data.get('sugar', 0)
        )
        db.add(daily_summary)
    
    await db.commit()

# 获取用户餐食记录
@app.get("/meals")
async def get_user_meals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    # 只返回当前登录用户的记录
    try:
        result = await db.execute(
            select(Meal).where(Meal.user_id == user_id).order_by(Meal.meal_time.desc())
        )
        meals = result.scalars().all()
        return {
            "user_id": user_id, 
            "meals": [
                {
                    "id": meal.id, 
                    "input_text": meal.input_text,
                    "calories": meal.calories,
                    "protein": meal.protein,
                    "fat": meal.fat,
                    "carbohydrates": meal.carbohydrates,
                    "fiber": meal.fiber,
                    "sugar": meal.sugar,
                    "sodium": meal.sodium,
                    "vitamins": json.loads(str(meal.vitamins)) if meal.vitamins is not None else {},
                    "minerals": json.loads(str(meal.minerals)) if meal.minerals is not None else {},
                    "meal_time": meal.meal_time
                } for meal in meals
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取用户每日汇总
@app.get("/daily_summary")
async def get_daily_summary(
    date_str: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前登录用户的每日营养汇总"""
    try:
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            target_date = date.today()
        
        result = await db.execute(
            select(DailySummary).where(
                DailySummary.user_id == current_user.id,
                DailySummary.date == target_date
            )
        )
        daily_summary = result.scalar_one_or_none()
        
        if daily_summary:
            return {
                "user_id": daily_summary.user_id,
                "date": daily_summary.date.isoformat(),
                "total_calories": daily_summary.total_calories,
                "total_protein": daily_summary.total_protein,
                "total_fat": daily_summary.total_fat,
                "total_carbs": daily_summary.total_carbs,
                "total_fiber": daily_summary.total_fiber,
                "total_sugar": daily_summary.total_sugar,
                "created_at": daily_summary.created_at
            }
        else:
            return {
                "user_id": current_user.id,
                "date": target_date.isoformat(),
                "total_calories": 0,
                "total_protein": 0,
                "total_fat": 0,
                "total_carbs": 0,
                "total_fiber": 0,
                "total_sugar": 0,
                "message": "No data for this date"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取当前用户信息
@app.get("/users/me")
async def get_user_me(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    try:
        print("current_user:", current_user)#debug
        print("current_user.id:", current_user.id)#debug
        print("type(current_user.id):", type(current_user.id))#debug
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "created_at": current_user.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取当前用户profile
@app.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "height": profile.height,
        "weight": profile.weight,
        "target_weight": profile.target_weight,
        "is_vegetarian": profile.is_vegetarian,
        "allergies": profile.allergies,
        "chronic_diseases": profile.chronic_diseases,
        "age": profile.age,
        "gender": profile.gender,
        "updated_at": profile.updated_at
    }

# 新建或更新profile
@app.post("/profile")
async def update_profile(
    profile_in: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if profile:
        for field, value in profile_in.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
    else:
        profile = UserProfile(user_id=current_user.id, **profile_in)
        db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "height": profile.height,
        "weight": profile.weight,
        "target_weight": profile.target_weight,
        "is_vegetarian": profile.is_vegetarian,
        "allergies": profile.allergies,
        "chronic_diseases": profile.chronic_diseases,
        "age": profile.age,
        "gender": profile.gender,
        "updated_at": profile.updated_at
    }

@app.post("/generate_advice")
async def generate_advice(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    summary: dict = Body(...)
):
    # 获取用户profile
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    # 拼接prompt
    prompt = f"""
你是一名专业营养师，请根据以下用户健康档案和今日营养摄入，直接给出个性化饮食建议。

重要要求：
1. 直接给出建议，不要提问或互动
2. 使用准确的中文，避免错别字
3. 用简洁明了的语言回答

用户健康档案：
- 性别: {profile.gender}
- 年龄: {profile.age}
- 身高: {profile.height}cm
- 体重: {profile.weight}kg
- 目标体重: {profile.target_weight}kg
- 是否素食: {"是" if profile.is_vegetarian else "否"}
- 过敏源: {profile.allergies or "无"}
- 慢性疾病: {profile.chronic_diseases or "无"}

今日营养摄入汇总：
- 热量: {summary.get('total_calories', 0)} kcal
- 蛋白质: {summary.get('total_protein', 0)} g
- 脂肪: {summary.get('total_fat', 0)} g
- 碳水: {summary.get('total_carbs', 0)} g
- 膳食纤维: {summary.get('total_fiber', 0)} g
- 糖: {summary.get('total_sugar', 0)} g

请结合用户健康状况、目标和今日摄入，直接给出合理饮食建议。不要提问，直接输出建议内容。
"""

    advice = get_ai_response(prompt, model=AI_BACKEND)
    return {"advice": advice}

@app.post("/generate_meal_advice")
async def generate_meal_advice(
    data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    生成针对单餐的AI建议
    输入：用户描述的食物、AI分析的营养成分
    输出：基于用户profile和本餐营养的个性化建议
    """
    input_text = data.get("input_text", "")
    nutrition = data.get("nutrition", {})
    
    # 获取用户profile信息
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    
    # 构建包含用户profile信息的prompt
    profile_info = ""
    if profile:
        profile_info = f"""
用户健康档案：
- 性别: {profile.gender or '未知'}
- 年龄: {profile.age or '未知'}
- 身高: {profile.height or '未知'}cm
- 体重: {profile.weight or '未知'}kg
- 目标体重: {profile.target_weight or '未知'}kg
- 是否素食: {"是" if profile.is_vegetarian else "否"}
- 过敏源: {profile.allergies or "无"}
- 慢性疾病: {profile.chronic_diseases or "无"}
"""
    
    prompt = f"""
你是一名专业营养师。请根据用户本餐的描述、AI分析的营养成分，以及用户的健康档案，直接给出个性化的饮食建议。

重要要求：
1. 直接给出建议，不要提问或互动
2. 使用准确的中文，避免错别字
3. 用简洁明了的语言回答

用户描述：{input_text}
AI分析的营养成分：{nutrition}
{profile_info}

请结合以下角度直接给出建议：
1. 营养均衡：这餐的营养搭配是否合理
2. 健康目标：基于用户profile（如减肥、增重、控制血糖等）
3. 饮食结构：如何改进这一餐的搭配
4. 后续建议：下一餐或未来几餐的建议

请直接输出建议内容，不要提问。
"""
    
    advice = get_ai_response(prompt, model=AI_BACKEND)
    return {"advice": advice}

@app.post("/change_password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 校验旧密码
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    # 更新新密码
    current_user.password_hash = hash_password(req.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password changed successfully"}


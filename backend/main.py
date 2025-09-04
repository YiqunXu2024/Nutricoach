from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel
import openai
import os
import requests
import json
import re
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

# AI backend config
AI_BACKEND = os.getenv("AI_BACKEND", "ollama")  # optional: "openai", "ollama", "huggingface"

# OpenAI config
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ollama config
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# HuggingFace config
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium")

SECRET_KEY = "your_secret_key"  # use a more complex string
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

app = FastAPI(title="NutriCoach API", description="nutrition analysis API")

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class FoodInput(BaseModel):
    input_text: str  # user's original description

class NutritionResponse(BaseModel):
    calories: float
    protein: float
    fat: float
    carbohydrates: float
    fiber: float
    sugar: float
    sodium: float
    vitamins: dict = {}  # vitamin information
    minerals: dict = {}  # mineral information

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
    """password hash"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """verify password"""
    return hash_password(password) == hashed

@app.post("/register")
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """user register"""
    try:
        # check if username already exists
        result = await db.execute(select(User).where(User.username == user_data.username))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # create new user
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
    # OAuth2PasswordRequestForm automatically gets username and password fields
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
    credentials_exception = HTTPException(status_code=401, detail="invalid credentials")
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
        unified AI call interface, support openai, ollama, huggingface
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
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 300
                    }
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


def format_advice_output(text: str, max_chars: int = 100) -> str:
    """clean AI output, format into points, and strictly limit the length."""
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.replace("\r\n", "\n")
    cleaned = re.sub(r"[^\S\n]+", " ", cleaned)  # keep newlines, merge extra spaces

    # prioritize splitting by newlines/periods/semicolons etc.
    segments = re.split(r"[\n；。;.,，]", cleaned)
    segments = [s.strip() for s in segments if s.strip()]
    if not segments:
        segments = [cleaned]

    # take the first 2-3 items, each item should be less than 30 characters
    bullets = []
    for seg in segments[:3]:
        item = seg
        if len(item) > 30:
            item = item[:30]
        bullets.append(f"• {item}")

    output = "\n".join(bullets[:3])
    if len(output) > max_chars:
        output = output[:max_chars]
    return output


def format_advice_output_words(text: str, max_words: int = 100) -> str:
    """clean AI output, format into points, and strictly limit the number of English words."""
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.replace("\r\n", "\n")
    cleaned = re.sub(r"[^\S\n]+", " ", cleaned)

    # split into points
    segments = re.split(r"[\n.;]\s*", cleaned)
    segments = [s.strip(" -•\t") for s in segments if s.strip()]
    if not segments:
        segments = [cleaned]

    bullets: list[str] = []
    for seg in segments[:3]:
        if not seg:
            continue
        bullets.append(f"• {seg}")

    # limit total length by words
    result_lines: list[str] = []
    used_words = 0
    for b in bullets:
        words = b.split()
        if used_words >= max_words:
            break
        if used_words + len(words) <= max_words:
            result_lines.append(b)
            used_words += len(words)
        else:
            remaining = max_words - used_words
            if remaining > 0:
                result_lines.append(" ".join(words[:remaining]))
                used_words = max_words
            break

    return "\n".join(result_lines)

@app.post("/analyze_food")
async def analyze_food(
    input: FoodInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # now current_user is the authenticated user object
    # you can use current_user.id as user_id
    prompt = f"""
Analyze the nutrition of the following food. Return ONLY a JSON object, no other text.

Food: {input.input_text}

Return format (numbers only, no text):
{{"calories": number, "protein": number, "fat": number, "carbohydrates": number, "fiber": number, "sugar": number, "sodium": number, "vitamins": {{"vitamin_a": 0, "vitamin_c": 0, "vitamin_d": 0, "vitamin_e": 0, "vitamin_b12": 0}}, "minerals": {{"iron": 0, "calcium": 0, "zinc": 0, "magnesium": 0}}}}

JSON:"""
    
    try:
        content = get_ai_response(prompt, model=AI_BACKEND)
        
        # debug: print the original content returned by AI
        print(f"AI Response: {content}")
        
        # clean and extract JSON content
        content = content.strip()
        
        # remove possible markdown code block markers
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        
        # find JSON object
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            content = content[start:end+1]
        
        # clean newlines and extra spaces
        content = content.replace('\n', ' ').replace('\r', ' ')
        content = re.sub(r'\s+', ' ', content)
        
        # fix common JSON format issues
        # 1. replace smart quotes to standard double quotes
        content = content.replace('"', '"').replace('"', '"')
        content = content.replace(''', "'").replace(''', "'")
        
        # 2. remove possible non-printable characters
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
        
        # 3. fix cases where there are quotes but the format is incorrect
        content = re.sub(r'""(\w+)"":', r'"\1":', content)
        
        # 3. check and fix incomplete JSON
        if not content.endswith('}'):
            # if JSON is incomplete, try to complete the missing parts
            open_braces = content.count('{')
            close_braces = content.count('}')
            missing_braces = open_braces - close_braces
            
            # if minerals part is missing, add default values
            if '"minerals"' not in content:
                if content.endswith('"vitamins": { "vitamin_a": 0, "vitamin_c": 0, "vitamin_d": 0, "vitamin_e": 0, "vitamin_b12": 0 }'):
                    content += ', "minerals": { "iron": 0, "calcium": 0, "zinc": 0, "magnesium": 0 }'
            
            # complete missing braces
            content += '}' * missing_braces
        
        print(f"Cleaned JSON: {content}")
        
        # try to parse JSON, if failed, try to fallback to default values
        try:
            nutrition_data = json.loads(content)
        except json.JSONDecodeError as json_error:
            print(f"JSON parse failed: {json_error}")
            print(f"Problematic content: {content}")
            # if parsing fails, return default nutrition data
            nutrition_data = {
                "calories": 300,
                "protein": 15,
                "fat": 10,
                "carbohydrates": 45,
                "fiber": 3,
                "sugar": 5,
                "sodium": 200,
                "vitamins": {
                    "vitamin_a": 0,
                    "vitamin_c": 0,
                    "vitamin_d": 0,
                    "vitamin_e": 0,
                    "vitamin_b12": 0
                },
                "minerals": {
                    "iron": 0,
                    "calcium": 0,
                    "zinc": 0,
                    "magnesium": 0
                }
            }
        
        # save to database
        try:
            # check if user exists
            result = await db.execute(select(User).where(User.id == current_user.id))
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # create meal record
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
            print(f"data saved to database, record ID: {meal.id}")
            
            # update or create daily summary
            today = date.today()
            await update_daily_summary(db, current_user.id, today, nutrition_data)
            
        except Exception as db_error:
            print(f"database save failed: {db_error}")
            # even if database save fails, return nutrition analysis result
            return nutrition_data
        
        return nutrition_data
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Raw content: {content}")
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON. Raw response: {content[:200]}...")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_daily_summary(db: AsyncSession, user_id: int, date: date, nutrition_data: dict):
    """update daily nutrition summary"""
    # find today's summary record
    result = await db.execute(
        select(DailySummary).where(
            DailySummary.user_id == user_id,
            DailySummary.date == date
        )
    )
    daily_summary = result.scalar_one_or_none()
    
    if daily_summary:
        # update existing record
        daily_summary.total_calories += nutrition_data.get('calories', 0)
        daily_summary.total_protein += nutrition_data.get('protein', 0)
        daily_summary.total_fat += nutrition_data.get('fat', 0)
        daily_summary.total_carbs += nutrition_data.get('carbohydrates', 0)
        daily_summary.total_fiber += nutrition_data.get('fiber', 0)
        daily_summary.total_sugar += nutrition_data.get('sugar', 0)
    else:
        # create new record
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

# get user meal records
@app.get("/meals")
async def get_user_meals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    # only return records of the current logged-in user
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

# get user daily summary
@app.get("/daily_summary")
async def get_daily_summary(
    date_str: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """get daily nutrition summary of the current logged-in user"""
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

# get current user info
@app.get("/users/me")
async def get_user_me(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """get current logged-in user info"""
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

# get current user profile
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

# create or update profile
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
    # get user profile
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    # calculate user's goal type
    current_weight = profile.weight or 0
    target_weight = profile.target_weight or 0
    weight_goal = "maintain weight"
    if target_weight > current_weight:
        weight_goal = "GAIN WEIGHT"
    elif target_weight < current_weight:
        weight_goal = "LOSE WEIGHT"
    
    # Prompt for generating daily advice in English
    prompt = f"""
You are a professional dietitian. Based on the user's health profile and today's nutrition summary below, provide personalized dietary advice.

CRITICAL: The user's primary goal is to {weight_goal.upper()}. All advice must align with this goal.

STRICT INSTRUCTIONS:
- Output in Simplified English only and should be full sentences.
- Be concise and to the point. No lengthy explanations.
- No questions or interaction. No emojis or code fences.
- Use accurate English with no typos or garbled text.
- Format as 2–3 brief, actionable bullet points.
- Each point should be one clear, practical suggestion.
- MUST consider the user's weight goal: {weight_goal}

User Profile:
- Gender: {profile.gender or 'Unknown'}
- Age: {profile.age or 'Unknown'}
- Height: {profile.height or 'Unknown'} cm
- Current Weight: {current_weight} kg
- Target Weight: {target_weight} kg
- PRIMARY GOAL: {weight_goal.upper()}
- Vegetarian: {"Yes" if profile.is_vegetarian else "No"}
- Allergies: {profile.allergies or "None"}
- Chronic Diseases: {profile.chronic_diseases or "None"}

Today's Nutrition Summary:
- Calories: {summary.get('total_calories', 0)} kcal
- Protein: {summary.get('total_protein', 0)} g
- Fat: {summary.get('total_fat', 0)} g
- Carbs: {summary.get('total_carbs', 0)} g
- Fiber: {summary.get('total_fiber', 0)} g
- Sugar: {summary.get('total_sugar', 0)} g

Provide advice specifically for someone who wants to {weight_goal.lower()}. Focus on practical steps to achieve this goal.

Respond now.
"""

    try:
        raw_advice = get_ai_response(prompt, model=AI_BACKEND)
        return {"advice": raw_advice}
    except Exception as e:
        print(f"Error generating advice: {e}")
        return {"advice": "• Increase vegetable and fruit intake\n• Control portion size of high-calorie foods\n• Keep it simple and easy to follow."}

@app.post("/generate_meal_advice")
async def generate_meal_advice(
    data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI advice for a single meal.
    Input: user's meal description and AI-analyzed nutrition.
    Output: concise, personalized advice based on the user's profile and this meal's nutrition.
    """
    input_text = data.get("input_text", "")
    nutrition = data.get("nutrition", {})
    
    # Fetch user profile
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    
    # calculate user's goal type
    weight_goal = "maintain weight"
    if profile:
        current_weight = profile.weight or 0
        target_weight = profile.target_weight or 0
        if target_weight > current_weight:
            weight_goal = "GAIN WEIGHT"
        elif target_weight < current_weight:
            weight_goal = "LOSE WEIGHT"
    
    # Build prompt with user profile info
    profile_info = ""
    if profile:
        profile_info = f"""
User Profile:
- Gender: {profile.gender or 'Unknown'}
- Age: {profile.age or 'Unknown'}
- Height: {str(profile.height) + ' cm' if profile.height is not None else 'Unknown'}
- Current Weight: {str(profile.weight) + ' kg' if profile.weight is not None else 'Unknown'}
- Target Weight: {str(profile.target_weight) + ' kg' if profile.target_weight is not None else 'Unknown'}
- PRIMARY GOAL: {weight_goal.upper()}
- Vegetarian: {"Yes" if profile.is_vegetarian else "No"}
- Allergies: {profile.allergies or "None"}
- Chronic Diseases: {profile.chronic_diseases or "None"}
"""
    
    prompt = f"""
You are a professional dietitian. Based on the meal description, the AI-analyzed nutrition, and the user's health profile, provide concise, personalized advice for this meal.

CRITICAL: The user's primary goal is to {weight_goal.upper()}. All advice must align with this goal.

STRICT INSTRUCTIONS:
- Output in English only.
- Be brief and to the point. No lengthy explanations.
- No questions or interaction. No emojis or code fences.
- Use accurate English with no typos or grammatical errors.
- Format as 2–3 short, actionable bullet points.
- Each point should be one clear, practical suggestion.
- MUST consider the user's weight goal: {weight_goal}

Meal Description: {input_text}
AI Nutrition: {nutrition}
{profile_info}

Focus on:
1) Balance and suitability of this meal for someone who wants to {weight_goal.lower()}
2) How this meal aligns with the goal to {weight_goal.lower()}
3) Concrete improvements for next meals to support {weight_goal.lower()}

Provide advice specifically for someone who wants to {weight_goal.lower()}.

Respond now.
"""

    raw_advice = get_ai_response(prompt, model=AI_BACKEND)
    return {"advice": raw_advice}

@app.post("/change_password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # check old password
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    # update new password
    current_user.password_hash = hash_password(req.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password changed successfully"}


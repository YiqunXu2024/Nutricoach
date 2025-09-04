import requests
import json

def test_register():
    """test user registration"""
    url = "http://127.0.0.1:8000/register"
    
    # test registering new user
    test_data = {
        "username": "newuser",
        "password": "password123",
        "email": "newuser@example.com"
    }
    
    try:
        print("testing user registration...")
        response = requests.post(url, json=test_data)
        
        print(f"status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("user registration successful!")
            print(f"user information: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result.get('user_id')
        else:
            print(f"user registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"request failed: {e}")
        return None

def test_login():
    """test user login"""
    url = "http://127.0.0.1:8000/login"
    
    test_data = {
        "username": "newuser",
        "password": "password123"
    }
    
    try:
        print("\ntesting user login...")
        response = requests.post(url, json=test_data)
        
        print(f"status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("user login successful!")
            print(f"login information: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result.get('user_id')
        else:
            print(f"user login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"request failed: {e}")
        return None

def test_analyze_food_with_new_user(user_id):
    """test analyzing food for new user"""
    url = "http://127.0.0.1:8000/analyze_food"
    
    test_data = {
        "input_text": "had a chicken sandwich for lunch today",
        "user_id": user_id
    }
    
    try:
        print(f"\ntesting user {user_id} 's food analysis...")
        response = requests.post(url, json=test_data)
        
        print(f"status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("food analysis successful!")
            print(f"analysis result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"food analysis failed: {response.text}")
            
    except Exception as e:
        print(f"request failed: {e}")

def test_get_user_meals(user_id):
    """test getting user meal records"""
    url = f"http://127.0.0.1:8000/meals/{user_id}"
    
    try:
        print(f"\ntesting user {user_id} 's meal records...")
        response = requests.get(url)
        
        print(f"status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("get meal records successfully!")
            print(f"user {result['user_id']} 's meal records:")
            for meal in result['meals']:
                print(f"  - ID: {meal['id']}, description: {meal['input_text']}")
                print(f"    calories: {meal['calories']}kcal, protein: {meal['protein']}g")
        else:
            print(f"get meal records failed: {response.text}")
            
    except Exception as e:
        print(f"request failed: {e}")

if __name__ == "__main__":
    print("start testing user system...")
    
    # 1. register new user
    new_user_id = test_register()
    
    if new_user_id:
        # 2. login new user
        login_user_id = test_login()
        
        # 3. new user analyze food
        test_analyze_food_with_new_user(new_user_id)
        
        # 4. get new user meal records
        test_get_user_meals(new_user_id)
    
    print("\ntesting completed!") 
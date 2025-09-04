import requests
import json

def test_api():
    """测试API功能"""
    url = "http://127.0.0.1:8000/analyze_food"
    
    # 测试数据
    test_data = {
        "input_text": "had a chicken sandwich for lunch today",
        "user_id": 1
    }
    
    try:
        print("sending request...")
        response = requests.post(url, json=test_data)
        
        print(f"status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(" API call successful!")
            print(f"nutrition analysis result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"API call failed: {response.text}")
            
    except Exception as e:
        print(f"request failed: {e}")

def test_get_meals():
    """test getting user meal records"""
    url = "http://127.0.0.1:8000/meals/1"
    
    try:
        print("\ngetting user meal records...")
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

def test_get_daily_summary():
    """test getting daily summary"""
    url = "http://127.0.0.1:8000/daily_summary/1"
    
    try:
        print("\ngetting daily summary...")
        response = requests.get(url)
        
        print(f"status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("get daily summary successfully!")
            print(f"user {result['user_id']} 's daily summary:")
            print(f"  date: {result['date']}")
            print(f"  total calories: {result['total_calories']}kcal")
            print(f"  total protein: {result['total_protein']}g")
            print(f"  total fat: {result['total_fat']}g")
            print(f"  total carbs: {result['total_carbs']}g")
        else:
            print(f"get daily summary failed: {response.text}")
            
    except Exception as e:
        print(f"request failed: {e}")

def test_get_user():
    """test getting user information"""
    url = "http://127.0.0.1:8000/users/1"
    
    try:
        print("\ngetting user information...")
        response = requests.get(url)
        
        print(f"status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("get user information successfully!")
            print(f"user information: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"get user information failed: {response.text}")
            
    except Exception as e:
        print(f"request failed: {e}")

if __name__ == "__main__":
    print("start testing API...")
    test_api()
    test_get_meals()
    test_get_daily_summary()
    test_get_user()
    print("\ntesting completed!") 
import requests
import json

def test_register():
    """测试用户注册"""
    url = "http://127.0.0.1:8000/register"
    
    # 测试注册新用户
    test_data = {
        "username": "newuser",
        "password": "password123",
        "email": "newuser@example.com"
    }
    
    try:
        print("测试用户注册...")
        response = requests.post(url, json=test_data)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 用户注册成功!")
            print(f"用户信息: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result.get('user_id')
        else:
            print(f"❌ 用户注册失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_login():
    """测试用户登录"""
    url = "http://127.0.0.1:8000/login"
    
    test_data = {
        "username": "newuser",
        "password": "password123"
    }
    
    try:
        print("\n测试用户登录...")
        response = requests.post(url, json=test_data)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 用户登录成功!")
            print(f"登录信息: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result.get('user_id')
        else:
            print(f"❌ 用户登录失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_analyze_food_with_new_user(user_id):
    """测试新用户的营养分析"""
    url = "http://127.0.0.1:8000/analyze_food"
    
    test_data = {
        "input_text": "今天早上吃了一个鸡蛋和一杯牛奶",
        "user_id": user_id
    }
    
    try:
        print(f"\n测试用户 {user_id} 的营养分析...")
        response = requests.post(url, json=test_data)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 营养分析成功!")
            print(f"分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 营养分析失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_get_user_meals(user_id):
    """测试获取新用户的餐食记录"""
    url = f"http://127.0.0.1:8000/meals/{user_id}"
    
    try:
        print(f"\n获取用户 {user_id} 的餐食记录...")
        response = requests.get(url)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取餐食记录成功!")
            print(f"用户 {result['user_id']} 的餐食记录:")
            for meal in result['meals']:
                print(f"  - ID: {meal['id']}, 描述: {meal['input_text']}")
                print(f"    热量: {meal['calories']}卡, 蛋白质: {meal['protein']}g")
        else:
            print(f"❌ 获取餐食记录失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    print("开始测试用户系统...")
    
    # 1. 注册新用户
    new_user_id = test_register()
    
    if new_user_id:
        # 2. 登录新用户
        login_user_id = test_login()
        
        # 3. 新用户进行营养分析
        test_analyze_food_with_new_user(new_user_id)
        
        # 4. 查看新用户的餐食记录
        test_get_user_meals(new_user_id)
    
    print("\n测试完成!") 
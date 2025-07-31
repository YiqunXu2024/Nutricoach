import requests
import json

def test_api():
    """测试API功能"""
    url = "http://127.0.0.1:8000/analyze_food"
    
    # 测试数据
    test_data = {
        "input_text": "今天中午吃了一个鸡肉三明治和一杯咖啡",
        "user_id": 1
    }
    
    try:
        print("发送请求...")
        response = requests.post(url, json=test_data)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功!")
            print(f"营养分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ API调用失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_get_meals():
    """测试获取用户餐食记录"""
    url = "http://127.0.0.1:8000/meals/1"
    
    try:
        print("\n获取用户餐食记录...")
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

def test_get_daily_summary():
    """测试获取每日汇总"""
    url = "http://127.0.0.1:8000/daily_summary/1"
    
    try:
        print("\n获取每日营养汇总...")
        response = requests.get(url)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取每日汇总成功!")
            print(f"用户 {result['user_id']} 的今日营养汇总:")
            print(f"  日期: {result['date']}")
            print(f"  总热量: {result['total_calories']}卡")
            print(f"  总蛋白质: {result['total_protein']}g")
            print(f"  总脂肪: {result['total_fat']}g")
            print(f"  总碳水化合物: {result['total_carbs']}g")
        else:
            print(f"❌ 获取每日汇总失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_get_user():
    """测试获取用户信息"""
    url = "http://127.0.0.1:8000/users/1"
    
    try:
        print("\n获取用户信息...")
        response = requests.get(url)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取用户信息成功!")
            print(f"用户信息: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    print("开始测试API...")
    test_api()
    test_get_meals()
    test_get_daily_summary()
    test_get_user()
    print("\n测试完成!") 
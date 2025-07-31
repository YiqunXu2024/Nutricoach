import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

const String apiBaseUrl = 'http://127.0.0.1:8000'; // iOS模拟器用localhost

Future<http.Response> login(String username, String password) {
  return http.post(
    Uri.parse('$apiBaseUrl/login'),
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'username=$username&password=$password',
  );
}

Future<http.Response> register(String username, String email, String password) {
  return http.post(
    Uri.parse('$apiBaseUrl/register'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'username': username,
      'email': email,
      'password': password,
    }),
  );
}

Future<String?> getToken() async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString('jwt_token');
}

Future<http.Response> getProtectedResource() async {
  final token = await getToken();
  return http.get(
    Uri.parse('$apiBaseUrl/protected'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );
}

Future<Map<String, dynamic>?> fetchDailySummary() async {
  final prefs = await SharedPreferences.getInstance();
  final token = prefs.getString('jwt_token');
  if (token == null) return null;

  final response = await http.get(
    Uri.parse('$apiBaseUrl/daily_summary'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    return null;
  }
}

Future<Map<String, dynamic>?> analyzeFood(String inputText) async {
  final prefs = await SharedPreferences.getInstance();
  final token = prefs.getString('jwt_token');
  if (token == null) return null;

  final response = await http.post(
    Uri.parse('$apiBaseUrl/analyze_food'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'input_text': inputText}),
  );
  print('status: ${response.statusCode}');
  print('body: ${response.body}');
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    return null;
  }
}

Future<List<Map<String, dynamic>>> fetchMeals() async {
  final prefs = await SharedPreferences.getInstance();
  final token = prefs.getString('jwt_token');
  if (token == null) return [];

  final response = await http.get(
    Uri.parse('$apiBaseUrl/meals'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    // data['meals'] 是 List
    return List<Map<String, dynamic>>.from(data['meals']);
  } else {
    return [];
  }
}

Future<Map<String, dynamic>?> fetchProfile() async {
  final token = await getToken();
  final response = await http.get(
    Uri.parse('$apiBaseUrl/profile'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    return null;
  }
}

Future<void> updateProfile(Map<String, dynamic> data) async {
  final token = await getToken();
  final response = await http.post(
    Uri.parse('$apiBaseUrl/profile'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: json.encode(data),
  );
  if (response.statusCode != 200) {
    throw Exception('Failed to update profile');
  }
}

Future<String?> fetchAdvice(Map<String, dynamic> summary) async {
  final token = await getToken();
  final response = await http.post(
    Uri.parse('$apiBaseUrl/generate_advice'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: json.encode(summary),
  );
  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    return data['advice'];
  } else {
    return null;
  }
}

Future<Map<String, dynamic>?> fetchUserMe() async {
  final token = await getToken();
  final response = await http.get(
    Uri.parse('$apiBaseUrl/users/me'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
  );
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    return null;
  }
}

Future<void> changePassword(String oldPassword, String newPassword) async {
  final token = await getToken();
  final response = await http.post(
    Uri.parse('$apiBaseUrl/change_password'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'old_password': oldPassword,
      'new_password': newPassword,
    }),
  );
  if (response.statusCode != 200) {
    throw Exception('Failed to change password');
  }
}

Future<String?> fetchMealAdvice(String inputText, Map<String, dynamic> nutrition) async {
  // 获取针对单餐的AI建议
  // 参数：inputText - 用户描述的食物，nutrition - AI分析的营养成分
  // 返回：AI生成的个性化建议字符串
  final token = await getToken();
  final response = await http.post(
    Uri.parse('$apiBaseUrl/generate_meal_advice'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'input_text': inputText,
      'nutrition': nutrition,
    }),
  );
  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    return data['advice'];
  } else {
    return null;
  }
}

Future<bool> saveMeal(String inputText, Map<String, dynamic> nutrition) async {
  final token = await getToken();
  final response = await http.post(
    Uri.parse('$apiBaseUrl/save_meal'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'input_text': inputText,
      'nutrition': nutrition,
    }),
  );
  return response.statusCode == 200;
}

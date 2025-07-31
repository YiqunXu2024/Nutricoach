import 'package:flutter/material.dart';
import '../services/api_service.dart';

class MealHistoryScreen extends StatefulWidget {
  @override
  _MealHistoryScreenState createState() => _MealHistoryScreenState();
}

class _MealHistoryScreenState extends State<MealHistoryScreen> {
  List<Map<String, dynamic>> allMeals = [];
  Map<String, List<Map<String, dynamic>>> mealsByDate = {};
  String? selectedDate;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadMeals();
  }

  Future<void> _loadMeals() async {
    final data = await fetchMeals();
    setState(() {
      allMeals = data;
      _groupMealsByDate();
      isLoading = false;
    });
  }

  void _groupMealsByDate() {
    mealsByDate.clear();
    
    for (var meal in allMeals) {
      String mealTime = meal['meal_time'] ?? '';
      if (mealTime.isNotEmpty) {
        // 提取日期部分 (YYYY-MM-DD)
        String dateKey = mealTime.split('T')[0];
        
        if (!mealsByDate.containsKey(dateKey)) {
          mealsByDate[dateKey] = [];
        }
        mealsByDate[dateKey]!.add(meal);
      }
    }
    
    // 按日期排序，最新的在前面
    var sortedDates = mealsByDate.keys.toList()..sort((a, b) => b.compareTo(a));
    if (sortedDates.isNotEmpty && selectedDate == null) {
      selectedDate = sortedDates.first;
    }
  }

  String _getMealTypeIcon(String inputText) {
    inputText = inputText.toLowerCase();
    if (inputText.contains('早餐') || inputText.contains('breakfast') || inputText.contains('morning')) {
      return '🌅';
    } else if (inputText.contains('午餐') || inputText.contains('lunch') || inputText.contains('noon')) {
      return '☀️';
    } else if (inputText.contains('晚餐') || inputText.contains('dinner') || inputText.contains('evening')) {
      return '🌙';
    } else if (inputText.contains('零食') || inputText.contains('snack')) {
      return '🍪';
    } else {
      return '🍽️';
    }
  }

  String _formatDate(String dateStr) {
    DateTime date = DateTime.parse(dateStr);
    DateTime now = DateTime.now();
    DateTime today = DateTime(now.year, now.month, now.day);
    DateTime yesterday = today.subtract(Duration(days: 1));
    DateTime mealDate = DateTime(date.year, date.month, date.day);
    
    if (mealDate == today) {
      return '今天';
    } else if (mealDate == yesterday) {
      return '昨天';
    } else {
      return '${date.month}/${date.day}';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('用餐记录'),
        backgroundColor: Colors.green,
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // 日期选择器
                Container(
                  height: 80,
                  padding: EdgeInsets.symmetric(vertical: 8),
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    padding: EdgeInsets.symmetric(horizontal: 16),
                    itemCount: mealsByDate.length,
                    itemBuilder: (context, index) {
                      String dateKey = mealsByDate.keys.elementAt(index);
                      bool isSelected = selectedDate == dateKey;
                      int mealCount = mealsByDate[dateKey]!.length;
                      
                      return GestureDetector(
                        onTap: () {
                          setState(() {
                            selectedDate = dateKey;
                          });
                        },
                        child: Container(
                          width: 70,
                          margin: EdgeInsets.only(right: 12),
                          decoration: BoxDecoration(
                            color: isSelected ? Colors.green : Colors.grey[200],
                            borderRadius: BorderRadius.circular(12),
                            border: isSelected 
                                ? Border.all(color: Colors.green, width: 2)
                                : null,
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                _formatDate(dateKey),
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: isSelected ? Colors.white : Colors.black87,
                                  fontSize: 12,
                                ),
                              ),
                              SizedBox(height: 4),
                              Container(
                                padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: isSelected ? Colors.white.withOpacity(0.3) : Colors.grey[300],
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  '$mealCount 餐',
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: isSelected ? Colors.white : Colors.black54,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                
                // 分割线
                Divider(height: 1),
                
                // 选中日期的餐食记录
                Expanded(
                  child: selectedDate == null || !mealsByDate.containsKey(selectedDate)
                      ? Center(child: Text('暂无记录'))
                      : ListView.builder(
                          padding: EdgeInsets.all(16.0),
                          itemCount: mealsByDate[selectedDate]!.length,
                          itemBuilder: (context, index) {
                            final meal = mealsByDate[selectedDate]![index];
                            String mealTime = meal['meal_time'] ?? '';
                            String timeStr = '';
                            
                            if (mealTime.isNotEmpty) {
                              try {
                                DateTime mealDateTime = DateTime.parse(mealTime);
                                timeStr = '${mealDateTime.hour.toString().padLeft(2, '0')}:${mealDateTime.minute.toString().padLeft(2, '0')}';
                              } catch (e) {
                                timeStr = '';
                              }
                            }
                            
                            return Card(
                              margin: EdgeInsets.only(bottom: 12),
                              elevation: 2,
                              child: ListTile(
                                contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                leading: CircleAvatar(
                                  radius: 18,
                                  backgroundColor: Colors.green,
                                  child: Text(
                                    _getMealTypeIcon(meal['input_text'] ?? ''),
                                    style: TextStyle(fontSize: 14),
                                  ),
                                ),
                                title: Text(
                                  meal['input_text'] ?? '',
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(fontSize: 14),
                                ),
                                subtitle: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    if (timeStr.isNotEmpty)
                                      Text(
                                        '时间: $timeStr',
                                        style: TextStyle(fontSize: 11, color: Colors.grey[600]),
                                      ),
                                    SizedBox(height: 4),
                                    Wrap(
                                      spacing: 6,
                                      runSpacing: 4,
                                      children: [
                                        _buildNutritionChip('热量', '${meal['calories'] ?? 0}', 'kcal'),
                                        _buildNutritionChip('蛋白质', '${meal['protein'] ?? 0}', 'g'),
                                        _buildNutritionChip('碳水', '${meal['carbohydrates'] ?? 0}', 'g'),
                                      ],
                                    ),
                                  ],
                                ),
                                trailing: Icon(Icons.chevron_right, size: 20),
                                onTap: () {
                                  _showMealDetails(meal);
                                },
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }

  Widget _buildNutritionChip(String label, String value, String unit) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 4, vertical: 1),
      decoration: BoxDecoration(
        color: Colors.green.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.green.withOpacity(0.3)),
      ),
      child: Text(
        '$label: $value$unit',
        style: TextStyle(
          fontSize: 9,
          color: Colors.green[700],
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  void _showMealDetails(Map<String, dynamic> meal) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Text(_getMealTypeIcon(meal['input_text'] ?? '')),
            SizedBox(width: 8),
            Expanded(child: Text('餐食详情')),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '食物描述:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 4),
              Text(meal['input_text'] ?? ''),
              SizedBox(height: 16),
              Text(
                '营养成分:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              _buildNutritionRow('热量', '${meal['calories'] ?? 0}', 'kcal'),
              _buildNutritionRow('蛋白质', '${meal['protein'] ?? 0}', 'g'),
              _buildNutritionRow('脂肪', '${meal['fat'] ?? 0}', 'g'),
              _buildNutritionRow('碳水化合物', '${meal['carbohydrates'] ?? 0}', 'g'),
              _buildNutritionRow('膳食纤维', '${meal['fiber'] ?? 0}', 'g'),
              _buildNutritionRow('糖分', '${meal['sugar'] ?? 0}', 'g'),
              _buildNutritionRow('钠', '${meal['sodium'] ?? 0}', 'mg'),
              if (meal['meal_time'] != null) ...[
                SizedBox(height: 16),
                Text(
                  '记录时间:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 4),
                Text(meal['meal_time'].toString().replaceFirst('T', ' ').substring(0, 16)),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            child: Text('关闭'),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }

  Widget _buildNutritionRow(String label, String value, String unit) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            '$value $unit',
            style: TextStyle(fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
} 
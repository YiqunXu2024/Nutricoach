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
        // extract date (YYYY-MM-DD)
        String dateKey = mealTime.split('T')[0];

        if (!mealsByDate.containsKey(dateKey)) {
          mealsByDate[dateKey] = [];
        }
        mealsByDate[dateKey]!.add(meal);
      }
    }

    // sort by date, latest first
    var sortedDates = mealsByDate.keys.toList()..sort((a, b) => b.compareTo(a));
    if (sortedDates.isNotEmpty && selectedDate == null) {
      selectedDate = sortedDates.first;
    }
  }

  String _getMealTypeIcon(String inputText) {
    inputText = inputText.toLowerCase();
    if (inputText.contains('Breakfast') ||
        inputText.contains('breakfast') ||
        inputText.contains('morning')) {
      return '🌅';
    } else if (inputText.contains('Lunch') ||
        inputText.contains('lunch') ||
        inputText.contains('noon')) {
      return '☀️';
    } else if (inputText.contains('Dinner') ||
        inputText.contains('dinner') ||
        inputText.contains('evening')) {
      return '🌙';
    } else if (inputText.contains('Snack') || inputText.contains('snack')) {
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
      return 'Today';
    } else if (mealDate == yesterday) {
      return 'Yesterday';
    } else {
      return '${date.month}/${date.day}';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Meal History'),
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
                                  color: isSelected
                                      ? Colors.white
                                      : Colors.black87,
                                  fontSize: 12,
                                ),
                              ),
                              SizedBox(height: 4),
                              Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 6,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: isSelected
                                      ? Colors.white.withOpacity(0.3)
                                      : Colors.grey[300],
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  '$mealCount Meals',
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: isSelected
                                        ? Colors.white
                                        : Colors.black54,
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

                // divider
                Divider(height: 1),

                // meal list
                Expanded(
                  child:
                      selectedDate == null ||
                          !mealsByDate.containsKey(selectedDate)
                      ? Center(child: Text('No meal history'))
                      : ListView.builder(
                          padding: EdgeInsets.all(16.0),
                          itemCount: mealsByDate[selectedDate]!.length,
                          itemBuilder: (context, index) {
                            final meal = mealsByDate[selectedDate]![index];
                            String mealTime = meal['meal_time'] ?? '';
                            String timeStr = '';

                            if (mealTime.isNotEmpty) {
                              try {
                                DateTime mealDateTime = DateTime.parse(
                                  mealTime,
                                );
                                timeStr =
                                    '${mealDateTime.hour.toString().padLeft(2, '0')}:${mealDateTime.minute.toString().padLeft(2, '0')}';
                              } catch (e) {
                                timeStr = '';
                              }
                            }

                            return Card(
                              margin: EdgeInsets.only(bottom: 12),
                              elevation: 2,
                              child: ListTile(
                                contentPadding: EdgeInsets.symmetric(
                                  horizontal: 16,
                                  vertical: 8,
                                ),
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
                                        'Time: $timeStr',
                                        style: TextStyle(
                                          fontSize: 11,
                                          color: Colors.grey[600],
                                        ),
                                      ),
                                    SizedBox(height: 4),
                                    Wrap(
                                      spacing: 6,
                                      runSpacing: 4,
                                      children: [
                                        _buildNutritionChip(
                                          'Calories',
                                          '${meal['calories'] ?? 0}',
                                          'kcal',
                                        ),
                                        _buildNutritionChip(
                                          'proteins',
                                          '${meal['protein'] ?? 0}',
                                          'g',
                                        ),
                                        _buildNutritionChip(
                                          'carbohydrates',
                                          '${meal['carbohydrates'] ?? 0}',
                                          'g',
                                        ),
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
            Expanded(child: Text('Meal Details')),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Food Description:', style: TextStyle(fontWeight: FontWeight.bold)),
              SizedBox(height: 4),
              Text(meal['input_text'] ?? ''),
              SizedBox(height: 16),
              Text('Nutrition:', style: TextStyle(fontWeight: FontWeight.bold)),
              SizedBox(height: 8),
              _buildNutritionRow('Calories', '${meal['calories'] ?? 0}', 'kcal'),
              _buildNutritionRow('Protein', '${meal['protein'] ?? 0}', 'g'),
              _buildNutritionRow('Fat', '${meal['fat'] ?? 0}', 'g'),
              _buildNutritionRow('Carbohydrates', '${meal['carbohydrates'] ?? 0}', 'g'),
              _buildNutritionRow('Fiber', '${meal['fiber'] ?? 0}', 'g'),
              _buildNutritionRow('Sugar', '${meal['sugar'] ?? 0}', 'g'),
              _buildNutritionRow('Sodium', '${meal['sodium'] ?? 0}', 'mg'),
              if (meal['meal_time'] != null) ...[
                SizedBox(height: 16),
                Text('Record Time:', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 4),
                Text(
                  meal['meal_time']
                      .toString()
                      .replaceFirst('T', ' ')
                      .substring(0, 16),
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            child: Text('Close'),
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
          Text('$value $unit', style: TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}

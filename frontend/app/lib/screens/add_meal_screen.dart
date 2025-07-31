import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AddMealScreen extends StatefulWidget {
  @override
  _AddMealScreenState createState() => _AddMealScreenState();
}

class _AddMealScreenState extends State<AddMealScreen> {
  final TextEditingController _mealDescriptionController = TextEditingController();
  bool _isAnalyzing = false;
  Map<String, dynamic>? nutritionResult;
  String? mealAdvice;
  bool _isAdviceLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Add meal'),
        backgroundColor: Colors.green,
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            children: [
              Text(
                'Describe the food you ate',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 20),
              TextField(
                controller: _mealDescriptionController,
                maxLines: 4,
                decoration: InputDecoration(
                  hintText: 'Recommended format: [Date] [Meal] [Food details]\nExample: 2025-07-23 breakfast: 2 boiled eggs, 1 slice of whole wheat bread, 1 cup of milk',
                  border: OutlineInputBorder(),
                  filled: true,
                  fillColor: Colors.grey[100],
                ),
              ),
              SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  child: _isAnalyzing
                      ? Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            ),
                            SizedBox(width: 10),
                            Text('AI analyzing...'),
                          ],
                        )
                      : Text(
                          'AI analyzing nutrition...',
                          style: TextStyle(fontSize: 18),
                        ),
                  onPressed: _isAnalyzing ? null : _analyzeMeal,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
              SizedBox(height: 20),
              if (nutritionResult != null)
                Card(
                  child: Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'AI analyzing result',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        SizedBox(height: 10),
                        // 展示所有营养成分
                        Wrap(
                          spacing: 20,
                          runSpacing: 10,
                          children: [
                            _buildNutritionResult('Calories', '${nutritionResult!['calories']}', 'kcal'),
                            _buildNutritionResult('Protein', '${nutritionResult!['protein']}', 'g'),
                            _buildNutritionResult('Fat', '${nutritionResult!['fat']}', 'g'),
                            _buildNutritionResult('Carbs', '${nutritionResult!['carbohydrates']}', 'g'),
                            _buildNutritionResult('Fiber', '${nutritionResult!['fiber']}', 'g'),
                            _buildNutritionResult('Sugar', '${nutritionResult!['sugar']}', 'g'),
                            _buildNutritionResult('Sodium', '${nutritionResult!['sodium']}', 'mg'),
                          ],
                        ),
                        SizedBox(height: 20),
                        Container(
                          width: double.infinity,
                          padding: EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                            color: Colors.grey[100],
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'Analysis result has been recorded',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 14,
                            ),
                          ),
                        ),
                        SizedBox(height: 20),
                        Text(
                          'AI advice for this meal',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 5),
                        if (mealAdvice == null && !_isAnalyzing)
                          Center(
                            child: Column(
                              children: [
                                CircularProgressIndicator(),
                                SizedBox(height: 10),
                                Text('Generating AI advice...', style: TextStyle(fontSize: 12, color: Colors.grey)),
                              ],
                            ),
                          )
                        else if (mealAdvice != null)
                          Text(mealAdvice!, style: TextStyle(fontSize: 14)),
                        SizedBox(height: 20),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _analyzeMeal() async {
    if (_mealDescriptionController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('请输入食物描述')),
      );
      return;
    }

    setState(() {
      _isAnalyzing = true;
      nutritionResult = null;
      mealAdvice = null;
    });

    final result = await analyzeFood(_mealDescriptionController.text);

    setState(() {
      _isAnalyzing = false;
      nutritionResult = result;
    });

    if (result == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('AI分析失败，请重试')),
      );
    } else {
      // AI分析成功后，自动生成针对本餐的建议
      final advice = await fetchMealAdvice(_mealDescriptionController.text, result);
      setState(() {
        mealAdvice = advice;
      });
    }
  }

  Widget _buildNutritionResult(String label, String value, String unit) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
        Text(
          unit,
          style: TextStyle(fontSize: 12, color: Colors.grey),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _mealDescriptionController.dispose();
    super.dispose();
  }
} 
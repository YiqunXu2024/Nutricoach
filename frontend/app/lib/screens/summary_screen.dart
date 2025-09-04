import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SummaryScreen extends StatefulWidget {
  @override
  _SummaryScreenState createState() => _SummaryScreenState();
}

class _SummaryScreenState extends State<SummaryScreen> {
  Map<String, dynamic>? summary;
  Map<String, dynamic>? userProfile;
  String? gptAdvice;
  bool isLoading = true;
  bool isAdviceLoading = false;

  // default NHS recommended values
  static const double NHS_CALORIES = 2000;
  static const double NHS_PROTEIN = 65;
  static const double NHS_FAT = 70;
  static const double NHS_CARBS = 300;
  static const double NHS_FIBER = 25;
  static const double NHS_SUGAR = 50;

  double getGoal(String key) {
    if (userProfile != null) {
      // personalized goal based on profile (here is a simple example, can be extended)
      if (key == 'calories' && userProfile!["target_weight"] != null && userProfile!["height"] != null && userProfile!["age"] != null && userProfile!["gender"] != null) {
        // Mifflin-St Jeor formula to estimate basal metabolic rate
        double weight = userProfile!["target_weight"] ?? userProfile!["weight"] ?? 65;
        double height = userProfile!["height"] ?? 170;
        int age = userProfile!["age"] ?? 30;
        String gender = userProfile!["gender"] ?? 'male';
        double bmr = gender == 'female'
            ? 10 * weight + 6.25 * height - 5 * age - 161
            : 10 * weight + 6.25 * height - 5 * age + 5;
        // assume moderate activity, TDEE is about BMR*1.375
        return bmr * 1.375;
      }
      // other indicators can be extended based on profile
    }
    switch (key) {
      case 'calories': return NHS_CALORIES;
      case 'protein': return NHS_PROTEIN;
      case 'fat': return NHS_FAT;
      case 'carbs': return NHS_CARBS;
      case 'fiber': return NHS_FIBER;
      case 'sugar': return NHS_SUGAR;
      default: return 1;
    }
  }

  @override
  void initState() {
    super.initState();
    _loadSummaryAndProfile();
  }

  Future<void> _loadSummaryAndProfile() async {
    setState(() { isLoading = true; });
    final data = await fetchDailySummary();
    final profile = await fetchProfile();
    setState(() {
      summary = data;
      userProfile = profile;
      isLoading = false;
    });
  }

  Future<void> _loadAdvice() async {
    if (summary == null) return;
    setState(() { isAdviceLoading = true; });
    final advice = await fetchAdvice(summary!);
    setState(() {
      gptAdvice = advice;
      isAdviceLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Nutrition summary'),
        backgroundColor: Colors.green,
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : summary == null
              ? Center(child: Text('No data'))
              : Padding(
                  padding: EdgeInsets.all(16.0),
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        // today's summary card
                        Card(
                          child: Padding(
                            padding: EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Today\'s nutrition summary',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                SizedBox(height: 15),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                                  children: [
                                    _buildSummaryItem('Calories', '${summary!["total_calories"]}', 'kcal', Colors.orange),
                                    _buildSummaryItem('Protein', '${summary!["total_protein"]}', 'g', Colors.blue),
                                    _buildSummaryItem('Carbs', '${summary!["total_carbs"]}', 'g', Colors.green),
                                    _buildSummaryItem('Fat', '${summary!["total_fat"]}', 'g', Colors.red),
                                  ],
                                ),
                                SizedBox(height: 10),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                                  children: [
                                    _buildSummaryItem('Fiber', '${summary!["total_fiber"]}', 'g', Colors.brown),
                                    _buildSummaryItem('Sugar', '${summary!["total_sugar"]}', 'g', Colors.purple),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ),
                        SizedBox(height: 20),
                        // progress bar
                        Card(
                          child: Padding(
                            padding: EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Goal completion',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                SizedBox(height: 15),
                                _buildProgressBar('Calories', (summary!["total_calories"] as num).toDouble(), getGoal('calories'), Colors.orange, 'kcal'),
                                SizedBox(height: 10),
                                _buildProgressBar('Protein', (summary!["total_protein"] as num).toDouble(), getGoal('protein'), Colors.blue, 'g'),
                                SizedBox(height: 10),
                                _buildProgressBar('Carbs', (summary!["total_carbs"] as num).toDouble(), getGoal('carbs'), Colors.green, 'g'),
                                SizedBox(height: 10),
                                _buildProgressBar('Fat', (summary!["total_fat"] as num).toDouble(), getGoal('fat'), Colors.red, 'g'),
                                SizedBox(height: 10),
                                _buildProgressBar('Fiber', (summary!["total_fiber"] as num).toDouble(), getGoal('fiber'), Colors.brown, 'g'),
                                SizedBox(height: 10),
                                _buildProgressBar('Sugar', (summary!["total_sugar"] as num).toDouble(), getGoal('sugar'), Colors.purple, 'g'),
                                SizedBox(height: 10),
                                Align(
                                  alignment: Alignment.centerRight,
                                  child: Text(
                                    'Goal Data source: NHS Eatwell Guide',
                                    style: TextStyle(fontSize: 10, color: Colors.grey),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        SizedBox(height: 20),
                        // advice
                        Card(
                          child: Padding(
                            padding: EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Today\'s advice',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                SizedBox(height: 10),
                                if (gptAdvice != null)
                                  Text(
                                    gptAdvice!,
                                    style: TextStyle(fontSize: 14),
                                  )
                                else if (isAdviceLoading)
                                  Center(child: CircularProgressIndicator())
                                else
                                  ElevatedButton(
                                    onPressed: _loadAdvice,
                                    child: Text('Generate personalized advice'),
                                    style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                                  ),
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

  Widget _buildSummaryItem(String label, String value, String unit, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
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

  Widget _buildProgressBar(String label, double value, double goal, Color color, String unit) {
    double progress = value / goal;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label),
            Text('${(progress * 100).toInt()}%  (${value.toStringAsFixed(0)} / ${goal.toStringAsFixed(0)} $unit)'),
          ],
        ),
        SizedBox(height: 5),
        LinearProgressIndicator(
          value: progress.clamp(0.0, 1.0),
          backgroundColor: Colors.grey[300],
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ],
    );
  }
} 
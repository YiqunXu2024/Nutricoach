import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import '../app.dart'; // 导入 routeObserver
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with RouteAware {
  Map<String, dynamic>? summary;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSummary();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // subscribe
    routeObserver.subscribe(this, ModalRoute.of(context)!);
  }

  @override
  void dispose() {
    // unsubscribe
    routeObserver.unsubscribe(this);
    super.dispose();
  }

  // call when pop from other page
  @override
  void didPopNext() {
    _loadSummary();
  }

  Future<void> _loadSummary() async {
    final data = await fetchDailySummary();
    setState(() {
      summary = data;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('NutriCoach'),
        backgroundColor: Colors.green,
        actions: [
          IconButton(
            icon: Icon(Icons.person),
            onPressed: () {
              Navigator.pushNamed(context, '/profile');
            },
          ),
        ],
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: isLoading
            ? Center(child: CircularProgressIndicator())
            : summary == null
                ? Center(child: Text('No data'))
                : Column(
                    children: [
                      // 今日营养概览卡片
                      Card(
                        child: Padding(
                          padding: EdgeInsets.all(16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Today\'s nutrition summary',
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              SizedBox(height: 10),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceAround,
                                children: [
                                  _buildNutritionItem('Calories', '${summary!['total_calories']}', 'kcal'),
                                  _buildNutritionItem('Protein', '${summary!['total_protein']}', 'g'),
                                  _buildNutritionItem('Carbs', '${summary!['total_carbs']}', 'g'),
                                  _buildNutritionItem('Fat', '${summary!['total_fat']}', 'g'),
                                ],
                              ),
                              SizedBox(height: 10),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceAround,
                                children: [
                                  _buildNutritionItem('Fiber', '${summary!['total_fiber']}', 'g'),
                                  _buildNutritionItem('Sugar', '${summary!['total_sugar']}', 'g'),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                      SizedBox(height: 20),
                      
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              icon: Icon(Icons.add),
                              label: Text('Add meal'),
                              onPressed: () async {
                                final result = await Navigator.pushNamed(context, '/add_meal');
                                if (result == true) {
                                  _loadSummary(); 
                                }
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.green,
                                foregroundColor: Colors.white,
                                padding: EdgeInsets.symmetric(vertical: 15),
                              ),
                            ),
                          ),
                          SizedBox(width: 10),
                          Expanded(
                            child: ElevatedButton.icon(
                              icon: Icon(Icons.history),
                              label: Text('Meal history'),
                              onPressed: () {
                                Navigator.pushNamed(context, '/meal_history');
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.blue,
                                foregroundColor: Colors.white,
                                padding: EdgeInsets.symmetric(vertical: 15),
                              ),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 20),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              icon: Icon(Icons.analytics),
                              label: Text('Nutrition summary'),
                              onPressed: () {
                                Navigator.pushNamed(context, '/summary');
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.orange,
                                foregroundColor: Colors.white,
                                padding: EdgeInsets.symmetric(vertical: 15),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
      ),
    );
  }

  Widget _buildNutritionItem(String label, String value, String unit) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
        Text(
          unit,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }
} 
import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/home_screen.dart';
import 'screens/splash_screen.dart';
import 'screens/add_meal_screen.dart';
import 'screens/meal_history_screen.dart';
import 'screens/summary_screen.dart';
import 'screens/profile_screen.dart';

final RouteObserver<ModalRoute<void>> routeObserver = RouteObserver<ModalRoute<void>>();

class NutriCoachApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NutriCoach',
      theme: ThemeData(
        primarySwatch: Colors.green,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      initialRoute: '/splash',
      navigatorObservers: [routeObserver],
      routes: {
        '/splash': (context) => SplashScreen(),
        '/login': (context) => LoginScreen(),
        '/register': (context) => RegisterScreen(),
        '/home': (context) => HomeScreen(),
        '/add_meal': (context) => AddMealScreen(),
        '/meal_history': (context) => MealHistoryScreen(),
        '/summary': (context) => SummaryScreen(),
        '/profile': (context) => ProfileScreen(),
      },
    );
  }
} 
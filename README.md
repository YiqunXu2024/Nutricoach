# NutriCoach - AI-Powered Nutrition Tracking Application

## 📱 Project Overview

NutriCoach is an AI-powered mobile nutrition tracking application that helps users obtain detailed nutritional analysis and personalized dietary recommendations through natural language food descriptions.

## ✨ Key Features

- **Intelligent Nutrition Analysis**: Uses AI to analyze user-inputted food descriptions and provides detailed nutritional information
- **Personalized Recommendations**: Offers customized nutrition advice based on user health profiles and dietary records
- **Calendar View**: View meal records by date with support for historical data review
- **User Profile Management**: Records health information including height, weight, goals, allergies, and more
- **Daily Nutrition Summary**: View daily nutritional intake and goal completion progress

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Development environment database
- **OpenAI API**: AI nutrition analysis
- **JWT**: User authentication

### Frontend
- **Flutter**: Cross-platform mobile application development
- **Dart**: Programming language
- **HTTP**: Network requests
- **Shared Preferences**: Local data storage

## 📁 Project Structure

```
NutriCoach/
├── backend/                 # Backend code
│   ├── main.py             # FastAPI main application
│   ├── db/                 # Database related
│   │   └── db.py          # Data models
│   └── init_db.py         # Database initialization
├── frontend/               # Flutter frontend
│   └── app/
│       └── lib/
│           ├── screens/    # UI components
│           └── services/   # API services
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## 🚀 Quick Start

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Initialize database:
```bash
python init_db.py
```

3. Start FastAPI service:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Install Flutter dependencies:
```bash
cd frontend/app
flutter pub get
```

2. Launch Flutter application:
```bash
flutter run
```

## 📋 Requirements

- Python 3.8+
- Flutter 3.0+
- OpenAI API Key (or alternative AI backend)

## 🔧 Configuration

Configure in `backend/main.py`:
- OpenAI API Key
- Database connection
- AI model selection (OpenAI/Ollama/HuggingFace)

## 📱 Usage Instructions

1. **Register/Login**: Create an account or login to existing account
2. **Complete Profile**: Fill in health information such as height, weight, goals, etc.
3. **Record Meals**: Describe food in natural language to get nutrition analysis
4. **View Recommendations**: Get dietary advice based on personal circumstances
5. **Historical Review**: View historical meal records and nutrition trends

## 💡 Key Innovations

- **Natural Language Processing**: Supports flexible food descriptions in multiple languages
- **Multi-AI Backend Support**: Compatible with OpenAI, Ollama, and HuggingFace models
- **Personalized AI Advice**: Generates recommendations based on individual health profiles
- **Real-time Nutrition Analysis**: Instant processing and feedback for user inputs
- **Cross-platform Compatibility**: Runs on iOS and Android devices

## 🧪 Research Validation

This application has been evaluated through user studies demonstrating:
- **35-50% improvement** in food logging efficiency compared to traditional apps
- **High user satisfaction** with natural language input interface
- **Effective personalization** through AI-driven recommendations

## 🤝 Contributing

This is an academic research project. Suggestions and feedback are welcome for improving the system.

## 📄 License

This project is developed for academic research purposes only.

## 📚 Research Publication

This work contributes to research in:
- Human-Computer Interaction in Health Applications
- Natural Language Processing for Nutrition Analysis
- AI-Powered Personalized Health Recommendations
- Mobile Health Application Design

---

**Development Period**: July 2024 - August 2024  
**Technology Stack**: Flutter, FastAPI, OpenAI API, SQLite, Ollama  
**Research Focus**: Natural Language Processing, AI-Powered Health Applications 

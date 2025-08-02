# NutriCoach - AI驱动的营养追踪应用

## 📱 项目简介

NutriCoach是一个基于AI的移动营养追踪应用，帮助用户通过自然语言输入食物描述，获得详细的营养分析和个性化饮食建议。

## ✨ 主要功能

- **智能营养分析**: 使用AI分析用户输入的食物描述，提供详细的营养成分
- **个性化建议**: 基于用户健康档案和饮食记录，提供定制化的营养建议
- **日历视图**: 按日期查看用餐记录，支持历史数据回顾
- **用户档案管理**: 记录身高、体重、目标、过敏源等健康信息
- **每日营养汇总**: 查看每日营养摄入情况和目标完成度

## 🛠️ 技术栈

### 后端
- **FastAPI**: 高性能Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 开发环境数据库
- **OpenAI API**: AI营养分析
- **JWT**: 用户认证

### 前端
- **Flutter**: 跨平台移动应用开发
- **Dart**: 编程语言
- **HTTP**: 网络请求
- **Shared Preferences**: 本地数据存储

## 📁 项目结构

```
NutriCoach/
├── backend/                 # 后端代码
│   ├── main.py             # FastAPI主应用
│   ├── db/                 # 数据库相关
│   │   └── db.py          # 数据模型
│   └── init_db.py         # 数据库初始化
├── frontend/               # Flutter前端
│   └── app/
│       └── lib/
│           ├── screens/    # 页面组件
│           └── services/   # API服务
├── requirements.txt        # Python依赖
└── README.md              # 项目说明
```

## 🚀 快速开始

### 后端设置

1. 安装Python依赖：
```bash
cd backend
pip install -r requirements.txt
```

2. 初始化数据库：
```bash
python init_db.py
```

3. 启动FastAPI服务：
```bash
uvicorn main:app --reload
```

### 前端设置

1. 安装Flutter依赖：
```bash
cd frontend/app
flutter pub get
```

2. 启动Flutter应用：
```bash
flutter run
```

## 📋 环境要求

- Python 3.8+
- Flutter 3.0+
- OpenAI API Key

## 🔧 配置

在 `backend/main.py` 中配置：
- OpenAI API Key
- 数据库连接
- AI模型选择

## 📱 使用说明

1. **注册/登录**: 创建账户或登录现有账户
2. **完善档案**: 填写身高、体重、目标等健康信息
3. **记录餐食**: 用自然语言描述食物，获得营养分析
4. **查看建议**: 获取基于个人情况的饮食建议
5. **历史回顾**: 查看历史用餐记录和营养趋势

## 🤝 贡献

这是一个学术研究项目，欢迎提出建议和改进意见。

## 📄 许可证

本项目仅用于学术研究目的。

---

**开发时间**: 2024年7月 - 2024年8月  
**技术栈**: Flutter, FastAPI, OpenAI API, SQLite 
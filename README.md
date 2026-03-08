# TitanFit Gym Management System

A modern, professional gym management web application built using **Flask** and **SQLite**. TitanFit is designed for seamless deployment on cloud platforms like **Render**, allowing administrators to manage members, trainers, attendance, payments, and equipment through a clean, high-performance dashboard.

## 🚀 Features

- **📊 Dashboard Analytics**: Real-time statistics and growth tracking.
- **👥 Member Management**: Register, track, and manage gym members.
- **🏋️ Trainer Management**: Track instructors and assigned members.
- **📅 Attendance Tracking**: Modern, interactive daily attendance log.
- **💳 Payment System**: Track transaction status (Paid / Pending).
- **🔧 Equipment Management**: Maintain an inventory of gym equipment.
- **📢 Announcements**: Broadcast system for gym-wide updates.

## 🛠️ Technology Stack

- **Backend**: Python (Flask)
- **Database**: SQLite (Automated initialization)
- **Frontend**: HTML5, Vanilla CSS (Modern UI), JavaScript
- **Styling**: Premium Dark Theme with Glassmorphism
- **Deployment**: Ready for Render / Heroku / DigitalOcean

## ☁️ Cloud Deployment (Render)

This project is optimized for deployment on **Render**:

1. **GitHub**: Push this repository to your GitHub account.
2. **Render**: Create a new **Web Service**.
3. **Runtime**: Select **Python**.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `gunicorn --bind 0.0.0.0:10000 backend.app:app` (or simply `python backend/app.py`)
6. **Environment**: Render will automatically serve the app on port 10000.

## 💻 Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/K-Deepak1610/Gym-Management-System.git
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application**:
   ```bash
   python backend/app.py
   ```
4. **Access in Browser**:
   [http://127.0.0.1:10000](http://127.0.0.1:10000)

*Note: The system automatically creates `database/gym.db` and initializes the schema on first run.*

---
*Developed with ❤️ for TitanFit Gym.*

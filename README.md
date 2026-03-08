# TitanFit Gym Management System

A modern, professional gym management web application built using **Flask** and **MySQL**. TitanFit allows administrators to manage members, trainers, attendance, payments, equipment, and membership renewals through a clean, high-performance dashboard interface.

## 🚀 Features

- **📊 Dashboard Analytics**: Real-time statistics and growth tracking for your gym.
- **👥 Member Management**: Register, track, and manage gym members with ease.
- **🏋️ Trainer Management**: Keep records of trainers and their specializations.
- **📅 Attendance Tracking**: Modern, interactive daily attendance log.
- **💳 Payment System**: Track transaction status (Paid / Pending) and financial history.
- **🔄 Membership Renewal**: Streamlined system for handling member renewals.
- **🤝 Trainer Assignment**: Assign professional trainers to specific members.
- **🔧 Equipment Management**: Maintain an inventory of gym equipment.
- **📢 Announcements**: Broadcast system for gym-wide updates and expiring membership alerts.

## 🛠️ Technology Stack

- **Backend**: Python (Flask)
- **Database**: MySQL
- **Frontend**: HTML5, Vanilla CSS (Modern UI), JavaScript
- **Styling**: Premium Dark Theme with Glassmorphism

## 💻 Installation Guide

Follow these steps to run the project locally:

### 1. Prerequisites
- **Python 3.x** installed.
- **XAMPP** or a standalone **MySQL** server running.

### 2. Install Dependencies
Clone the repository and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Database Setup
1. Start **MySQL** (via XAMPP or local service).
2. Create a database named `titanfit` or run the provided schema:
```bash
# You can use the setup script to initialize the database
python database/setup_db.py
```
*Note: Ensure your database credentials in `backend/db.py` or `.env` are correct.*

### 4. Run the Application
Start the Flask server:

```bash
python backend/app.py
```

### 5. Open in Browser
Visit the following URL in your web browser:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---
*Developed with ❤️ for TitanFit Gym.*

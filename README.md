# 🚀 Smart Attendance System (AI-Powered)

![Banner](assets/banner.png)

## 📝 Project Overview
The **Smart Attendance System** is a professional, AI-driven web application designed to automate and modernize attendance tracking. Leveraging state-of-the-art **Face Recognition** technology and a premium **Glassmorphism UI**, this system provides a seamless experience for both teachers and administrators. It integrates with **Supabase (PostgreSQL)** for robust data persistence and offers detailed analytics.

---

## ✨ Features
- 🔐 **Secure Login**: Personalized access for authorized teachers/administrators.
- 📊 **Dynamic Dashboard**: Real-time analytics with Weekly, Monthly, and Yearly filters.
- 🤖 **AI Face Recognition**: Automatic student identification using advanced computer vision.
- 📹 **Live Camera Verification**: Real-time attendance marking via browser camera.
- 📁 **Manual Override**: Ability to manually mark or verify attendance if needed.
- 📥 **Export Reports**: Generate and download professional Excel reports.
- 💎 **Premium UI**: Modern dark-themed dashboard with futuristic glassmorphism aesthetics.
- ☁️ **Cloud Database**: Integrated with Supabase for reliable and scalable data storage.

---

## 🛠️ Tech Stack
- **Backend**: [Flask](https://flask.palletsprojects.com/) (Python)
- **AI/ML**: [Face Recognition](https://github.com/ageitgey/face_recognition), [OpenCV](https://opencv.org/)
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL) via [SQLAlchemy](https://www.sqlalchemy.org/)
- **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JavaScript
- **Deployment**: [Gunicorn](https://gunicorn.org/), [Heroku](https://www.heroku.com/) / Docker

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Manoranjanchintu/smart-attendance-ai.git
cd smart-attendance-ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the root directory and add the following:
```env
SECRET_KEY=your_secret_key_here
SUPABASE_DB_URL=postgresql://postgres:password@your-db-host:5432/postgres
```

### 5. Initialize Encodings
Ensure you have student images in the `students/` folder and run:
```bash
python encode.py
```

### 6. Run the Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

---

## 🔑 Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret key | `super_secret_key` |
| `SUPABASE_DB_URL` | PostgreSQL connection URL for Supabase | `None` (Required) |

---

## ☁️ Deployment Steps

### Deploying to Heroku
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).
2. Login and create an app:
   ```bash
   heroku login
   heroku create smart-attendance-app
   ```
3. Set Config Vars:
   ```bash
   heroku config:set SECRET_KEY=your_key
   heroku config:set SUPABASE_DB_URL=your_db_url
   ```
4. Push to Heroku:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push heroku main
   ```

---

## 📸 Screenshots
![Login Page](assets/login_page.png)
*(A futuristic glassmorphism login interface for the Smart Attendance System)*

---

## 👤 Author
**Manoranjan Sahoo**
- GitHub: [@Manoranjanchintu](https://github.com/Manoranjanchintu)
- LinkedIn: [Manoranjan Sahoo](https://www.linkedin.com/in/manoranjansahoo1319/)

---

⭐ **If you like this project, please give it a star!**

import os
import json
import base64
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from recognition import identify_faces
from config import Config
from db import db
from models import Student, Attendance
from sqlalchemy.dialects.postgresql import insert

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

STUDENTS_FILE = "students.json"

TEACHER_ID = "ABCD"
PASSWORD = "1234"

def load_students():
    return Student.query.all()

def migrate_students():
    if not os.path.exists(STUDENTS_FILE):
        return
    
    with open(STUDENTS_FILE, "r") as f:
        data = json.load(f)
    
    for roll, info in data.items():
        student = Student.query.filter_by(roll=str(roll)).first()
        if not student:
            new_student = Student(roll=str(roll), name=info["name"], class_name=info["class"])
            db.session.add(new_student)
    
    db.session.commit()

def get_attendance_stats(filter_type="weekly"):
    # Base query
    query = Attendance.query
    
    now = datetime.now()
    if filter_type == "weekly":
        # Last 7 days where attendance was recorded (as per requirements)
        # Actually, requirements say "Last 7 recorded attendance days" 
        # But usually it means last 7 calendar days. 
        # Let's stick to "Last 7 recorded days" by getting distinct dates
        distinct_dates = db.session.query(Attendance.date).distinct().order_by(Attendance.date.desc()).limit(7).all()
        dates = [d[0] for d in distinct_dates]
        if dates:
            query = query.filter(Attendance.date.in_(dates))
        else:
            return {"percentage": 0}
            
    elif filter_type == "monthly":
        month_str = now.strftime("%Y-%m")
        query = query.filter(Attendance.date.like(f"{month_str}%"))
        
    elif filter_type == "yearly":
        year_str = now.strftime("%Y")
        query = query.filter(Attendance.date.like(f"{year_str}%"))

    records = query.all()
    if not records:
        return {"percentage": 0}
        
    total_records = len(records)
    present_records = len([r for r in records if r.status == "Present"])
    
    percentage = (present_records / total_records) * 100 if total_records > 0 else 0
    return {"percentage": round(percentage, 2)}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        teacher_id = request.form.get("teacher_id")
        password = request.form.get("password")
        
        if teacher_id == TEACHER_ID and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "error")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    students = Student.query.all()
    total_students = len(students)
    stats = get_attendance_stats("weekly")
    
    student_list = []
    for s in students:
        # Calculate individual attendance percentage
        total_sessions = Attendance.query.filter_by(roll=s.roll).count()
        present_sessions = Attendance.query.filter_by(roll=s.roll, status="Present").count()
        
        attendance_str = "0%"
        if total_sessions > 0:
            attendance_str = f"{round((present_sessions / total_sessions) * 100)}%"
            
        student_list.append({
            "roll": s.roll,
            "name": s.name,
            "attendance": attendance_str
        })
        
    return render_template("dashboard.html", 
                           total_students=total_students, 
                           weekly_percentage=stats["percentage"],
                           students=student_list)

@app.route("/attendance", methods=["GET"])
def attendance():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    students = Student.query.all()
    student_list = [{"roll": s.roll, "name": s.name} for s in students]
    
    return render_template("attendance.html", students=student_list)

def process_verification(image_bytes, marked_present):
    detected_students = identify_faces(image_bytes)
    detected_rolls = [roll for roll, name in detected_students]
    
    students = Student.query.all()
    
    results = {
        "present": [],
        "false_present": [],
        "absent": [],
        "detected_count": len(detected_rolls),
        "marked_count": len(marked_present),
        "class_strength": len(students)
    }
    
    for student in students:
        roll = student.roll
        is_marked = roll in marked_present
        is_detected = roll in detected_rolls
        
        student_data = {
            "roll": roll, 
            "name": student.name, 
            "image": f"profiles/{student.name.lower()}.jpg"
        }
        
        if is_marked and is_detected:
            results["present"].append(student_data)
        elif is_marked and not is_detected:
            results["false_present"].append(student_data)
        elif not is_marked:
            results["absent"].append(student_data)
            
    return results

@app.route("/verify", methods=["POST"])
def verify_attendance():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
        
    marked_present = json.loads(request.form.get("marked_present", "[]"))
    
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
        
    file = request.files["image"]
    if file.filename == "":
         return jsonify({"error": "No selected file"}), 400
         
    image_bytes = file.read()
    session["verification_results"] = process_verification(image_bytes, marked_present)
    
    return jsonify({"success": True, "redirect": url_for("result")})

@app.route("/verify_live", methods=["POST"])
def verify_live():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    if not data or "image" not in data:
        return jsonify({"error": "No image provided"}), 400
        
    marked_present = data.get("marked_present", [])
    
    image_data = data["image"]
    if "," in image_data:
        image_data = image_data.split(",")[1]
    
    try:
        image_bytes = base64.b64decode(image_data)
    except Exception as e:
        return jsonify({"error": "Invalid image data"}), 400
        
    session["verification_results"] = process_verification(image_bytes, marked_present)
    
    return jsonify({"success": True, "redirect": url_for("result")})

@app.route("/result")
def result():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    results = session.get("verification_results")
    if not results:
        return redirect(url_for("attendance"))
        
    return render_template("result.html", results=results)

@app.route("/submit", methods=["POST"])
def submit_attendance():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    results = session.get("verification_results")
    if not results:
        return redirect(url_for("attendance"))
        
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    attendance_data = []
    
    for s in results["present"]:
        attendance_data.append({"roll": s["roll"], "date": date_str, "time": time_str, "status": "Present"})
        
    for s in results["false_present"]:
        attendance_data.append({"roll": s["roll"], "date": date_str, "time": time_str, "status": "Present"})
        
    for s in results["absent"]:
        attendance_data.append({"roll": s["roll"], "date": date_str, "time": time_str, "status": "Absent"})

    # UPSERT logic using SQLAlchemy's insert (PostgreSQL specific)
    for entry in attendance_data:
        stmt = insert(Attendance).values(
            roll=entry["roll"],
            date=entry["date"],
            time=entry["time"],
            status=entry["status"]
        )
        
        stmt = stmt.on_conflict_do_update(
            constraint='_roll_date_uc',
            set_={"time": entry["time"], "status": entry["status"]}
        )
        db.session.execute(stmt)
    
    db.session.commit()
    session.pop("verification_results", None)
    
    flash("Attendance successfully submitted to Database.", "success")
    return redirect(url_for("dashboard"))

@app.route("/get-dashboard-data", methods=["GET"])
def get_dashboard_data():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
        
    filter_type = request.args.get("filter", "weekly")
    stats = get_attendance_stats(filter_type)
    
    students = Student.query.all()
    student_list = []
    
    # Filter dates based on filter_type for roster table as well if needed?
    # Requirements say "Attendance % = (Present Sessions / Total Recorded Sessions) × 100"
    # and "Downloaded Excel should match selected filter."
    # So the roster should also reflect the selected timeframe.
    
    now = datetime.now()
    date_filter = None
    if filter_type == "weekly":
        distinct_dates = db.session.query(Attendance.date).distinct().order_by(Attendance.date.desc()).limit(7).all()
        date_filter = [d[0] for d in distinct_dates]
    elif filter_type == "monthly":
        date_filter = now.strftime("%Y-%m")
    elif filter_type == "yearly":
        date_filter = now.strftime("%Y")

    for s in students:
        query = Attendance.query.filter_by(roll=s.roll)
        if filter_type == "weekly" and date_filter:
            query = query.filter(Attendance.date.in_(date_filter))
        elif filter_type == "monthly":
            query = query.filter(Attendance.date.like(f"{date_filter}%"))
        elif filter_type == "yearly":
            query = query.filter(Attendance.date.like(f"{date_filter}%"))
            
        total_sessions = query.count()
        present_sessions = query.filter_by(status="Present").count()
        
        attendance_str = "0%"
        if total_sessions > 0:
            attendance_str = f"{round((present_sessions / total_sessions) * 100)}%"
            
        student_list.append({
            "roll": s.roll,
            "name": s.name,
            "attendance": attendance_str
        })
        
    return jsonify({
        "percentage": stats["percentage"],
        "students": student_list
    })

@app.route("/download-report", methods=["GET"])
def download_report():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    filter_type = request.args.get("filter", "weekly")
    
    query = db.session.query(
        Attendance.roll,
        Student.name,
        Student.class_name,
        Attendance.date,
        Attendance.time,
        Attendance.status
    ).join(Student, Attendance.roll == Student.roll)
    
    now = datetime.now()
    if filter_type == "weekly":
        distinct_dates = db.session.query(Attendance.date).distinct().order_by(Attendance.date.desc()).limit(7).all()
        dates = [d[0] for d in distinct_dates]
        if dates:
            query = query.filter(Attendance.date.in_(dates))
    elif filter_type == "monthly":
        query = query.filter(Attendance.date.like(f"{now.strftime('%Y-%m')}%"))
    elif filter_type == "yearly":
        query = query.filter(Attendance.date.like(f"{now.strftime('%Y')}%"))
        
    records = query.all()
    
    df = pd.DataFrame(records, columns=["Roll Number", "Student Name", "Class", "Date", "Time", "Status"])
    
    output_file = f"attendance_report_{filter_type}.xlsx"
    df.to_excel(output_file, index=False)
    
    from flask import send_file
    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        migrate_students()
    
    # Use environment variable for debug mode
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

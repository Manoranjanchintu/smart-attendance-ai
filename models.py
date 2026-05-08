from db import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    roll = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "roll": self.roll,
            "name": self.name,
            "class_name": self.class_name
        }

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll = db.Column(db.String(50), db.ForeignKey('students.roll'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    # Composite unique constraint for roll + date to support UPSERT logic
    __table_args__ = (db.UniqueConstraint('roll', 'date', name='_roll_date_uc'),)

    def to_dict(self):
        return {
            "id": self.id,
            "roll": self.roll,
            "date": self.date,
            "time": self.time,
            "status": self.status
        }

"""
encode.py - Generate face encodings from student images.
Run this once before starting the Flask app:
    python encode.py
"""

import os
import json
import pickle
import face_recognition
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
STUDENTS_DIR = BASE_DIR / "students"
OUTPUT_FILE = BASE_DIR / "encodings.pkl"
STUDENTS_JSON = BASE_DIR / "students.json"


def generate_encodings():
    with open(STUDENTS_JSON, "r") as f:
        students_meta = json.load(f)

    known_encodings = []
    known_roll_numbers = []
    known_names = []

    print("[INFO] Starting face encoding generation...")

    for folder in sorted(STUDENTS_DIR.iterdir()):
        if not folder.is_dir():
            continue

        folder_name = folder.name  # e.g., "101_Nikita"
        parts = folder_name.split("_", 1)
        if len(parts) < 2:
            print(f"[WARN] Skipping folder with unexpected name format: {folder_name}")
            continue

        roll = parts[0]
        student_info = students_meta.get(roll)
        if not student_info:
            print(f"[WARN] Roll {roll} not found in students.json, skipping.")
            continue

        name = student_info["name"]
        image_count = 0

        for img_file in folder.iterdir():
            if img_file.suffix.lower() not in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                continue

            try:
                image = face_recognition.load_image_file(str(img_file))
                encodings = face_recognition.face_encodings(image)

                if len(encodings) == 0:
                    print(f"  [WARN] No face found in {img_file.name}, skipping.")
                    continue

                known_encodings.append(encodings[0])
                known_roll_numbers.append(roll)
                known_names.append(name)
                image_count += 1
                print(f"  [OK] Encoded {img_file.name} for {name} (Roll: {roll})")

            except Exception as e:
                print(f"  [ERROR] Failed to encode {img_file.name}: {e}")

        print(f"[INFO] {name} ({roll}): {image_count} images encoded.")

    data = {
        "encodings": known_encodings,
        "roll_numbers": known_roll_numbers,
        "names": known_names
    }

    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump(data, f)

    total = len(known_encodings)
    print(f"\n[DONE] Encoding complete. {total} face(s) encoded.")
    print(f"[DONE] Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_encodings()

import face_recognition
import pickle
import numpy as np
import cv2

ENCODINGS_FILE = "encodings.pkl"

def load_encodings():
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
        return data["encodings"], data["roll_numbers"], data["names"]
    except FileNotFoundError:
        return [], [], []

def identify_faces(image_bytes):
    known_encodings, known_roll_numbers, known_names = load_encodings()
    
    if not known_encodings:
        return []

    # Convert image bytes to numpy array then to opencv format
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if image is None:
        return []
        
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    detected_students = set()

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"
        roll = "Unknown"

        if True in matches:
            matched_idxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matched_idxs:
                roll_num = known_roll_numbers[i]
                counts[roll_num] = counts.get(roll_num, 0) + 1
            
            roll = max(counts, key=counts.get)
            
            # Find the corresponding name
            name_idx = known_roll_numbers.index(roll)
            name = known_names[name_idx]
            
            detected_students.add((roll, name))

    return list(detected_students)

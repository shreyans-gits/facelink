import os
import sys
import types

venv_site = r"e:\ek-gits\Facelink\venv\Lib\site-packages"
m_dir = os.path.join(venv_site, "face_recognition_models", "models")
m = types.ModuleType("face_recognition_models")
m.pose_predictor_model_location = lambda: os.path.join(m_dir, "shape_predictor_68_face_landmarks.dat")
m.pose_predictor_five_point_model_location = lambda: os.path.join(m_dir, "shape_predictor_5_face_landmarks.dat")
m.face_recognition_model_location = lambda: os.path.join(m_dir, "dlib_face_recognition_resnet_model_v1.dat")
m.cnn_face_detector_model_location = lambda: os.path.join(m_dir, "mmod_human_face_detector.dat")
sys.modules["face_recognition_models"] = m

print("Successfully spoofed face_recognition_models.")

from enrollment import Enrollment

def main():
    enroller = Enrollment()
    db = enroller.load_enrolled()
    
    name = "Shreyans"
    photos = [
        "photos/shreyans0.jpg",
        "photos/shreyans1.jpg",
        "photos/shreyans2.jpg",
        "photos/shreyans3.jpg",
        "photos/shreyans4.jpg"
    ]
    
    print(f"Starting batch enrollment for {name}...")
    for photo_path in photos:
        print(f"Processing: {photo_path}")
        success = enroller.enroll_person(name, photo_path, db)
        
        if not success:
            print(f"Warning: Could not process {photo_path}")

    enroller.save_enrolled(db)
    print(f"Batch enrollment complete! {name} now has {len(db.get(name, []))} samples.")

if __name__ == "__main__":
    main()
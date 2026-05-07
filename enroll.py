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
    photo_path = "photos/shreyans.jpg"
    print (f"Enrolling {name}...")

    success = enroller.enroll_person(name,photo_path,db)
    if success:
        enroller.save_enrolled(db)
        print("Enrollment complete! You can now run main.py")
    else:
        print("Enrollment failed. Check the photo path or if a face is visible.")

if __name__ == "__main__":
    main()
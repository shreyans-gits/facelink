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

import os
import cv2
from detector import Detector
from embedder import Embedder

def collect_embeddings(photo_folder):
    detector = Detector()
    embedder = Embedder()

    results = []
    supported_extensions = ('.jpg','.jpeg','.png')
    all_image_paths = []
    for root, dirs, files in os.walk(photo_folder):
        for file in files:
            if file.lower().endswith(supported_extensions):
                all_image_paths.append(os.path.join(root, file))

    total_images = len(all_image_paths)
    print(f"Found {total_images} images. Starting extraction...")

    for i, photo_path in enumerate(all_image_paths,1):
        print(f"Processing {i}/{total_images}: {os.path.basename(photo_path)}...", end="\r")

        try:
            img = cv2.imread(photo_path)
            if img is None:
                continue

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faces = detector.detect_faces(img_rgb)

            if faces:
                for face_location in faces:
                    embedding = embedder.get_embedding(img_rgb, [face_location])
                    results.append((embedding, photo_path))

        except Exception as e:
            print(f"\nError processing {photo_path}: {e}")
            continue
    
    print(f"\nExtraction complete! Found {len(results)} faces across {total_images} images.")
    return results
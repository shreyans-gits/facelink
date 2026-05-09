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

import numpy as np
from sklearn.cluster import DBSCAN

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


def cluster_faces(embedding_data):
    embeddings = np.array([item[0] for item in embedding_data])
    print(f"Clustering {len(embeddings)} faces...")
    clt = DBSCAN(eps=0.25, min_samples=2, metric='cosine')
    labels = clt.fit_predict(embeddings)
    unique_labels = set(labels)
    num_clusters = len([l for l in unique_labels if l != -1])
    num_noise = list(labels).count(-1)
    print(f"Clustering complete!")
    print(f"-> Found {num_clusters} distinct clusters (people).")
    print(f"-> Identified {num_noise} noise points (outliers).")
    return labels, embedding_data

def show_representative(photo_path):
    img = cv2.imread(photo_path)
    if img is None:
        print(f"Could not read image: {photo_path}")
        return
    
    width = 600
    aspect_ratio = width / float(img.shape[1])
    height = int(img.shape[0] * aspect_ratio)
    resized_img = cv2.resize(img, (width, height))

    cv2.imshow("Who is this? (Press any key to continue)", resized_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

from enrollment import Enrollment

def run_clustering_enrollment(photo_folder):
    embedding_data = collect_embeddings(photo_folder)

    if not embedding_data:
        print("No faces found in the provided folder. Enrollment cancelled.")
        return

    labels, data = cluster_faces(embedding_data)

    enroller = Enrollment()
    db = enroller.load_enrolled()

    unique_labels = set(labels)
    
    for cluster_id in unique_labels:
        if cluster_id == -1:
            continue

        cluster_indices = [i for i, label in enumerate(labels) if label == cluster_id]
        cluster_items = [data[i] for i in cluster_indices]

        representative_path = cluster_items[0][1]
        print(f"\n--- Processing Cluster {cluster_id} ({len(cluster_items)} photos) ---")
        show_representative(representative_path)
        name = input(f"Enter the name for this person (or type 'skip' to ignore): ").strip()

        if name.lower() == 'skip':
            print(f"Skipping cluster {cluster_id}...")
            continue

        if name not in db:
            db[name] = []
        
        print(f"Adding {len(cluster_items)} embeddings to '{name}'...")
        for embedding, _ in cluster_items:
            db[name].append(embedding)

    enroller.save_enrolled(db)
    print("\nBatch enrollment complete! Your database is now updated.")

if __name__ == "__main__":
    takeout_path = "Takeout/Google Photos"
    run_clustering_enrollment(takeout_path)
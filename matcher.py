import config
import numpy as np

threshold = config.SIMILARITY_THRESHOLD

def find_match(embedding,db):
    best_match_name = "Unknown"
    highest_similarity = -1.0

    for name, stored_embedding in db.items():
        dot_product = np.dot(embedding, stored_embedding)
        norm_a = np.linalg.norm(embedding)
        norm_b = np.linalg.norm(stored_embedding)

        similarity = dot_product / (norm_a * norm_b)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match_name = name

    if highest_similarity < threshold:
        return "Unknown"
    
    return best_match_name
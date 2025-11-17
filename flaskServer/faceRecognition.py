# # import os
# # import cv2
# # import numpy as np
# # import torch
# # import requests
# # import time
# # import pandas as pd
# # from datetime import datetime
# # from facenet_pytorch import InceptionResnetV1, MTCNN
# # from sklearn.preprocessing import normalize

# # # ------------------- Configuration -------------------
# # UPLOADS_FOLDER = '../backend/uploads'  # Folder where embeddings are stored
# # API_URL = "http://localhost:3000/mark-attendance"
# # THRESHOLD = 0.65  # Cosine similarity threshold
# # # -----------------------------------------------------

# # # Initialize models
# # mtcnn = MTCNN(keep_all=True)
# # resnet = InceptionResnetV1(pretrained='vggface2').eval()

# # # ------------------- Functions -------------------

# # def detect_and_encode(image):
# #     with torch.no_grad():
# #         boxes, _ = mtcnn.detect(image)
# #         if boxes is not None:
# #             embeddings = []
# #             for box in boxes:
# #                 x1, y1, x2, y2 = map(int, box)
# #                 face = image[y1:y2, x1:x2]
# #                 if face.size == 0:
# #                     continue
# #                 face = cv2.resize(face, (160, 160))
# #                 face = np.transpose(face, (2, 0, 1)).astype(np.float32) / 255.0
# #                 face_tensor = torch.tensor(face).unsqueeze(0)
# #                 encoding = resnet(face_tensor).detach().numpy().flatten()
# #                 embedding = normalize([encoding])[0]
# #                 embeddings.append((embedding, box))
# #             return embeddings
# #     return []

# # def match_embedding(input_embedding):
# #     for person_folder in os.listdir(UPLOADS_FOLDER):
# #         full_path = os.path.join(UPLOADS_FOLDER, person_folder)
# #         csv_path = os.path.join(full_path, 'embeddings.csv')
# #         if not os.path.exists(csv_path):
# #             continue

# #         df = pd.read_csv(csv_path, header=None)
# #         for _, row in df.iterrows():
# #             known_embedding = row.values.astype(float)
# #             known_embedding = normalize([known_embedding])[0]
# #             similarity = np.dot(known_embedding, input_embedding)
# #             if similarity >= THRESHOLD:
# #                 return person_folder
# #     return "Unknown"

# # def mark_attendance(name):
# #     try:
# #         timestamp = datetime.now().isoformat()
# #         response = requests.post(API_URL, json={"name": name, "time": timestamp})
# #         if response.status_code == 200:
# #             print(f"✅ Marked attendance for {name}")
# #             return True
# #         else:
# #             print(f"⚠️ Failed to mark attendance for {name}: {response.status_code}")
# #     except Exception as e:
# #         print(f"❌ Error sending request for {name}: {e}")
# #     return False

# # # ------------------- Main -------------------

# # cap = cv2.VideoCapture(0)
# # marked_names = set()

# # print("🎥 Starting camera. Press 'q' to quit.")

# # while cap.isOpened():
# #     ret, frame = cap.read()
# #     if not ret:
# #         break

# #     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# #     embeddings_with_boxes = detect_and_encode(rgb_frame)

# #     for embedding, box in embeddings_with_boxes:
# #         name = match_embedding(embedding)

# #         x1, y1, x2, y2 = map(int, box)
# #         color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
# #         cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
# #         cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

# #         if name != "Unknown" and name not in marked_names:
# #             if mark_attendance(name):
# #                 marked_names.add(name)

# #     cv2.imshow("Face Recognition Attendance", frame)
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # cap.release()
# # cv2.destroyAllWindows()
# # print("📸 Camera stopped.")

# import os
# import cv2
# import numpy as np
# import torch
# import requests
# import time
# import pandas as pd
# from datetime import datetime
# from facenet_pytorch import InceptionResnetV1, MTCNN
# from sklearn.preprocessing import normalize
# from sklearn.neighbors import NearestNeighbors

# # ------------------- Configuration -------------------
# UPLOADS_FOLDER = '../backend/uploads'  # Folder where embeddings are stored
# API_URL = "http://localhost:3000/mark-attendance"
# THRESHOLD = 0.70  # Cosine similarity threshold
# # -----------------------------------------------------

# # Initialize models
# mtcnn = MTCNN(keep_all=True)
# resnet = InceptionResnetV1(pretrained='vggface2').eval()

# # ------------------- Preload embeddings and build LSH index -------------------

# all_embeddings = []
# all_names = []

# for person_folder in os.listdir(UPLOADS_FOLDER):
#     full_path = os.path.join(UPLOADS_FOLDER, person_folder)
#     csv_path = os.path.join(full_path, 'embeddings.csv')
#     if not os.path.exists(csv_path):
#         continue

#     df = pd.read_csv(csv_path, header=None)
#     for _, row in df.iterrows():
#         known_embedding = row.values.astype(float)
#         known_embedding = normalize([known_embedding])[0]
#         all_embeddings.append(known_embedding)
#         all_names.append(person_folder)

# # Build LSH index
# if all_embeddings:
#     neighbors_model = NearestNeighbors(n_neighbors=1, algorithm='auto', metric='cosine')
#     neighbors_model.fit(all_embeddings)
# else:
#     neighbors_model = None

# # ------------------- Functions -------------------

# def detect_and_encode(image):
#     with torch.no_grad():
#         boxes, _ = mtcnn.detect(image)
#         if boxes is not None:
#             embeddings = []
#             for box in boxes:
#                 x1, y1, x2, y2 = map(int, box)
#                 face = image[y1:y2, x1:x2]
#                 if face.size == 0:
#                     continue
#                 face = cv2.resize(face, (160, 160))
#                 face = np.transpose(face, (2, 0, 1)).astype(np.float32) / 255.0
#                 face_tensor = torch.tensor(face).unsqueeze(0)
#                 encoding = resnet(face_tensor).detach().numpy().flatten()
#                 embedding = normalize([encoding])[0]
#                 embeddings.append((embedding, box))
#             return embeddings
#     return []

# def match_embedding(input_embedding):
#     if neighbors_model is None:
#         return "Unknown"
#     input_embedding = np.array(input_embedding).reshape(1, -1)
#     distances, indices = neighbors_model.kneighbors(input_embedding)
#     if distances[0][0] <= (1 - THRESHOLD):  # cosine similarity threshold converted to distance
#         return all_names[indices[0][0]]
#     return "Unknown"

# def mark_attendance(name):
#     try:
#         timestamp = datetime.now().isoformat()
#         response = requests.post(API_URL, json={"name": name, "time": timestamp})
#         if response.status_code == 200:
#             print(f"✅ Marked attendance for {name}")
#             return True
#         else:
#             print(f"⚠️ Failed to mark attendance for {name}: {response.status_code}")
#     except Exception as e:
#         print(f"❌ Error sending request for {name}: {e}")
#     return False

# # ------------------- Main -------------------

# cap = cv2.VideoCapture(0)
# marked_names = set()

# print("🎥 Starting camera. Press 'q' to quit.")

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     embeddings_with_boxes = detect_and_encode(rgb_frame)

#     for embedding, box in embeddings_with_boxes:
#         name = match_embedding(embedding)

#         x1, y1, x2, y2 = map(int, box)
#         color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
#         cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#         cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

#         if name != "Unknown" and name not in marked_names:
#             if mark_attendance(name):
#                 marked_names.add(name)

#     cv2.imshow("Face Recognition Attendance", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
# print("📸 Camera stopped.")
# New 1



import os
import cv2
import numpy as np
import torch
import requests
import pandas as pd
from PIL import Image
from datetime import datetime
from facenet_pytorch import InceptionResnetV1, MTCNN
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors
from predict import AntiSpoofPredict
from utility import parse_model_name
from ppeDetection import load_ppe_model, detect_ppe_items, check_ppe_compliance, get_ppe_status_string
# ------------------- Configuration -------------------
UPLOADS_FOLDER = '../backend/uploads'
API_URL = "http://localhost:3000/mark-attendance"
THRESHOLD = 0.65  # Cosine similarity threshold (lowered from 0.75 for better recognition)
CACHE_TIMEOUT = 10  # seconds before re-marking same person
# -----------------------------------------------------

# Initialize models
device = 'cuda' if torch.cuda.is_available() else 'cpu'
mtcnn = MTCNN(keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
model_dir = './resources/anti_spoof_models'  # Adjust if needed
anti_spoof = AntiSpoofPredict(device_id=0)

# Initialize PPE detection model
print("[INFO] Initializing PPE detection model...")
ppe_model = load_ppe_model()
if ppe_model is not None:
    print("[INFO] PPE detection model loaded successfully")
else:
    print("[WARNING] PPE detection model not available. PPE checks will be skipped.")



# ------------------- Preload embeddings -------------------
all_embeddings = []
all_names = []

for person_folder in os.listdir(UPLOADS_FOLDER):
    full_path = os.path.join(UPLOADS_FOLDER, person_folder)
    csv_path = os.path.join(full_path, 'embeddings.csv')
    if not os.path.exists(csv_path):
        continue

    df = pd.read_csv(csv_path, header=None)
    for _, row in df.iterrows():
        known_embedding = row.values.astype(float)
        known_embedding = normalize([known_embedding])[0]
        all_embeddings.append(known_embedding)
        all_names.append(person_folder)

# Build similarity search index using scikit-learn (replaces FAISS for better Windows compatibility)
if all_embeddings:
    all_embeddings = np.array(all_embeddings).astype('float32')
    # Use NearestNeighbors with cosine metric for similarity search
    # n_neighbors=1 to get the best match
    index = NearestNeighbors(n_neighbors=1, metric='cosine', algorithm='brute')
    index.fit(all_embeddings)
    print(f"[INFO] Loaded {len(all_embeddings)} embeddings from {len(set(all_names))} person(s)")
    print(f"[INFO] Person names: {', '.join(set(all_names))}")
else:
    index = None
    print("[WARNING] No embeddings found! Face recognition will not work.")

# ------------------- Functions -------------------

def detect_and_encode(image):
    with torch.no_grad():
        boxes, _ = mtcnn.detect(image)
        if boxes is not None:
            embeddings = []
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                face = image[y1:y2, x1:x2]
                if face.size == 0:
                    print("[DEBUG] Empty face crop detected")
                    continue
                face = cv2.resize(face, (160, 160))
                face = np.transpose(face, (2, 0, 1)).astype(np.float32) / 255.0
                face_tensor = torch.tensor(face).unsqueeze(0).to(device)
                encoding = resnet(face_tensor).cpu().detach().numpy().flatten()
                embedding = normalize([encoding])[0]
                embeddings.append((embedding, box))
            return embeddings
        else:
            print("[DEBUG] No faces detected in frame")
    return []

def match_embedding(input_embedding):
    if index is None:
        return "Unknown", 0.0
    input_embedding = np.array(input_embedding).astype('float32').reshape(1, -1)
    
    # scikit-learn NearestNeighbors returns distances, convert to similarity
    # For cosine metric: similarity = 1 - distance (since cosine distance = 1 - cosine similarity)
    distances, indices = index.kneighbors(input_embedding, n_neighbors=1)
    cosine_distance = distances[0][0]
    best_similarity = 1.0 - cosine_distance  # Convert distance to similarity
    best_name = all_names[indices[0][0]]
    
    # Debug: print similarity scores
    if best_similarity < THRESHOLD:
        print(f"[DEBUG] Best match: {best_name} with similarity {best_similarity:.4f} (threshold: {THRESHOLD})")
    
    if best_similarity >= THRESHOLD:
        return best_name, best_similarity
    return "Unknown", best_similarity

def mark_attendance(name, recognition_time, time_taken_seconds, ppe_compliant=False, ppe_items=None, ppe_confidence=0.0):
    try:
        # timestamp = recognition_time.isoformat()
        payload = {
            "name": name,
            # "time": timestamp,
            "recognition_time_seconds": time_taken_seconds,
            "ppe_compliant": ppe_compliant,
            "ppe_items": ppe_items or {},
            "ppe_confidence": ppe_confidence
        }
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            ppe_status = "✅ PPE Compliant" if ppe_compliant else "⚠️ PPE Non-Compliant"
            print(f"✅ Marked attendance for {name} ({time_taken_seconds:.2f}s) - {ppe_status}")
            return True
        else:
            print(f"⚠️ Failed to mark attendance for {name}: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending request for {name}: {e}")
    return False

def is_real_face(frame, box, anti_spoof):
    x1, y1, x2, y2 = map(int, box)
    face_img = frame[y1:y2, x1:x2]
    if face_img.size == 0:
        return False

    # Resize the face image to 80x80
    face_img_resized = cv2.resize(face_img, (80, 80))  # Resize to 80x80

    # Convert NumPy array to PIL image
    face_img_rgb = cv2.cvtColor(face_img_resized, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(face_img_rgb)

    # Build a portable path to the anti-spoofing model relative to this file
    model_path = os.path.join(
        os.path.dirname(__file__),
        "Silent-Face-Anti-Spoofing",
        "resources",
        "anti_spoof_models",
        "2.7_80x80_MiniFASNetV2.pth",
    )
    prediction = anti_spoof.predict(pil_image, model_path)

    # prediction: [label, confidence]
    label = np.argmax(prediction)  # 1 = real, 0 = spoof
    return label == 1  # 1 = real, 0 = spoof



# ------------------- Main -------------------

cap = cv2.VideoCapture(0)
# Track already marked people forever during this session
marked_once = set()


print("🎥 Starting camera. Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    start_time = datetime.now()  
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    embeddings_with_boxes = detect_and_encode(rgb_frame)

    now = datetime.now()

    # Run PPE detection on the full frame (once per frame, not per face)
    ppe_detections = None
    ppe_compliant = False
    ppe_compliance_dict = {}
    ppe_missing = []
    
    if ppe_model is not None:
        try:
            ppe_detections = detect_ppe_items(frame, model=ppe_model)
            ppe_compliant, ppe_missing, ppe_compliance_dict = check_ppe_compliance(ppe_detections)
        except Exception as e:
            print(f"[PPE ERROR] Detection failed: {e}")
            ppe_compliant = True  # Default to compliant if detection fails (don't block attendance)

    for embedding, box in embeddings_with_boxes:
        name, confidence = match_embedding(embedding)
        x1, y1, x2, y2 = map(int, box)

        # 👉 Add this spoof detection step
        if not is_real_face(frame, box,anti_spoof):
            name = "Spoof Detected"
            color = (0, 165, 255)  # Orange box for spoof
        else:
            color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)

            if name != "Unknown" and name not in marked_once:
                recognition_end_time = datetime.now()
                time_taken_seconds = (recognition_end_time - start_time).total_seconds()

                # Prepare PPE data for API
                ppe_items_dict = {}
                ppe_avg_confidence = 0.0
                if ppe_compliance_dict:
                    for item, data in ppe_compliance_dict.items():
                        ppe_items_dict[item] = data["detected"]
                    confidences = [data["confidence"] for data in ppe_compliance_dict.values() if data["detected"]]
                    ppe_avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

                # Mark attendance with PPE status
                # Note: Currently allowing attendance even if PPE non-compliant (can be changed)
                if mark_attendance(name, recognition_end_time, time_taken_seconds, 
                                 ppe_compliant=ppe_compliant, 
                                 ppe_items=ppe_items_dict,
                                 ppe_confidence=ppe_avg_confidence):
                    marked_once.add(name)

        # Draw box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Prepare text with PPE status
        text = f"{name} ({confidence:.2f})"
        if ppe_model is not None and name != "Unknown" and name != "Spoof Detected":
            ppe_status = "✓PPE" if ppe_compliant else "✗PPE"
            text += f" [{ppe_status}]"
        
        cv2.putText(frame, text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Display PPE status on frame
    if ppe_model is not None and ppe_detections:
        ppe_status_text = get_ppe_status_string(ppe_detections, ppe_compliance_dict)
        status_color = (0, 255, 0) if ppe_compliant else (0, 0, 255)
        cv2.putText(frame, f"PPE: {ppe_status_text}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

    cv2.imshow("Face Recognition Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("📸 Camera stopped.")
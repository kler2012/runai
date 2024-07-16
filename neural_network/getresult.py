import os
import tempfile
import cv2
import mediapipe as mp
import math
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import pickle

# Загрузка модели и нормализатора
model = load_model(os.path.join(os.path.dirname(__file__), 'eto.h5'))
with open(os.path.join(os.path.dirname(__file__), 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)

# Настройка MediaPipe Pose
mp_pose = mp.solutions.pose

BODY_LANDMARKS = [
    mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER,
    mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST,
    mp_pose.PoseLandmark.RIGHT_WRIST, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP,
    mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE,
    mp_pose.PoseLandmark.RIGHT_ANKLE, mp_pose.PoseLandmark.LEFT_FOOT_INDEX, mp_pose.PoseLandmark.RIGHT_FOOT_INDEX,
    mp_pose.PoseLandmark.LEFT_HEEL, mp_pose.PoseLandmark.RIGHT_HEEL
]

BODY_LANDMARK_INDICES = [landmark.value for landmark in BODY_LANDMARKS]

def calculate_angle(a, b, c):
    AB = (a[0] - b[0], a[1] - b[1])
    BC = (c[0] - b[0], c[1] - b[1])
    ABBC = AB[0] * BC[0] + AB[1] * BC[1]
    length_AB = math.sqrt(AB[0]**2 + AB[1]**2)
    length_BC = math.sqrt(BC[0]**2 + BC[1]**2)
    cos_angle = ABBC / (length_AB * length_BC)
    angle_radians = math.acos(cos_angle)
    angle_degrees = math.degrees(angle_radians)
    return angle_degrees

def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    temp_processed_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    out = cv2.VideoWriter(temp_processed_video.name, cv2.VideoWriter_fourcc(*'H264'), fps, (frame_width, frame_height))
    out2 = cv2.VideoWriter('outputZ.mp4', cv2.VideoWriter_fourcc(*'H264'), fps, (frame_width, frame_height))
    angles = []

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=2,
        enable_segmentation=False,
        min_tracking_confidence=0.7,
        min_detection_confidence=0.7) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                for landmark_idx in BODY_LANDMARK_INDICES:
                    landmark = landmarks[landmark_idx]
                    if landmark.visibility < 0.7:
                        continue
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

                for connection in mp_pose.POSE_CONNECTIONS:
                    start_idx, end_idx = connection
                    if start_idx in BODY_LANDMARK_INDICES and end_idx in BODY_LANDMARK_INDICES:
                        x0 = int(landmarks[start_idx].x * frame_width)
                        y0 = int(landmarks[start_idx].y * frame_height)
                        x1 = int(landmarks[end_idx].x * frame_width)
                        y1 = int(landmarks[end_idx].y * frame_height)
                        cv2.line(image, (x0, y0), (x1, y1), (0, 255, 0), 1)

                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame_width,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame_height]
                right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * frame_width,
                               landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * frame_height]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * frame_width,
                               landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * frame_height]
                right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x * frame_width,
                             landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y * frame_height]
                right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x * frame_width,
                              landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y * frame_height]
                right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x * frame_width,
                               landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y * frame_height]
                right_foot_index = [landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x * frame_width,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y * frame_height]
                right_heel = [landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x * frame_width,
                              landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y * frame_height]

                right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
                right_foot_angle = calculate_angle(right_heel, right_ankle, right_foot_index)

                angles.append([right_elbow_angle, right_knee_angle, right_foot_angle])

                def draw_text_with_background(img, text, position, font, font_scale, font_color, bg_color, thickness):
                    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
                    text_w, text_h = text_size
                    x, y = position
                    cv2.rectangle(img, (x, y - text_h - 5), (x + text_w, y), bg_color, -1)
                    cv2.putText(img, text, (x, y - 5), font, font_scale, font_color, thickness)

                draw_text_with_background(image, str(int(right_elbow_angle)), 
                                          tuple(np.add(right_elbow, [10, 10]).astype(int)), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), (0, 0, 0), 1)
                draw_text_with_background(image, f'{int(right_foot_angle)}', 
                                          tuple(np.add(right_ankle, [10, 10]).astype(int)), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), (0, 0, 0), 1)
                draw_text_with_background(image, f'{int(right_knee_angle)}', 
                                          tuple(np.add(right_knee, [10, 10]).astype(int)), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), (0, 0, 0), 1)

            out.write(image)
            out2.write(image)

    cap.release()
    out.release()
    out2.release()

    # Преобразование углов в массив numpy и нормализация
    angles = np.array(angles)
    angles_scaled = scaler.transform(angles)

    # Изменение формы данных для LSTM слоя (samples, time steps, features)
    angles_scaled = angles_scaled.reshape((angles_scaled.shape[0], 1, angles_scaled.shape[1]))

    # Предсказание оценок для нового видео
    predictions = model.predict(angles_scaled)

    elbow_scores = predictions[0]
    knee_scores = predictions[1]
    foot_scores = predictions[2]

    # Преобразование предсказаний обратно в исходные классы (0, 1, 2 -> 1, 2, 3)
    elbow_scores = np.argmax(elbow_scores, axis=1) + 1
    knee_scores = np.argmax(knee_scores, axis=1) + 1
    foot_scores = np.argmax(foot_scores, axis=1) + 1

    foot_analysis = f"{foot_scores.mean()}"
    legs_analysis = f"{knee_scores.mean()}"
    arms_analysis = f"{elbow_scores.mean()}"

    return foot_analysis, legs_analysis, arms_analysis, temp_processed_video.name

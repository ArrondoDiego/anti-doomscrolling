import os
import sys
import time
import urllib.request
import cv2
from ffpyplayer.player import MediaPlayer
import mediapipe as mp


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Download automatico del modello se assente
MODEL_PATH = resource_path("face_landmarker.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Download modello MediaPipe in corso...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

VIDEO_PATH = resource_path("video.mp4")
DISTRACTION_SECONDS = 1.5

# Setup MediaPipe
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_faces=1,
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
last_distracted_time = None
last_log_time = 0
frame_idx = 0
cached_distracted = False
cached_h_off = 0.0
h_off = 0.0

# Variabili gestione video meme
video_cap = None
audio_player = None
is_playing_meme = False

with FaceLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        frame_idx += 1
        if frame_idx % 2 == 0:
            small = cv2.resize(frame, (320, 240))
            rgb_frame = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int(time.time() * 1000)
            detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)
            distracted = False
            h_off = 0
            if detection_result.face_landmarks:
                landmarks = detection_result.face_landmarks[0]
                nose = landmarks[1]
                forehead = landmarks[10]
                chin = landmarks[152]
                face_height = chin.y - forehead.y
                if face_height > 0:
                    nose_ratio = (nose.y - forehead.y) / face_height
                    if nose_ratio > 0.68 or chin.y > 0.85:
                        distracted = True
                left_x = landmarks[33].x
                right_x = landmarks[263].x
                eye_w = right_x - left_x
                if eye_w > 0:
                    cx = (left_x + right_x) / 2
                    h_off = abs(nose.x - cx) / eye_w
                    if h_off > 0.18:
                        distracted = True
                cv2.putText(frame, f"h_off:{h_off:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            else:
                distracted = True
            cached_distracted = distracted
            cached_h_off = h_off
        else:
            distracted = cached_distracted
            h_off = cached_h_off

        if not is_playing_meme:
            if distracted:
                if last_distracted_time is None:
                    last_distracted_time = time.time()
                elapsed = time.time() - last_distracted_time
                if time.time() - last_log_time > 0.5:
                    print(f"[{time.strftime('%H:%M:%S')}] DISTRAZIONE {elapsed:.1f}s/{DISTRACTION_SECONDS}s h_off:{h_off:.2f}")
                    last_log_time = time.time()
                if elapsed >= DISTRACTION_SECONDS:
                    print(f"[{time.strftime('%H:%M:%S')}] TRIGGER MEME")
                    if os.path.exists(VIDEO_PATH):
                        video_cap = cv2.VideoCapture(VIDEO_PATH)
                        audio_player = MediaPlayer(VIDEO_PATH)
                        is_playing_meme = True
            else:
                if last_distracted_time is not None:
                    print(f"[{time.strftime('%H:%M:%S')}] Sguardo tornato - reset timer")
                last_distracted_time = None
        else:
            if not distracted:
                print(f"[{time.strftime('%H:%M:%S')}] CONCENTRATO - stop meme")
                if video_cap:
                    video_cap.release()
                    video_cap = None
                if audio_player:
                    audio_player = None
                try:
                    cv2.destroyWindow("MEME ALERT")
                except cv2.error:
                    pass
                is_playing_meme = False
                last_distracted_time = None

        wait_ms = 1
        # Riproduzione video meme - si ferma se torni concentrato
        if is_playing_meme and video_cap is not None:
            v_ret, v_frame = video_cap.read()
            audio_frame, val = audio_player.get_frame() if audio_player else (None, 0)
            if v_ret:
                cv2.imshow("MEME ALERT", v_frame)
                if val != "eof" and val > 0:
                    wait_ms = max(1, int(val * 1000))
            else:
                # Video terminato
                video_cap.release()
                audio_player = None
                cv2.destroyWindow("MEME ALERT")
                is_playing_meme = False
                last_distracted_time = None

        cv2.imshow("Anti Distrazione", frame)
        if cv2.waitKey(wait_ms) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty("Anti Distrazione", cv2.WND_PROP_VISIBLE) < 1:
            break
        if is_playing_meme and cv2.getWindowProperty("MEME ALERT", cv2.WND_PROP_VISIBLE) < 1:
            cv2.destroyWindow("MEME ALERT")
            is_playing_meme = False
            if video_cap:
                video_cap.release()
                video_cap = None
            audio_player = None
            last_distracted_time = None

if video_cap:
    video_cap.release()
cap.release()
cv2.destroyAllWindows()

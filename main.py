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


# Auto-download model if missing
MODEL_PATH = resource_path("face_landmarker.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading MediaPipe model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

PHONE_MODEL_PATH = resource_path("efficientdet_lite0.tflite")
PHONE_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float32/1/efficientdet_lite0.tflite"
if not os.path.exists(PHONE_MODEL_PATH):
    print("Downloading ObjectDetector model...")
    try:
        urllib.request.urlretrieve(PHONE_MODEL_URL, PHONE_MODEL_PATH)
    except Exception as e:
        print(f"Failed to download phone detector: {e}")

VIDEO_PATH = resource_path("video.mp4")
DISTRACTION_SECONDS = 1.5

# Setup MediaPipe
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

face_options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_faces=1,
)
phone_options = ObjectDetectorOptions(
    base_options=BaseOptions(model_asset_path=PHONE_MODEL_PATH),
    score_threshold=0.5,
    max_results=5,
    running_mode=VisionRunningMode.VIDEO,
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
cached_phone = False
h_off = 0.0
phone_detected = False

# Meme video playback variables
video_cap = None
audio_player = None
is_playing_meme = False

phone_detector = None
if os.path.exists(PHONE_MODEL_PATH):
    try:
        phone_detector = ObjectDetector.create_from_options(phone_options)
        print("Phone detector ready")
    except Exception as e:
        print(f"Phone detector unavailable: {e}")

with FaceLandmarker.create_from_options(face_options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        frame_idx += 1
        timestamp_ms = int(time.time() * 1000)
        if frame_idx % 2 == 0:
            small = cv2.resize(frame, (320, 240))
            rgb_frame = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
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
            phone_detected = cached_phone
        else:
            if phone_detector is not None:
                small_p = cv2.resize(frame, (320, 240))
                rgb_p = cv2.cvtColor(small_p, cv2.COLOR_BGR2RGB)
                mp_image_p = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_p)
                phone_result = phone_detector.detect_for_video(mp_image_p, timestamp_ms)
                phone_detected = False
                for det in phone_result.detections:
                    for cat in det.categories:
                        if cat.category_name == "cell phone" and cat.score > 0.5:
                            phone_detected = True
                            box = det.bounding_box
                            x1 = int(box.origin_x * w / 320)
                            y1 = int(box.origin_y * h / 240)
                            x2 = int((box.origin_x + box.width) * w / 320)
                            y2 = int((box.origin_y + box.height) * h / 240)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                            cv2.putText(frame, f"phone {cat.score:.2f}", (x1, max(15, y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            else:
                phone_detected = False
            cached_phone = phone_detected
            distracted = cached_distracted
            h_off = cached_h_off
        if phone_detected:
            cv2.putText(frame, "PHONE", (w-110, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        if time.time() - last_log_time > 0.5 and (distracted or phone_detected):
            print(f"[{time.strftime('%H:%M:%S')}] h_off:{h_off:.2f} phone:{phone_detected} distracted:{distracted}")
            last_log_time = time.time()

        phone_should_play = phone_detected
        should_play = phone_should_play

        if should_play and not is_playing_meme:
            print(f"[{time.strftime('%H:%M:%S')}] TRIGGER MEME (PHONE)")
            if os.path.exists(VIDEO_PATH):
                video_cap = cv2.VideoCapture(VIDEO_PATH)
                audio_player = MediaPlayer(VIDEO_PATH)
                is_playing_meme = True
        elif not should_play and is_playing_meme:
            print(f"[{time.strftime('%H:%M:%S')}] STOP MEME (phone put away)")
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
        # Meme video playback - stops when focus returns
        if is_playing_meme and video_cap is not None:
            v_ret, v_frame = video_cap.read()
            audio_frame, val = audio_player.get_frame() if audio_player else (None, 0)
            if v_ret:
                cv2.imshow("MEME ALERT", v_frame)
                if val != "eof" and val > 0:
                    wait_ms = max(1, int(val * 1000))
            else:
                # Video ended
                video_cap.release()
                audio_player = None
                cv2.destroyWindow("MEME ALERT")
                is_playing_meme = False
                last_distracted_time = None

        cv2.imshow("Anti Distraction", frame)
        if cv2.waitKey(wait_ms) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty("Anti Distraction", cv2.WND_PROP_VISIBLE) < 1:
            break
        if is_playing_meme and cv2.getWindowProperty("MEME ALERT", cv2.WND_PROP_VISIBLE) < 1:
            cv2.destroyWindow("MEME ALERT")
            is_playing_meme = False
            if video_cap:
                video_cap.release()
                video_cap = None
            audio_player = None
            last_distracted_time = None

if phone_detector:
    try:
        phone_detector.close()
    except:
        pass
if video_cap:
    video_cap.release()
cap.release()
cv2.destroyAllWindows()

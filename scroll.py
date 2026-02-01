import cv2
import mediapipe as mp
import pyautogui
import time

# =
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

LIKE_POS = (1250, 430)      
VIDEO_CENTER = (700, 400)   

def scroll_down():
    pyautogui.scroll(-700)
    print("Scroll ke bawah 1 kali")
    return "Scroll ke bawah"

def scroll_up():
    pyautogui.scroll(700)
    print("Scroll ke atas 1 kali")
    return "Scroll ke atas"

def pause_video():
    pyautogui.click(VIDEO_CENTER)
    print("Video dijeda/diputar")
    return "Pause/Play video"

def like_video():
    pyautogui.moveTo(LIKE_POS)
    pyautogui.click()
    print("Video di-like")
    return "Like video"

cap = cv2.VideoCapture(0)
cv2.namedWindow("Gesture Controller", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Gesture Controller", 240, 160)
cv2.moveWindow("Gesture Controller", 10, 10)
cv2.setWindowProperty("Gesture Controller", cv2.WND_PROP_TOPMOST, 1)


last_action_time = 0
action_delay = 0.5        
last_action_text = "Menunggu gesture..."
stable_count = 0          
stable_required = 3       
last_gesture = None


with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.flip(image, 1)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        action_text = None
        now = time.time()
        gesture_detected = None

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                landmarks = hand_landmarks.landmark
                thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP].y
                index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
                ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y
                pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP].y

                # deteksi gesture
                if thumb_tip < index_tip and thumb_tip < middle_tip:
                    gesture_detected = "scroll_down"

                elif index_tip < ring_tip and middle_tip < ring_tip and abs(index_tip - middle_tip) < 0.05:
                    gesture_detected = "scroll_up"

                elif index_tip > thumb_tip and middle_tip > thumb_tip and ring_tip > thumb_tip:
                    gesture_detected = "like"

                elif (thumb_tip > index_tip and 
                      thumb_tip > middle_tip and 
                      thumb_tip > ring_tip and 
                      thumb_tip > pinky_tip):
                    gesture_detected = "pause"

                # gesturnya yah
                if gesture_detected:
                    if gesture_detected == last_gesture:
                        stable_count += 1
                    else:
                        stable_count = 0
                    last_gesture = gesture_detected

                    if stable_count >= stable_required and (now - last_action_time > action_delay):
                        if gesture_detected == "scroll_down":
                            action_text = scroll_down()
                        elif gesture_detected == "scroll_up":
                            action_text = scroll_up()
                        elif gesture_detected == "like":
                            action_text = like_video()
                        elif gesture_detected == "pause":
                            action_text = pause_video()
                            time.sleep(0.2)  

                        last_action_time = now
                        stable_count = 0
                break

        # tulisan di layar
        if action_text:
            last_action_text = action_text

        cv2.rectangle(image, (0, image.shape[0] - 40), (image.shape[1], image.shape[0]), (0, 0, 0), -1)
        cv2.putText(image, f"Aksi: {last_action_text}", (10, image.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(image, f"Stabil: {stable_count}/{stable_required}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA)

        cv2.imshow("Gesture Controller", image)
        key = cv2.waitKey(5) & 0xFF
        if key == 27:  
            break

cap.release()
cv2.destroyAllWindows()
 
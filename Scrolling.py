import cv2, time, pyautogui
import mediapipe as mp

mp_hands= mp.solutions.hands
hands= mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing= mp.solutions.drawing_utils

#Configurations
scroll_speed= 300
scroll_delay= 1
cam_w, cam_h= 640, 480

def detect_gesture(landmarks,handedness):
    fingers= []
    tips= [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]
    for tip in tips:
        if landmarks.landmark[tip].y < landmarks.landmark[tip-2].y:
            fingers.append(1)

    #Thumb
    thumb_tip= landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip= landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    if(handedness == "Right" and thumb_tip.x < thumb_ip.x) or (handedness == "Left" and thumb_tip.x > thumb_ip.x):
        fingers.append(1)
    
    return "scroll_up" if sum(fingers) == 5 else "scroll_down" if len(fingers) == 0 else "none"

cam= cv2.VideoCapture(0)
cam.set(3, cam_w)
cam.set(4, cam_h)

last_scroll= p_time= 0

print("Press 'q' to exit")
while cam.isOpened():
    ret, frame= cam.read()
    if not ret: break

    frame=cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 1)
    results= hands.process(frame)
    gesture, handedness= "none", "Unknown"
    if results.multi_hand_landmarks:
        for hand, handedness_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            handedness= handedness_info.classification[0].label
            gesture= detect_gesture(hand, handedness)
            mp_drawing.draw_landmarks(frame, hand, mp_hands.HAndConnection.HAND_CONNECTIONS)

            if (time.time() - last_scroll) > scroll_delay:
                if gesture == "scroll_up":
                    pyautogui.scroll(scroll_speed)
                    last_scroll= time.time()
                elif gesture == "scroll_down":
                    pyautogui.scroll(-scroll_speed)
                    last_scroll= time.time()

            fps= 1/(time.time()-p_time) if (time.time()-p_time) > 0 else 0
            p_time= time.time()
            cv2.putText(frame, f"FPS: {int(fps)} | Hand: {handedness} | Gesture: {gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            cv2.imshow("Gesture Control", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

#Stop the camera and close the window
cam.release()
cv2.destroyAllWindows()
#End of the code              
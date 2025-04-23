import cv2 as cv
import pyttsx3
import speech_recognition as sr
import threading
import time
from cvzone.HandTrackingModule import HandDetector
from tkinter import Tk, Button, Label
from PIL import Image, ImageTk
import os

# === Text-to-Speech ===
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# === Gesture Labels ===
gestures = [
    'Index Point Gesture', 'V Sign (Peace)', 'Okay Gesture',
    'Horn Sign Gesture', 'ILY Gesture', 'Thumbs Up',
    'Help (Fist) Gesture', 'Call Me Gesture', 'Finger Gun',
    'Wave Gesture', 'Three-Finger Salute'
]

voice_to_gesture = {
    "point": "like.PNG",
    "peace": "four.png",
    "okey": "okey.png",
    "horn": "dislike.jpg",
    "ily": "ily.jpg",
    "thumbs up": "thumbs_up.jpg",
    "help": "help.jpg",
    "call me": "call_me.jpg",
    "gun": "gun.jpg",
    "wave": "wave.jpg",
    "salute": "salute.jpg"
}

# === Finger patterns for gesture recognition ===
finger_patterns = [
    [0, 1, 0, 0, 0],  # Point
    [0, 1, 1, 0, 0],  # Peace
    [1, 0, 1, 1, 1],  # Okay
    [0, 1, 0, 0, 1],  # Horn
    [1, 1, 0, 0, 1],  # ILY
    [1, 0, 0, 0, 0],  # Thumbs Up
    [0, 0, 0, 0, 0],  # Fist / Help
    [1, 0, 0, 0, 1],  # Call Me
    [1, 1, 0, 0, 0],  # Gun
    [1, 1, 1, 1, 1],  # Wave
    [0, 1, 1, 1, 0],  # Salute
]

# === Function: Gesture to Voice ===
def gesture_to_voice():
    cap = cv.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    last_gesture = ""

    while True:
        success, img = cap.read()
        if not success:
            continue

        hands, img = detector.findHands(img)

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)

            for i, pattern in enumerate(finger_patterns):
                if fingers == pattern:
                    gesture = gestures[i]
                    if gesture != last_gesture:
                        print(f"✋ Detected: {gesture}")
                        engine.say(gesture)
                        engine.runAndWait()
                        last_gesture = gesture
                    cv.putText(img, gesture, (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    break

        cv.imshow("Gesture to Voice", img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

# === Function: Voice to Gesture (Shows image) ===
def voice_to_gesture():
    mic_list = sr.Microphone.list_microphone_names()
    print("🎤 Available Microphones:")
    for i, mic_name in enumerate(mic_list):
        print(f"{i}: {mic_name}")

    mic_index = 0  # Change this if needed
    mic = sr.Microphone(device_index=mic_index)

    win = Tk()
    win.title("🗣️ Voice to Gesture Display")
    win.geometry("600x500")
    win.configure(bg="white")

    label = Label(win, text="🎤 Say a gesture...", font=("Arial", 16), bg="white")
    label.pack(pady=10)

    img_label = Label(win, bg="white")
    img_label.pack()

    def listen_and_show():
        while True:
            try:
                with mic as source:
                    label.config(text="🎧 Listening...")
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio).lower()
                    print(f"🗣️ You said: {text}")

                    for keyword, img_file in voice_to_gesture.items():
                        if keyword in text:
                            path = os.path.join("gestures", img_file)
                            if os.path.exists(path):
                                img = Image.open(path)
                                img = img.resize((400, 300))
                                photo = ImageTk.PhotoImage(img)
                                img_label.config(image=photo)
                                img_label.image = photo
                                label.config(text=f"✅ Gesture: {keyword}")
                                engine.say(f"{keyword} gesture")
                                engine.runAndWait()
                            else:
                                label.config(text="❌ Image not found.")
                            break
                    else:
                        label.config(text="❌ Unknown gesture.")
                        engine.say("Unknown gesture")
                        engine.runAndWait()
            except Exception as e:
                print("❌ Voice error:", e)
                label.config(text="❌ Try again...")
            time.sleep(1)

    threading.Thread(target=listen_and_show, daemon=True).start()
    win.mainloop()

# === GUI Interface ===
def create_gui():
    window = Tk()
    window.title("🧠 Sign Language ↔ Voice")
    window.geometry("360x240")
    window.configure(bg="#f0f0f0")

    Label(window, text="Sign Language Translator", font=("Arial", 16), bg="#f0f0f0").pack(pady=10)

    Button(window, text="✋ Gesture to Voice", font=("Arial", 12), width=25, bg="#4CAF50", fg="white",
           command=lambda: threading.Thread(target=gesture_to_voice).start()).pack(pady=10)

    Button(window, text="🗣️ Voice to Gesture (Image)", font=("Arial", 12), width=25, bg="#2196F3", fg="white",
           command=lambda: threading.Thread(target=voice_to_gesture).start()).pack(pady=10)

    Button(window, text="❌ Exit", font=("Arial", 12), width=25, bg="#f44336", fg="white",
           command=window.destroy).pack(pady=10)

    window.mainloop()

# === Run App ===
create_gui()

import cv2
import numpy as np
from fer import FER
import google.generativeai as genai
import speech_recognition as sr
import threading
import time
import pyttsx3
import queue
from picamera2 import Picamera2

# --- Initialize Resources ---
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

detector = FER(mtcnn=False)  # Use lightweight model
recognizer = sr.Recognizer()

# Google AI API Key (Set your API key here)
genai.configure(api_key="YOUR_API_KEY")

language = "en"
user_prompt = ""
res = {}
iteration = 0
listening = False

# --- TTS Worker Thread ---
tts_queue = queue.Queue()
global_tts_engine = None

def tts_worker():
    """Dedicated TTS worker for Raspberry Pi."""
    global global_tts_engine
    engine = pyttsx3.init()
    engine.setProperty("voice", "english-us")
    engine.setProperty("rate", 150)
    global_tts_engine = engine
    while True:
        phrase = tts_queue.get()
        if phrase is None:
            break
        engine.say(phrase)
        try:
            engine.runAndWait()
        except RuntimeError as e:
            print("TTS error:", e)
    engine.stop()

tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak(phrase):
    """Enqueue text for speech output."""
    tts_queue.put(phrase)

# --- Speech Recognition ---
def get_speech():
    global user_prompt, listening
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            if not listening:
                print("Sleeping... Say 'wake up' to activate.")
                audio = recognizer.listen(source)
                try:
                    recognized_text = recognizer.recognize_google(audio).lower()
                    print("Heard:", recognized_text)
                    if "wake up" in recognized_text:
                        print("Wake up command received. Activating listening mode.")
                        listening = True
                except sr.UnknownValueError:
                    print("Could not understand wake-up command.")
                except sr.RequestError as e:
                    print("Speech recognition error:", e)
            else:
                print("Listening for command...")
                audio = recognizer.listen(source)
                try:
                    recognized_text = recognizer.recognize_google(audio).lower()
                    print("Command recognized:", recognized_text)
                    if recognized_text == "close":
                        break
                    user_prompt = recognized_text
                    get_Response(prompt=user_prompt)
                except sr.UnknownValueError:
                    print("Could not understand command.")
                except sr.RequestError as e:
                    print("Speech recognition error:", e)
                listening = False
            time.sleep(0.5)

# --- AI Response ---
def get_Response(emotion_set="", prompt=""):
    global iteration, user_prompt
    if iteration == 0:
        prompt = ["Emotion set = " + str(emotion_set) + "\n\nGenerate a greeting based on this emotion set."]
        iteration = 1
    elif user_prompt == "" and iteration != 0:
        prompt = " "
        print("...waiting for command")
    else:
        prompt = [user_prompt]
    
    try:
        response = genai.generate_text(model="gemini-1.0", contents=prompt)
        reply = response.text.strip()
        print("Generated response:", reply)
        speak(reply)
        return reply
    except Exception as e:
        print("AI response error:", e)
        return "Sorry, I couldn't process that."

# --- Facial Recognition ---
def get_FacialRecognition():
    global res, user_prompt
    while True:
        frame = picam2.capture_array()
        results = detector.detect_emotions(frame)
        if results:
            for result in results:
                emotions = result["emotions"]
                top_emotion = max(emotions, key=emotions.get)
                res = emotions
                print("Detected emotions:", res)
        
        # Exit Condition
        if str(user_prompt).lower() == "close":
            break
        time.sleep(0.1)

# --- Main Execution ---
if __name__ == "__main__":
    face_thread = threading.Thread(target=get_FacialRecognition)
    speech_thread = threading.Thread(target=get_speech)
    response_thread = threading.Thread(target=get_Response, args=(res,))
    
    face_thread.start()
    time.sleep(5)
    response_thread.start()
    time.sleep(5)
    speech_thread.start()
    
    face_thread.join()
    response_thread.join()
    speech_thread.join()
    
    tts_queue.put(None)  # Stop TTS
    picam2.stop()

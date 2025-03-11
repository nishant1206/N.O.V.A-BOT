import cv2
from fer import FER
from google import genai
import speech_recognition as sr
import threading
import time
import pyttsx3
import queue

# Initialize global resources and state
capture = cv2.VideoCapture(0)
client = genai.Client(api_key="AIzaSyDCzWNSkM_TCdDHItZTgCT2sGxjYqcdeaE")
detector = FER(mtcnn=True)
recognizer = sr.Recognizer()

language = "en"

# Global state variables for speech and prompts
user_prompt = ""
res = {}
iteration = 0  # used to check first iteration

# --- TTS Worker Thread Setup ---
tts_queue = queue.Queue()
global_tts_engine = None

def tts_worker():
    """Dedicated TTS worker running its own engine instance."""
    global global_tts_engine
    engine = pyttsx3.init()
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
    """Enqueue a phrase to be spoken."""
    tts_queue.put(phrase)

def interrupt_tts():
    """Clear queued TTS commands and stop ongoing speech."""
    with tts_queue.mutex:
        tts_queue.queue.clear()
    if global_tts_engine:
        global_tts_engine.stop()
    print("TTS interrupted by wake-up call")
# --- End of TTS Worker Setup ---

# State variable to control active listening mode
# When False, the system only listens for the wake-up phrase.
# When True, it listens for the command.
listening = False

def get_speech():
    global user_prompt, listening
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            if not listening:
                print("Sleeping... Say 'wake up' to activate.")
                # Listen briefly for a wake-up phrase
                audio = recognizer.listen(source)
                try:
                    recognized_text = recognizer.recognize_azure(
                        audio,
                        key="1akjNvSqrMp2Ofpz78DV4AvL8Xb9r9ntIExGYUsdEQKSYZ3esBqRJQQJ99BCACGhslBXJ3w3AAAYACOGvZcV",
                        location="centralindia"
                    )
                    recognized_text = recognized_text
                    print("Heard:", recognized_text)
                    if str(recognized_text[0]).lower() == "wake up.":
                        print("Wake up command received. Activating listening mode.")
                        listening = True
                    else:
                        # Not the wake-up phrase; remain asleep.
                        continue
                except sr.UnknownValueError:
                    print("Could not understand audio in wake-up mode.")
                except sr.RequestError as e:
                    print("Speech recognition error: {0}".format(e))
            else:
                print("Listening for command...")
                audio = recognizer.listen(source)
                try:
                    recognized_text = recognizer.recognize_azure(
                        audio,
                        key="1akjNvSqrMp2Ofpz78DV4AvL8Xb9r9ntIExGYUsdEQKSYZ3esBqRJQQJ99BCACGhslBXJ3w3AAAYACOGvZcV",
                        location="centralindia"
                    )
                    recognized_text = recognized_text
                    print("Command recognized:", recognized_text[0])
                    
                    # If command is "close", exit.
                    if recognized_text[0].lower() == "close":
                        break
                    
                    # Process the command.
                    user_prompt = str(recognized_text[0])
                    get_Response(prompt=user_prompt)
                except sr.UnknownValueError:
                    print("Could not understand command.")
                except sr.RequestError as e:
                    print("Speech recognition error: {0}".format(e))
                # After processing a command, revert to sleep mode.
                listening = False
            time.sleep(0.5)

def get_Response(emotion_set="", prompt=""):
    global iteration, user_prompt
    if iteration == 0:
        prompt = ["emotion set = " + str(emotion_set) + "\n\n" +
                  "Generate a Greeting According to This Emotion Set (Just one formal, fancy line)"]
        iteration = 1
    elif user_prompt == "" and iteration != 0:
        prompt = " "
        print("...waiting for command")
    else:
        prompt = [user_prompt]
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    iteration += 1
    print("Generated response:", response.text)
    speak(response.text)
    return response.text

def get_FacialRecognition():
    global res, user_prompt
    while True:
        ret, frame = capture.read()
        if not ret:
            continue
        results = detector.detect_emotions(frame)
        if results:
            for result in results:
                (x, y, w, h) = result["box"]
                emotions = result["emotions"]
                top_emotion = max(emotions, key=emotions.get)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, top_emotion, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                res = emotions
            cv2.imshow("Facial Expression Detection", frame)
            print("Detected emotions:", res)
        if str(user_prompt).lower() == "close":
            capture.release()
            cv2.destroyAllWindows()
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            capture.release()
            cv2.destroyAllWindows()
            break

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
    
    tts_queue.put(None)  # Signal TTS worker to exit

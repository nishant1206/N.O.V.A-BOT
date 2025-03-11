# 🚀 AI-Powered Facial Recognition & Voice Assistant

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python) ![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-red?style=for-the-badge&logo=opencv) ![Azure](https://img.shields.io/badge/Azure-Speech_Recognition-blue?style=for-the-badge&logo=microsoft)

## 📝 Overview
This project is an advanced AI-powered assistant that integrates facial emotion recognition, speech recognition, and text-to-speech (TTS) functionalities. It utilizes various cutting-edge technologies:

- 🎥 **OpenCV** → Real-time facial recognition
- 😊 **FER (Facial Expression Recognition)** → Emotion detection
- 🤖 **Google Generative AI (Gemini 2.0 Flash)** → Response generation
- 🎤 **Azure Speech Recognition** → Voice commands
- 🗣 **Pyttsx3** → Text-to-Speech conversion
- ⚡ **Multithreading** → Parallel execution for efficiency

---

## 📦 Prerequisites
Ensure you have the required dependencies installed:
```bash
pip install opencv-python fer google-generativeai speechrecognition pyttsx3
```

---

## 🏗 Components & Functionality
### 🔹 1. **Global Resources & Initialization**
- 🎬 `cv2.VideoCapture(0)`: Opens webcam for real-time processing.
- 😊 `FER(mtcnn=True)`: Uses MTCNN for face detection and emotion recognition.
- 🗣 `sr.Recognizer()`: Initializes speech recognition.
- 🧠 `genai.Client(api_key=...)`: AI model for response generation.
- 📌 `queue.Queue()`: Implements a queue-based system for speech output.

### 🔹 2. **Text-to-Speech (TTS) Worker**
- Runs in a separate thread using `pyttsx3.init()` for speech synthesis.
- Uses a queue system to handle multiple speech requests.
- Supports interruption and speech clearing.

### 🔹 3. **Speech Recognition & Wake-up Mechanism**
- Listens for the phrase **"wake up"** to activate the assistant.
- Uses **Azure Speech Recognition API** for processing voice commands.
- Commands like **"close"** can terminate the assistant.

### 🔹 4. **Facial Emotion Recognition**
- Captures frames from the webcam and detects facial emotions.
- Displays bounding boxes with emotion labels.
- Updates the emotion state dynamically for AI response generation.

### 🔹 5. **AI Response Generation**
- Generates greetings based on detected emotions.
- Processes user inputs via **Google Generative AI**.
- Uses TTS to read responses aloud.

### 🔹 6. **Multithreading Execution**
Runs the following concurrently:
- **Facial Recognition** → Detects and labels emotions in real-time.
- **Speech Recognition** → Listens for wake-up calls & commands.
- **AI Response Generation** → Creates intelligent responses.

---

## 🚀 Usage
```bash
python script.py
```
1. Say **"wake up"** to activate.
2. Speak a command.
3. The AI processes your command and responds.
4. Say **"close"** to exit.

---

## 🛠 Exit & Cleanup
- 🖼 `cv2.destroyAllWindows()` ensures smooth camera shutdown.
- 🔄 `queue.Queue()` gracefully handles TTS termination.
- 📸 `capture.release()` releases webcam resources.

---

## 🚀 Future Enhancements
✅ Add a GUI for a better user experience.
✅ Support multiple wake-up phrases.
✅ Personalize AI responses using stored user interactions.
✅ Improve noise reduction for better speech accuracy.
✅ Optimize latency for real-time interactions.

---

## 🎯 Conclusion
This **AI-powered assistant** seamlessly combines **facial recognition, speech recognition, and AI-driven responses** to offer a natural and intuitive interaction experience. 🚀💡

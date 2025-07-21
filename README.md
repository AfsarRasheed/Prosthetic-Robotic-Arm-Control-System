# 🦾 Smart Prosthetic Robotic Arm

A multi-modal prosthetic hand powered by gesture recognition, offline voice commands, and Arduino-based real-time servo control. This project aims to build an assistive robotic arm controlled intuitively using hand tracking via webcam or voice instructions—no internet required.



---

## 🎯 Features

- ✋ **Hand Detection Mode** using OpenCV + CVZone
- 🗣️ **Offline Voice Command Mode** using Vosk Speech Recognition
- 🎮 **Rock-Paper-Scissors Mode** for demo/testing control gestures
- 💻 GUI-based mode switching (`tkinter`)
- 🔁 Reconnects to Arduino on failure

---

## 🧰 Hardware Components

- Arduino Uno + Sensor Shield
- 5 × MG996R Servo Motors
- 3D Printed Prosthetic Hand
- USB webcam (for hand detection)
- External microphone (for voice mode)
- 5V regulated power supply for servos

---

## 🧪 Software Stack

| Component     | Libraries/Tools Used                |
|--------------|--------------------------------------|
| Hand detection | `cvzone`, `OpenCV`                 |
| Voice recognition | `vosk`, `sounddevice`, `json`   |
| Serial communication | `pyserial`, `serial.tools.list_ports` |
| GUI/dashboard | `tkinter`, `threading`, `queue`     |

---

## 📦 Installation & Setup

### 1. Clone the Repository


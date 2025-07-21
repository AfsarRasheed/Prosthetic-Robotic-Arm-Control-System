# 🦾 Smart Prosthetic Robotic Arm

A multimodal prosthetic hand that mimics human finger movement via **computer vision**, **offline voice control** (Vosk), and **Arduino-based servo motors**. The system is modular, offline-capable, and intuitive—with gesture, speech, and game-based (rock-paper-scissors) operation, all integrated with a Python GUI (developed in PyCharm).


---

## 🚀 Features

- **Hand Detection:** Live finger tracking using webcam & CVZone
- **Voice Mode (Offline):** Accepts speech commands via Vosk for private, no-internet control
- **Rock-Paper-Scissors Mode:** Play RPS with your prosthetic using voice
- **Tkinter GUI:** Easy mode-switching and visualization
- **Robust Serial Control:** Stable auto-reconnect to Arduino Uno
- **5 DOF Actuation:** 5 servo motors, one per finger, for true dexterity

---

## 🧰 Hardware Components

- Arduino Uno + Sensor Shield  
- 5× MG996R Servo motors  
- 3D Printed Prosthetic Hand  
- USB Webcam  
- Microphone  
- 5V external supply (for servos)

---

## 🧪 Software Requirements

- Python 3.7+
- Arduino IDE
- PyCharm IDE (project developed in PyCharm)
- Windows or Linux
- Webcam & Microphone

#### 📦 Python Libraries

Install in the terminal (PyCharm or command prompt):

pip install opencv-python cvzone pyserial sounddevice vosk


---

## 📁 Directory Structure

prosthetic-robotic-arm/

├── main.py # Hand gesture (basic version, see below)

├── main2.py # Full GUI (all modes, recommended)

├── prosthetic_arm_control.ino # Arduino code

├── vosk-model-small-en-us-0.15/ # Vosk offline speech model

└── README.md


> 🎙 Download Vosk English model: [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)  
> Recommended: `vosk-model-small-en-us-0.15`

---

## 🔧 Arduino Code (`ROBOTICARM.ino`)


**Explanation:**  
- **Data reception:** Waits for a serial message that starts with `$` and has five digits (each for one finger).
- **Parsing:** Each digit is converted to an integer (1 = closed, 0 = open).
- **Actuation:** Corresponding servo is set to `0°` (closed) for `1`, `180°` (open) for `0`.

---

## 🐍 Python Hand Gesture Module (`main.py`)  
**A foundational demo to test webcam-based finger-tracking.**

### **What It Does**

- Uses **OpenCV** & **CVZone** to find your hand and detect if each finger is up/down in real time
- Inverts the finger-up list (`1` becomes `0` = *open*, `0` becomes `1` = *closed*)
- Sends the resulting 5-digit binary (e.g., `$10100`) over serial to Arduino
- If the Arduino port disconnects, it auto-retries connection

### **How the Code Works (Step by Step)**

1. **Serial Connection Functions:**
   - `find_arduino_port()`: Searches all COM ports for an Arduino
   - `connect_serial()`: Tries to connect, auto-retries on error
   - `send_data()`: Packages the finger data, sends over USB to Arduino

2. **Hand Tracking Loop:**
   - Initializes webcam and CVZone detector
   - On each frame:
     - Captures landmarks and finger states
     - If state changes, inverts it, prints, and sends via serial
     - Handles big disruptions with auto-disconnect/reconnect logic

3. **Termination:**
   - User can exit by pressing `'q'`, which releases camera and closes windows

### **Typical Usage Flow**
1. Start Arduino code (`ROBOTICARM.ino`)
2. Run `python main.py` in PyCharm or terminal
3. Make hand gestures in front of webcam; each change updates Arduino-controlled fingers

---

## 🖥 Python GUI (`main2.py`) – All Modes!

A full-featured Tkinter GUI to select between:

1. **Hand Detection Mode**  
   - Webcam tracks hand, deduces 5-finger states  
   - Real-time servo actuation

2. **Voice Mode**  
   - Listens for the words: one, two, three, four, five  
   - Maps each voice number to a finger pattern

3. **Rock-Paper-Scissors**  
   - Listens for: "rock", "paper", "scissors"  
   - Matches:
     - Rock → `[1, 1, 1, 1, 1]`
     - Paper → `[0, 0, 0, 0, 0]`
     - Scissors → `[1, 0, 0, 1, 1]`

### **Sample Patterns**

| Action/Command | Pattern            |
|----------------|--------------------|
| All Open       | `[0, 0, 0, 0, 0]`  |
| All Closed     | `[1, 1, 1, 1, 1]`  |
| "Two"          | `[1, 0, 0, 1, 1]`  |
| "Rock"         | `[1, 1, 1, 1, 1]`  |
| "Paper"        | `[0, 0, 0, 0, 0]`  |
| "Scissors"     | `[1, 0, 0, 1, 1]`  |

---

## 🔌 Serial Data Format

- Python sends: `$ABCDE`  
  Where A-E are `[Thumb, Index, Middle, Ring, Pinky]`
- `1` = finger closed (servo 0°), `0` = open (servo 180°)
- Arduino reads and actuates each finger accordingly

---

## ⚙️ Running & Usage

1. **Upload** the Arduino code via Arduino IDE
2. **Run** `main2.py` in PyCharm (or other terminal)
3. **Switch modes** in the GUI (`Hand Detection`, `Voice Recognition`, `Rock Paper Scissors`)
4. **Interact:** Show gestures, speak commands, or play RPS—servo fingers respond in real time

---

## 🛠️ Troubleshooting

| Symptom                    | Solution                                |
|----------------------------|-----------------------------------------|
| Arduino not detected       | Update `PORT` in code, check wiring     |
| Camera error               | Try changing webcam index to `1` or `2` |
| Mic not working            | Check permissions, device availability  |
| Servos not moving          | Use external 5V power, check wiring     |
| Vosk error                 | Ensure model folder path is correct     |

---

## 👨‍🏫 Special Thanks

Project completed with the guidance and mentorship of **Abhiram**.

---

## 📝 License

Licensed under the **MIT License**.  
Re-use, fork, or expand for your own assistive robotics—and please share your work back!

---

## 🤝 Contributions

- Suggestions, issues, and pull requests always welcome!
- If you create a new mode, fix a bug, or adapt for another prosthetic—let me know and tag the repo.

---

🎯 *Built with PyCharm. Powered by OpenCV, CVZone, Vosk & Arduino.*

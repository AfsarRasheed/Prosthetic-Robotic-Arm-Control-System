# 🦾 Smart Prosthetic Robotic Arm

A multimodal prosthetic robotic arm that mimics human hand movement using **computer vision**, **offline voice recognition**, and **Arduino-controlled servo motors**. This system supports **gesture-based**, **voice-based**, and **game-based (rock-paper-scissors)** control—making it intuitive, offline-capable, and modular.



---

## 🚀 Features

- ✋ **Hand Detection Mode**: Detects finger positions using webcam + CVZone
- 🗣️ **Offline Voice Control Mode**: Responds to speech input via Vosk (offline)
- 🎮 **Rock-Paper-Scissors Mode**: Uses voice to play RPS gestures
- 🖥️ GUI built with `tkinter` to switch between modes
- 🔌 Reliable auto-reconnect serial communication with Arduino Uno
- 🦿 Controls 3D-printed robotic fingers using 5 servo motors

---

## 🧰 Hardware Components

- Arduino Uno + Sensor Shield  
- 5× MG996R Servo motors  
- 3D Printed Prosthetic Arm  
- USB Webcam  
- Microphone  
- 5V external power supply (for servos)

---

## 🧪 Software Requirements

- Python 3.7 or higher  
- Arduino IDE  
- Webcam & Microphone  
- Windows or Linux  

### 📦 Python Libraries

Install these in PyCharm via terminal or project interpreter:

pip install opencv-python cvzone pyserial sounddevice vosk


---

## 📁 Directory Structure

prosthetic-robotic-arm/
├── main.py # Simple hand-control version

├── main2.py # Full multimode GUI version (recommended)

├── prosthetic_arm_control.ino # Arduino code

├── vosk-model-small-en-us-0.15/ # Offline speech model directory

└── README.md


> 🎙 Download Vosk English model from: [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)  
> Suggested model: `vosk-model-small-en-us-0.15`

---

## 🔧 Arduino Code (`prosthetic_arm_control.ino`)

#define numOfValsRec 5
#define digitsPerValRec 1

#include <Servo.h>

Servo servoThumb, servoIndex, servoMiddle, servoRing, servoPinky;
int valsRec[numOfValsRec] = {0, 0, 0, 0, 0};
String recievedString = "";
bool receiving = false;

void setup() {
Serial.begin(9600);
servoThumb.attach(9);
servoIndex.attach(10);
servoMiddle.attach(13);
servoRing.attach(3);
servoPinky.attach(11);
updateServos();
}

void recieveData() {
while (Serial.available()) {
char c = Serial.read();
if (c == '$') {
recievedString = "";
receiving = true;
} else if (receiving) {
recievedString += c;
if (recievedString.length() >= numOfValsRec * digitsPerValRec) {
receiving = false;
for (int i = 0; i < numOfValsRec; i++) {
int pos = i * digitsPerValRec;
valsRec[i] = recievedString.substring(pos, pos + digitsPerValRec).toInt();
}
updateServos();
}
}
}
}

void updateServos() {
servoThumb.write(valsRec == 1 ? 0 : 180);
servoIndex.write(valsRec == 1 ? 0 : 180);
servoMiddle.write(valsRec == 1 ? 0 : 180);
servoRing.write(valsRec == 1 ? 0 : 180);
servoPinky.write(valsRec == 1 ? 0 : 180);
}

void loop() {
recieveData();
}


---
## 🐍 Python GUI Overview

Project contains **two Python files**:

### `main.py` – Hand Gesture Control (basic)  
- Detects fingers using `cvzone`  
- Sends inverted binary (open/closed) finger states to Arduino  
- Format: `$10101`

---
### `main2.py` – Full GUI (all 3 modes)

#### 🧭 Modes:

1. **Hand Detection Mode**  
   - Webcam detects fingers and sends data via Serial.

2. **Offline Voice Mode**  
   - VOSK listens for: one, two, three, four, five  
   - Maps each to pre-defined finger bit patterns

3. **Rock-Paper-Scissors Mode (RPS)**  
   - Voice detects: “rock”, “paper”, “scissors”  
   - Maps to:
     - Rock → `[1,1,1,1,1]`
     - Paper → `[0,0,0,0,0]`
     - Scissors → `[1,0,0,1,1]`

---

### ✅ Run the Program

python main2.py

### 🗂️ Sample Finger Patterns

| Action     | Pattern            |
|------------|--------------------|
| All Open   | `[0, 0, 0, 0, 0]`  |
| All Closed | `[1, 1, 1, 1, 1]`  |
| "Two"      | `[1, 0, 0, 1, 1]`  |
| "Rock"     | `[1, 1, 1, 1, 1]`  |
| "Paper"    | `[0, 0, 0, 0, 0]`  |
| "Scissors" | `[1, 0, 0, 1, 1]`  |

### 🎤 Voice Input Mappings

**Number Mode:**

| Command | Pattern             |
|---------|---------------------|
| One     | `[1, 0, 1, 1, 1]`   |
| Two     | `[1, 0, 0, 1, 1]`   |
| Three   | `[1, 1, 0, 0, 0]`   |
| Four    | `[1, 0, 0, 0, 0]`   |
| Five    | `[0, 0, 0, 0, 0]`   |

**RPS Mode:**

| Command     | Pattern             |
|-------------|---------------------|
| Rock        | `[1, 1, 1, 1, 1]`   |
| Paper       | `[0, 0, 0, 0, 0]`   |
| Scissors    | `[1, 0, 0, 1, 1]`   |

---

## 🔌 Serial Communication

All Python code sends a 5-bit binary string (e.g., `$10110`) via USB serial to Arduino Uno. The string is parsed and each digit controls one servo corresponding to:
[Thumb, Index, Middle, Ring, Pinky]


1 = finger closed → servo at 0°  
0 = finger open → servo at 180°

---

## 🛠️ Troubleshooting

- ❌ **Not detecting Arduino?**
  - Check `PORT = "comX"` in `main2.py` matches your system’s COM port.
- 🎥 **Webcam not working?**
  - Check OpenCV camera index (`cv2.VideoCapture(0)`) or drivers.
- 🔇 **Microphone not recognized?**
  - Check permissions and mic availability with `sounddevice`.

---

## 👨‍🏫 Special Thanks

Project developed under the mentorship and guidance of **Abhiram**.

---

## 📝 License

This project is licensed under the **MIT License**.  
Feel free to fork, contribute, or use this for your own developments in assistive technology or robotics.

---

## 🤝 Contributions

Pull requests, feedback, and ideas are always welcome!  
If you build upon this project or adapt it for a different purpose, feel free to share your version and tag me.


🎯 *Built with PyCharm, powered by OpenCV, Vosk & Arduino.*




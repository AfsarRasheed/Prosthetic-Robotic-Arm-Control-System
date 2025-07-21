# === Library Imports ===
import cv2  # Computer vision — for webcam and image display
from cvzone.HandTrackingModule import HandDetector  # Hand tracking from CVZone
import serial  # Serial communication with Arduino
import serial.tools.list_ports  # Utility to get all COM ports
import time  # Time delays and timestamp control
import queue  # Queue for sharing voice data across threads
import sounddevice as sd  # Real-time microphone input
from vosk import Model, KaldiRecognizer  # Offline speech recognition
import json  # Handling speech recognition results
import os  # File and directory path handling
import tkinter as tk  # GUI framework
from tkinter import ttk  # Advanced tkinter widgets
import threading  # To run multiple detection modes in parallel

# === Serial Connection Functions ===

# Function to search for Arduino COM port
def find_arduino_port(known_port=None):
    ports = list(serial.tools.list_ports.comports())  # List all serial ports
    for p in ports:
        if known_port and known_port.lower() in p.device.lower():
            return p.device  # Return matched known port
        if "arduino" in p.description.lower():
            return p.device  # Auto-detect Arduino based on description
    return None  # Not found

# Try connecting to serial (with retries)
def connect_serial(port, baudrate, timeout=1, retries=9999, wait=2):
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt+1} to connect to Arduino on {port}...")
            ser = serial.Serial(port, baudrate, timeout=timeout)
            print(f"Connected to Arduino on {port}")
            return ser
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in {wait} seconds...")
            time.sleep(wait)
            port = find_arduino_port(port) or port  # Try refreshing the port
    raise Exception("Could not connect to Arduino after multiple attempts.")

# Serial send function (finger pattern)
def send_data(ser, data):
    try:
        msg = "$" + "".join(str(int(x)) for x in data)  # Format: $10101
        ser.write(msg.encode())
    except Exception as e:
        raise e

# === Vosk Voice Recognition Setup ===

# Path to the downloaded Vosk model
model_path = "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    raise Exception("Vosk model not found. Please download and extract to: " + model_path)

model = Model(model_path)  # Load the model
recognizer = KaldiRecognizer(model, 16000)  # Init recognizer with 16000Hz audio
q = queue.Queue()  # Queue for microphone audio

# Callback for microphone input
def callback(indata, frames, time_info, status):
    if status:
        print("Mic status:", status)
    q.put(bytes(indata))  # Push audio bytes to queue

# Recognize number spoken using Vosk
def recognize_number_vosk():
    number_words = {
        1: ['1', 'one', 'won', 'wan', 'on', 'first'],
        2: ['2', 'two', 'to', 'too', 'tu', 'second', 'tow', 'do'],
        3: ['3', 'three', 'tree', 'free', 'third', 'thre'],
        4: ['4', 'four', 'for', 'fore', 'forth', 'fourth'],
        5: ['5', 'five', 'fife', 'fiv', 'fifth'],
    }
    while True:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            print("🎤 [Vosk] Listening offline for number...")
            rec = KaldiRecognizer(model, 16000)
            while True:
                if not q.empty():
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "")
                        if text:
                            print(f"✅ [Vosk] Heard: '{text}'")
                            for word in text.split():
                                for num, words in number_words.items():
                                    if word.lower() in words:
                                        return num  # Return matched voice number

# === GUI Class ===
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prosthetic Arm Control")
        self.geometry("400x200")
        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Capture window close event

        # Create notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Hand Detection')
        self.notebook.add(self.tab2, text='Voice Recognition')
        self.notebook.add(self.tab3, text='Rock Paper Scissors')

        # Thread management
        self.running = True
        self.hand_thread = None
        self.voice_thread = None
        self.rps_thread = None
        self.active_tab = 0

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)  # Tab switch callback
        self.start_hand_detection()  # Default start with hand detection

    def on_tab_change(self, event):
        tab = self.notebook.index(self.notebook.select())
        # Start / stop logic based on active tab
        if tab == 0 and self.active_tab != 0:
            self.stop_voice_recognition()
            self.stop_rps_recognition()
            self.start_hand_detection()
            self.active_tab = 0
        elif tab == 1 and self.active_tab != 1:
            self.stop_hand_detection()
            self.stop_rps_recognition()
            self.start_voice_recognition()
            self.active_tab = 1
        elif tab == 2 and self.active_tab != 2:
            self.stop_hand_detection()
            self.stop_voice_recognition()
            self.start_rps_recognition()
            self.active_tab = 2

    # Thread wrappers
    def start_hand_detection(self):
        if self.hand_thread is None or not self.hand_thread.is_alive():
            self.hand_thread = threading.Thread(target=hand_detection_loop, daemon=True)
            self.hand_thread.start()

    def stop_hand_detection(self):
        global hand_detection_active
        hand_detection_active = False

    def start_voice_recognition(self):
        if self.voice_thread is None or not self.voice_thread.is_alive():
            self.voice_thread = threading.Thread(target=voice_recognition_loop, daemon=True)
            self.voice_thread.start()

    def stop_voice_recognition(self):
        global voice_recognition_active
        voice_recognition_active = False

    def start_rps_recognition(self):
        if self.rps_thread is None or not self.rps_thread.is_alive():
            self.rps_thread = threading.Thread(target=rps_recognition_loop, daemon=True)
            self.rps_thread.start()

    def stop_rps_recognition(self):
        global rps_recognition_active
        rps_recognition_active = False

    def on_close(self):
        self.running = False
        self.stop_hand_detection()
        self.stop_voice_recognition()
        self.stop_rps_recognition()
        self.destroy()

# === Initialize Hand Tracker ===
cap = cv2.VideoCapture(0)  # Open webcam
detector = HandDetector(maxHands=1, detectionCon=0.8, minTrackCon=0.5)  # Detect 1 hand max

PORT = "com5"  # Your Arduino COM port
BAUD = 9600  # Must match Arduino sketch

# Try connecting to Arduino
ser = None
while ser is None:
    port = find_arduino_port(PORT)
    if port:
        try:
            ser = connect_serial(port, BAUD)
        except Exception as e:
            print(e)
            time.sleep(2)
    else:
        print("Arduino not found. Retrying...")
        time.sleep(2)

# Track previous finger state
prev_fingers = [0, 0, 0, 0, 0]

# === Hand Detection Thread Function ===
hand_detection_active = False
def hand_detection_loop():
    global hand_detection_active
    hand_detection_active = True
    while hand_detection_active:
        success, img = cap.read()
        if not success:
            print("Camera read failed.")
            break
        hands, img = detector.findHands(img)
        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            if len(fingers) == 5:
                invertedFingers = [1 - f for f in fingers]
                if invertedFingers != prev_fingers:
                    print(f"🖐 Hand detected. Finger states: {invertedFingers}")
                    try:
                        send_data(ser, invertedFingers)
                    except Exception as e:
                        print(f"Serial error: {e}. Reconnecting...")
                        try:
                            if ser is not None:
                                ser.close()
                        except:
                            pass
                        reconnect_serial()
                    prev_fingers[:] = invertedFingers
        cv2.imshow("Hand Tracking", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

# === Voice Recognition Thread ===
voice_recognition_active = False
def voice_recognition_loop():
    global voice_recognition_active
    voice_recognition_active = True
    while voice_recognition_active:
        number = recognize_number_vosk()
        if number:
            voice_fingers = {
                1: [1, 0, 1, 1, 1],
                2: [1, 0, 0, 1, 1],
                3: [1, 1, 0, 0, 0],
                4: [1, 0, 0, 0, 0],
                5: [0, 0, 0, 0, 0],
            }.get(number, None)
            if voice_fingers:
                print(f"🎯 Activating finger pattern {voice_fingers} for number {number} via voice")
                try:
                    send_data(ser, voice_fingers)
                    prev_fingers[:] = voice_fingers
                except Exception as e:
                    print(f"Serial error: {e}. Reconnecting...")
                    try:
                        if ser:
                            ser.close()
                    except:
                        pass
                    reconnect_serial()

# === Rock-Paper-Scissors Recognition ===
def recognize_rps_vosk():
    rps_words = {
        'rock': ['rock', 'rok', 'roc', 'lock', 'ruck'],
        'paper': ['paper', 'papor', 'papa', 'peper'],
        'scissors': ['scissors', 'scissor', 'scizzors', 'season'],
    }
    while True:
        with sd.RawInputStream(samplerate=16000, blocksize=8000,
                               dtype='int16', channels=1, callback=callback):
            print("🎤 [Vosk] Listening offline for rock, paper, or scissors...")
            rec = KaldiRecognizer(model, 16000)
            while True:
                if not q.empty():
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "")
                        if text:
                            print(f"✅ [Vosk] Heard: '{text}'")
                            for word in text.split():
                                for move, keywords in rps_words.items():
                                    if word.lower() in keywords:
                                        return move

rps_recognition_active = False
def rps_recognition_loop():
    global rps_recognition_active
    rps_recognition_active = True
    while rps_recognition_active:
        move = recognize_rps_vosk()
        rps_fingers = {
            'rock': [1, 1, 1, 1, 1],
            'paper': [0, 0, 0, 0, 0],
            'scissors': [1, 0, 0, 1, 1]
        }.get(move, None)
        if rps_fingers:
            print(f"🎯 Activating pattern for '{move}': {rps_fingers}")
            try:
                send_data(ser, rps_fingers)
                prev_fingers[:] = rps_fingers
            except Exception as e:
                print(f"Serial error: {e}. Reconnecting...")
                try:
                    if ser: ser.close()
                except:
                    pass
                reconnect_serial()

# === Reconnect Serial ===
def reconnect_serial():
    global ser
    ser = None
    while ser is None:
        port = find_arduino_port(PORT)
        if port:
            try:
                ser = connect_serial(port, BAUD)
            except Exception as e:
                print(e)
                time.sleep(2)
        else:
            print("Arduino not found. Retrying...")
            time.sleep(2)

# === App Entry Point ===
if __name__ == "__main__":
    app = App()
    app.mainloop()  # Launch the GUI

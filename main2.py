import cv2
from cvzone.HandTrackingModule import HandDetector
import serial
import serial.tools.list_ports
import time
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json
import os
import tkinter as tk
from tkinter import ttk
import threading

# === Serial connection helpers ===
def find_arduino_port(known_port=None):
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if known_port and known_port.lower() in p.device.lower():
            return p.device
        if "arduino" in p.description.lower():
            return p.device
    return None

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
            port = find_arduino_port(port) or port
    raise Exception("Could not connect to Arduino after multiple attempts.")

def send_data(ser, data):
    try:
        msg = "$" + "".join(str(int(x)) for x in data)
        ser.write(msg.encode())
    except Exception as e:
        raise e

# === Offline voice recognition setup (Vosk) ===
model_path = "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    raise Exception("Vosk model not found. Please download and extract to: " + model_path)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)
q = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        print("Mic status:", status)
    q.put(bytes(indata))

def recognize_number_vosk():
    number_words = {
        1: ['1', 'one', 'won', 'wan', 'on', 'first'],
        2: ['2', 'two', 'to', 'too', 'tu', 'second', 'tow','do'],
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
                                        return num

# === GUI Application ===
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prosthetic Arm Control")
        self.geometry("400x200")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Hand Detection')
        self.notebook.add(self.tab2, text='Voice Recognition')
        self.notebook.add(self.tab3, text='Rock Paper Scissors')
        self.running = True
        self.hand_thread = None
        self.voice_thread = None
        self.rps_thread = None
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.active_tab = 0
        self.start_hand_detection()

    def on_tab_change(self, event):
        tab = self.notebook.index(self.notebook.select())
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

# === Hand tracking setup ===
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1, detectionCon=0.8, minTrackCon=0.5)
PORT = "com5"  # Change this if needed
BAUD = 9600
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
prev_fingers = [0, 0, 0, 0, 0]

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

voice_recognition_active = False
def voice_recognition_loop():
    global voice_recognition_active
    voice_recognition_active = True
    while voice_recognition_active:
        number = recognize_number_vosk()
        if number:
            # Finger pattern: [thumb, index, middle, ring, pinky]
            if number == 1:
                voice_fingers = [1, 0, 1, 1, 1]
            elif number == 2:
                voice_fingers = [1, 0, 0, 1, 1]
            elif number == 3:
                voice_fingers = [1, 1, 0, 0, 0]
            elif number == 4:
                voice_fingers = [1, 0, 0, 0, 0]
            elif number == 5:
                voice_fingers = [0, 0, 0, 0, 0]
            else:
                continue
            print(f"🎯 Activating finger pattern {voice_fingers} for number {number} via voice")
            try:
                send_data(ser, voice_fingers)
                prev_fingers[:] = voice_fingers
            except Exception as e:
                print(f"Serial error: {e}. Reconnecting...")
                try:
                    if ser is not None:
                        ser.close()
                except:
                    pass
                reconnect_serial()

def recognize_rps_vosk():
    rps_words = {
        'rock': ['rock', 'rok', 'roc', 'lock', 'ruck', 'rack','brock'],
        'paper': ['paper', 'papor', 'payper', 'piper', 'papa', 'peper','people'],
        'scissors': ['scissors', 'scisor', 'scizzors', 'scissor', 'scissers', 'scizzers', 'sizzors', 'scisors', 'sciszer', 'sciser','caesar','season','see them'],
    }
    while True:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
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
                                for move, words in rps_words.items():
                                    if word.lower() in words:
                                        return move

rps_recognition_active = False
def rps_recognition_loop():
    global rps_recognition_active
    rps_recognition_active = True
    while rps_recognition_active:
        move = recognize_rps_vosk()
        if move:
            if move == 'rock':
                rps_fingers = [1, 1, 1, 1, 1]
            elif move == 'paper':
                rps_fingers = [0, 0, 0, 0, 0]
            elif move == 'scissors':
                rps_fingers = [1, 0, 0, 1, 1]
            else:
                continue
            print(f"🎯 Activating RPS pattern {rps_fingers} for move '{move}' via voice")
            try:
                send_data(ser, rps_fingers)
                prev_fingers[:] = rps_fingers
            except Exception as e:
                print(f"Serial error: {e}. Reconnecting...")
                try:
                    if ser is not None:
                        ser.close()
                except:
                    pass
                reconnect_serial()

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

if __name__ == "__main__":
    app = App()
    app.mainloop()
    
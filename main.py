import cv2
from cvzone.HandTrackingModule import HandDetector
import serial
import serial.tools.list_ports
import time

# --- Serial connection helpers ---
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

# --- Hand tracking setup ---
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1, detectionCon=0.8, minTrackCon=0.5)

PORT = "com6"  # Change as needed
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

while True:
    success, img = cap.read()
    if not success:
        print("Failed to read from camera")
        break

    hands, img = detector.findHands(img)
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]  # List of 21 landmark points
        bbox = hand["bbox"]      # Bounding box info x, y, w, h
        fingers = detector.fingersUp(hand)
        if len(fingers) == 5:
            invertedFingers = [1 - f for f in fingers]
            if invertedFingers != prev_fingers:
                print(f"Finger states: {invertedFingers}")
                try:
                    send_data(ser, invertedFingers)
                except Exception as e:
                    print(f"Serial error: {e}. Attempting to reconnect...")
                    try:
                        ser.close()
                    except:
                        pass
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
                prev_fingers = invertedFingers.copy()

    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
# Import necessary libraries
import cv2  # OpenCV for video capture and display
from cvzone.HandTrackingModule import HandDetector  # Hand detector from cvzone for finger recognition
import serial  # For serial communication with Arduino
import serial.tools.list_ports  # For listing available COM ports
import time  # Used for delays and retry mechanisms

# --- Serial connection helper functions --- #

# Function to find the Arduino COM port
def find_arduino_port(known_port=None):
    ports = list(serial.tools.list_ports.comports())  # Get all available serial ports
    for p in ports:
        if known_port and known_port.lower() in p.device.lower():
            return p.device  # If known COM port is found
        if "arduino" in p.description.lower():
            return p.device  # If description contains "arduino"
    return None  # If no suitable port is found

# Function to connect to Arduino over serial with multiple retries
def connect_serial(port, baudrate, timeout=1, retries=9999, wait=2):
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt+1} to connect to Arduino on {port}...")
            ser = serial.Serial(port, baudrate, timeout=timeout)  # Attempt serial connection
            print(f"Connected to Arduino on {port}")
            return ser  # Return the serial object on success
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in {wait} seconds...")
            time.sleep(wait)  # Wait and retry
            port = find_arduino_port(port) or port  # Try to find port again
    raise Exception("Could not connect to Arduino after multiple attempts.")

# Function to encode finger data and send to Arduino via serial
def send_data(ser, data):
    try:
        msg = "$" + "".join(str(int(x)) for x in data)  # Format: $10101 (thumb to pinky)
        ser.write(msg.encode())  # Send the message to Arduino
    except Exception as e:
        raise e  # Re-raise error if there's a failure

# --- Hand tracking setup --- #

cap = cv2.VideoCapture(0)  # Initialize webcam (camera index 0)
detector = HandDetector(maxHands=1, detectionCon=0.8, minTrackCon=0.5)  # Configure hand detector

PORT = "com6"  # COM port used for Arduino connection (Change this if needed)
BAUD = 9600  # Baud rate for Arduino communication

ser = None  # Holds the serial object

# Try connecting to Arduino in a loop until successful
while ser is None:
    port = find_arduino_port(PORT)  # Find available Arduino port
    if port:
        try:
            ser = connect_serial(port, BAUD)  # Attempt connection
        except Exception as e:
            print(e)
            time.sleep(2)
    else:
        print("Arduino not found. Retrying...")
        time.sleep(2)

# Initialize a list to store previous finger states for change detection
prev_fingers = [0, 0, 0, 0, 0]  # Represents [thumb, index, middle, ring, pinky]

# --- Main internal loop for hand tracking and serial dispatch --- #
while True:
    success, img = cap.read()  # Capture video frame from webcam
    if not success:
        print("Failed to read from camera")
        break  # If camera read fails, stop the loop

    hands, img = detector.findHands(img)  # Detect hands from frame

    if hands:  # If at least one hand is detected
        hand = hands[0]  # Focus on the first detected hand
        lmList = hand["lmList"]  # List of 21 hand landmark positions
        bbox = hand["bbox"]  # Bounding box info of hand: [x, y, width, height]
        fingers = detector.fingersUp(hand)  # Detect which fingers are currently up
        if len(fingers) == 5:  # Ensure valid 5-finger detection
            invertedFingers = [1 - f for f in fingers]  # Invert the result: 1=closed, 0=open (for servos)
            if invertedFingers != prev_fingers:  # Only send if finger state has changed
                print(f"Finger states: {invertedFingers}")  # Show current finger states
                try:
                    send_data(ser, invertedFingers)  # Send data to Arduino
                except Exception as e:
                    print(f"Serial error: {e}. Attempting to reconnect...")
                    try:
                        ser.close()  # Close the previous connection if exists
                    except:
                        pass
                    ser = None  # Reset the serial connection
                    while ser is None:  # Retry until successfully reconnected
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
                prev_fingers = invertedFingers.copy()  # Update previous finger state

    cv2.imshow("Hand Tracking", img)  # Display the video feed in a window
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit the program
        break

# --- Cleanup --- #
cap.release()  # Release the webcam
cv2.destroyAllWindows()  # Close all OpenCV windows

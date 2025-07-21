#define numOfValsRec 5
#define digitsPerValRec 1

#include <Servo.h>

// Servo declarations
Servo servoThumb;
Servo servoIndex;
Servo servoMiddle;
Servo servoRing;
Servo servoPinky;

// Variables for receiving data
int valsRec[numOfValsRec] = {0, 0, 0, 0, 0}; // Start with all fingers closed
String recievedString = "";
bool receiving = false;

void setup() {
  Serial.begin(9600);

  // Attach servos to respective pins
  servoThumb.attach(9);
  servoIndex.attach(10);
  servoMiddle.attach(13);
  servoRing.attach(3);
  servoPinky.attach(11);

  updateServos(); // Set initial positions
}

void recieveData() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '$') {
      recievedString = "";  // Start new message
      receiving = true;
    } else if (receiving) {
      recievedString += c;

      if (recievedString.length() >= numOfValsRec * digitsPerValRec) {
        receiving = false;

        for (int i = 0; i < numOfValsRec; i++) {
          int pos = i * digitsPerValRec;
          valsRec[i] = recievedString.substring(pos, pos + digitsPerValRec).toInt();
        }
        updateServos(); // Only update when valid data is received
      }
    }
  }
}

void updateServos() {
  if (valsRec[0] == 1) servoThumb.write(0); else servoThumb.write(180);
  if (valsRec[1] == 1) servoIndex.write(0); else servoIndex.write(180);
  if (valsRec[2] == 1) servoMiddle.write(0); else servoMiddle.write(180);
  if (valsRec[3] == 1) servoRing.write(0); else servoRing.write(180);
  if (valsRec[4] == 1) servoPinky.write(0); else servoPinky.write(180);
}

void loop() {
  recieveData();                                                                 
  // Do not update servos here; only update when valid data is received
}
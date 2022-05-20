#include "rescueServo.h"

Servo myservo;
const int R_angle = 165;
const int L_angle = 5;
const int C_angle = 82;

void setupServo() {
  //  myservo.attach(A7, 550, 2600); // attaches the servo on pin A7 to the servo object
}

void turnTo(int dir) {
  myservo.attach(A7, 550, 2600);
  myservo.write(dir);
}

void wiggle(int angle, int wiggleAmt) {
  Serial.println("In wiggle");
  for (int i = 1; i < wiggleAmt; i++) {
    myservo.write(angle - i);
    delay(100);
    myservo.write(angle + i);
    delay(100);
  }
  Serial.println("Done wiggle");
}

void dropKits(char dir, int amt) {
  Serial.println("In dropKits");
  myservo.attach(A7, 550, 2600); // attaches the servo on pin A7 to the servo object
  if (dir == 'L') {
    for (int i = 0; i < amt; i++) {
      wiggle(C_angle, 7);
      myservo.write(C_angle);
      delay(100);
      myservo.write(L_angle);
      wiggle(L_angle, 7);
      delay(500);
    }
  } else if (dir == 'R') {
    for (int i = 0; i < amt; i++) {
      wiggle(C_angle, 7);
      myservo.write(C_angle);
      delay(100);
      myservo.write(R_angle);
      wiggle(R_angle, 7);
      delay(500);
    }
  }
  myservo.write(C_angle);
  wiggle(C_angle, 5);
  myservo.detach();
  Serial.println("Done dropKits");
}

void RGB_color(int red_light_value, int green_light_value, int blue_light_value, int rescueKits, char dir) {
  analogWrite(47, red_light_value);
  analogWrite(43, green_light_value);
  analogWrite(42, blue_light_value);
  if (rescueKits == 0) {
    delay(500);
  } else {
    dropKits(dir, rescueKits);
  }
  analogWrite(47, 0);
  analogWrite(43, 0);
  analogWrite(42, 0);
  for (int i = 0; i < 4; i++) {
    analogWrite(47, red_light_value);
    analogWrite(43, green_light_value);
    analogWrite(42, blue_light_value);
    delay(500);
    analogWrite(47, 0);
    analogWrite(43, 0);
    analogWrite(42, 0);
    delay(500);
  }

}

void victim() {
  if (!isHeat) {
    doHeatVictim(getHeatSensorReadings('L'), getHeatSensorReadings('R'));
  }

  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    Serial.print("Victim Message Received: ");
    Serial.println(incoming_byte);
    ports[RIGHT].setMotorSpeed(0);
    ports[LEFT].setMotorSpeed(0);

    if ((incoming_byte - tolower(incoming_byte) && getSensorReadings(0) < 35) || (incoming_byte - toupper(incoming_byte) && getSensorReadings(1) < 35)) { //if letter is uppercase

      switch (incoming_byte) {
        case 'Y': // 1 kit
          Serial.println("red/yellow");
          RGB_color(255, 0, 0, 1, 'R'); // Red
          //dropKits('R', 1);
          break;

        case 'G': // 0 kits
          Serial.println("green");
          RGB_color(0, 255, 0, 0, 'R'); // Green
          break;

        case 'H': // 3 kits
          Serial.println("H");
          RGB_color(0, 0, 255, 3, 'R'); // Blue
          //dropKits('R', 3);
          break;

        //turn left
        case 'S': // 2 kits
          Serial.println("S");
          RGB_color(0, 255, 255, 2, 'R'); // Cyan
          //dropKits('R', 2);
          break;

        //turn right
        case 'U': // 0 kits
          Serial.println("U");
          RGB_color(255, 0, 255, 0, 'R'); // Magenta
          break;
        case 'y': // 1 kit
          Serial.println("red/yellow");
          RGB_color(255, 0, 0, 1, 'L'); // Red
          //dropKits('L', 1);
          break;

        case 'g': // 0 kits
          Serial.println("green");
          RGB_color(0, 255, 0, 0, 'L'); // Green
          break;

        case 'h': // 3 kits
          Serial.println("H");
          RGB_color(0, 0, 255, 3, 'L'); // Blue
          //dropKits('L', 3);
          break;

        //turn left
        case 's': // 2 kits
          Serial.println("S");
          RGB_color(0, 255, 255, 2, 'L'); // Cyan
          //dropKits('L', 2);
          break;

        //turn right
        case 'u': // 0 kits
          Serial.println("U");
          RGB_color(255, 0, 255, 0, 'R'); // Magenta
          break;
        default:
          Serial.print("#2 hmmm wut is this: ");
          Serial.println(incoming_byte);
      }
    }
  }
}

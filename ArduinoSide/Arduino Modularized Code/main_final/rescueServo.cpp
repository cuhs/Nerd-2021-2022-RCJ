#include "rescueServo.h"

Servo myservo;
const int R_angle = 10;
const int L_angle = 168;
const int C_angle = 82;

void setupServo() {
  myservo.attach(A7, 550, 2600); // attaches the servo on pin A7 to the servo object
}

void wiggle(char angle) {
  for (int i = 5; i < 10; i++) {
    myservo.write(angle - i);
    delay(100);
    myservo.write(angle + i);
    delay(100);
  }
}

void dropKits(char dir, int amt) {
  if (dir == 'L') {
    for (int i = 0; i < amt; i++) {
      wiggle(C_angle);
      myservo.write(C_angle);
      delay(2000);
      myservo.write(L_angle);
      delay(2000);
    }
  } else if (dir == 'R') {
    for (int i = 0; i < amt; i++) {
      wiggle(C_angle);
      myservo.write(C_angle);
      delay(2000);
      myservo.write(R_angle);
      delay(2000);
    }
  }
}

void RGB_color(int red_light_value, int green_light_value, int blue_light_value) {
  analogWrite(47, red_light_value);
  analogWrite(43, green_light_value);
  analogWrite(42, blue_light_value);
}

void victim() {
  doHeatVictim(getHeatSensorReadings(4), getHeatSensorReadings(5));

  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);

    ports[RIGHT].setMotorSpeed(0);
    ports[LEFT].setMotorSpeed(0);

    switch (incoming_byte) {
      case 'R': // 1 kit
        Serial.println("red/yellow");
        RGB_color(255, 0, 0); // Red
        dropKits('L', 1);
        delay(1000);
        RGB_color(0, 0, 0); // Red
        break;

      case 'G': // 0 kits
        Serial.println("green");
        RGB_color(0, 255, 0); // Green
        delay(1000);
        RGB_color(0, 0, 0);
        break;

      case 'H': // 3 kits
        Serial.println("H");
        RGB_color(0, 0, 255); // Blue
        dropKits('L', 3);
        delay(1000);
        RGB_color(0, 0, 0); //
        break;

      //turn left
      case 'S': // 2 kits
        Serial.println("S");
        RGB_color(0, 255, 255); // Cyan
        dropKits('L', 2);
        delay(1000);
        RGB_color(0, 0, 0); //
        break;

      //turn right
      case 'U': // 0 kits
        Serial.println("U");
        RGB_color(255, 0, 255); // Magenta
        delay(1000);
        RGB_color(0, 0, 0); //
        break;

      default:
        Serial.print("hmmm wut is this: ");
        Serial.println(incoming_byte);
    }
  }
}

#include "rescueServo.h"
Servo myservo;
bool shouldRun = true;
//midPos: 60
bool stuckTest(int target) {
  int ang = myservo.read();
  //Serial.println(ang);
  if (!(ang > target - 1 && ang < target + 1)) {
    return true;
  }
  return false;

}

void setupServo() {
  myservo.attach(A8, 300, 2400); // attaches the servo on pin A8 to the servo object
  //myservo.attach(A6);
}
void wiggle(int target, int times) {

  for (int i = 1; i < times; i++) {
    myservo.write(target + i);
    delay(200);
    myservo.write(target - i);
    delay(200);
  }
  myservo.write(target);
  //}
  if (stuckTest(target)) {
    shouldRun = false;
  }
}

void servoTurnLeft() {
  myservo.write(0);

  delay(500);
  wiggle(0, 5);
}

void servoMidPos() {
  myservo.write(60);
  delay(500);
  wiggle(60, 5);
}


void servoTurnRight() {

  myservo.write(173);
  delay(500);
  //Serial.print(myservo.read());
  wiggle(173, 5);
}

void RGB_color(int red_light_value, int green_light_value, int blue_light_value)
 {
  analogWrite(47, red_light_value);
  analogWrite(43, green_light_value);
  analogWrite(42, blue_light_value);
}
void victim() {

  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);

    ports[RIGHT].setMotorSpeed(0);
    ports[LEFT].setMotorSpeed(0);

    switch (incoming_byte) {
      case 'R':
        Serial.println("red/yellow");
         RGB_color(255, 0, 0); // Red
         delay(1000);
         RGB_color(0, 0, 0); // Red
        break;
      case 'G':
        Serial.println("green");
        RGB_color(255, 0, 0); // Green
         delay(1000);
         RGB_color(0, 255, 0); 
        break;
      case 'H':
        Serial.println("H");
        RGB_color(255, 0, 255); // Blue
         delay(1000);
         RGB_color(0, 0, 0); // 
        break;
      //turn left
      case 'S':
        Serial.println("S");
        RGB_color(0, 255, 255); // Cyan
         delay(1000);
         RGB_color(0, 0, 0); // 
        break;
      //turn right
      case 'U':
        Serial.println("U");
        RGB_color(255, 0, 255); // Magenta
         delay(1000);
         RGB_color(0, 0, 0); // 
        break;
      default:
        Serial.println("hmmm wut is this");
    }
  }
}

#include "rescueServo.h"
Servo myservo;
bool shouldRun = true;
int ct = 0;
 bool stuckTest(int target) {
  int ang = myservo.read();
  //Serial.println(ang);
  if (!(ang > target - 1 && ang < target + 1)) {
    return true;
  }
  return false;

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

void turnLeft() {
  myservo.write(0);

  delay(500);
  wiggle(0, 5);
  ct++;
}

void midPos() {
  myservo.write(60);
  delay(500);
  wiggle(60, ct * 1.5 + 1);
}


void turnRight() {

  myservo.write(173);
  delay(500);
  //Serial.print(myservo.read());
  wiggle(173, 5);
  ct++;
}

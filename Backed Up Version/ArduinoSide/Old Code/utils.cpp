#ifndef _utils_ino_
#define _utils_ino_

#include "global_vars.h"

// This function updates motor encoder count every time goes high. Ex: going from low to high increases encoder count
//template <int PN> // PN represents an index in the object array "MegaPiPort Motor" of the motor being run IN MOTOR.H
/*void motorinterrupt() {
  if (ports[PN].backwards)
    (digitalRead(ports[PN].encPin)) ? ports[PN].count++ : ports[PN].count--;
  else
    (digitalRead(ports[PN].encPin)) ? ports[PN].count-- : ports[PN].count++;
}

void doTurn(char dir, int deg) {
  ports[RIGHT].count = 0;
  if (dir == 'L') {
    Serial.print("Left turn ");
    Serial.print(deg);
    Serial.println(" degrees.");
    while (abs(ports[0].count) < (WB / D) * deg) { //300 for 90 deg turn 600 for 180 deg turn
      ports[RIGHT].setMotorSpeed(120);
      ports[LEFT].setMotorSpeed(-120);
    }
  } else {
    Serial.print("Right turn ");
    Serial.print(deg);
    Serial.println(" degrees.");
    while (abs(ports[0].count) < (WB / D) * deg) { //300 for 90 deg turn 600 for 180 deg turn
      ports[RIGHT].setMotorSpeed(-120);
      ports[LEFT].setMotorSpeed(120);
    }
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void goForward(int dist) {
  ports[RIGHT].count = 0;
  Serial.print("Forward ");
  Serial.print(dist);
  Serial.println(" centimeters.");
  while (abs(ports[0].count) < (360 / (D * PI))*dist) {
    ports[RIGHT].setMotorSpeed(120);
    ports[LEFT].setMotorSpeed(120);
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void goForwardTiles(int tiles) {
  int tileSize = 30; // Set to 30
  ports[RIGHT].count = 0;
  Serial.print("Forward ");
  Serial.print(tiles);
  Serial.print(" tiles. (");
  Serial.print(tiles * 30);
  Serial.println(" centimeters)");

  int enc = ((360 / (D * PI)) * tileSize * tiles);

  while (((abs(ports[0].count) < (360 / (D * PI)) * tileSize * tiles)) && (getSensorReadings(2) > 5)) {
    Serial.print(enc);
    Serial.print(' ');
    Serial.println(abs(ports[0].count));
    //    if (Serial.available() >= 1) {
    //      if (Serial.read() == 'v') {
    //        char side = Serial.read();
    //        int kits = (Serial.read() - '0');
    //        Serial.print("Side: ");
    //        Serial.println(side);
    //        Serial.print("Kits: ");
    //        Serial.println(kits);
    //        //victim stuff
    //      }
    //    } else {
    ports[RIGHT].setMotorSpeed(120);
    ports[LEFT].setMotorSpeed(120);
    //    }
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
  delay(1000);
  //Serial.println('f');
  //Serial2.write('f');
}

// VVVVV incorporates PID wall following, still in progress
void goForwardTiles2(int tiles) {
  int target = 11;
  int Ftarget = 5;
  int kp = 14;
  int Lspeed, Rspeed;
  int motorSpeed = 100;
  int error;
  int tileSize = 30; // Set to 30
  ports[RIGHT].count = 0;
  Serial.print("Forward ");
  Serial.print(tiles);
  Serial.print(" tiles. (");
  Serial.print(tiles * 30);
  Serial.println(" centimeters)");
  while (((abs(ports[0].count) < (360 / (D * PI)) * tileSize * tiles)) && (getSensorReadings(2) > 5)) {
    if (getSensorReadings(3) < 2 * target && (abs(getSensorReadings(3) - getSensorReadings(1)) < target * 2)) {
      error = target - getSensorReadings(3);
      Lspeed = motorSpeed + error * kp;
      Rspeed = motorSpeed - error * kp;

      ports[RIGHT].setMotorSpeed(Rspeed);
      ports[LEFT].setMotorSpeed(Lspeed);
      Serial.print(Lspeed);
      Serial.print(" + ");
      Serial.println(Rspeed);

    } else if (getSensorReadings(4) < 2 * target && (abs(getSensorReadings(4) - getSensorReadings(0)) < target * 2)) {
      error = target - getSensorReadings(4);
      Lspeed = motorSpeed - error * kp;
      Rspeed = motorSpeed + error * kp;

      ports[RIGHT].setMotorSpeed(Rspeed);
      ports[LEFT].setMotorSpeed(Lspeed);
      Serial.print(Lspeed);
      Serial.print(" + ");
      Serial.println(Rspeed);
    } else {
      ports[RIGHT].setMotorSpeed(100);
      ports[LEFT].setMotorSpeed(100);
    }
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void motorControl() {

  Serial.println("Running Motor Control.");
  // Read in the incoming messages
  for (int x = 0; x < 4; x++) {
    message[x] = 'a';
  }

  while (Serial2.available() > 0) {
    if (message[0] == '$') {
      Serial2.write('d');
      break;
    }
    for (int x = 0; x < 4; x++) {
      delay(1);
      message[x] = Serial2.read();
      Serial.print(x);
      Serial.print(": ");
      Serial.println(message[x]);
      if (message[0] == '$')
        break;
    }
    Serial.println("a");
    if (message[0] == 'L' || message[0] == 'R')
      doTurn(message[0], (message[1] - '0') * 10 + (message[2] - '0'));
    if (message[0] == 'F') {
      if (message[1] == 'T') {
        goForwardTiles(message[2] - '0');
      } else {
        goForward(message[1] - '0');
      }
    }
    Serial.println("b");
    alignRobot();
    Serial.println("c");
  }
} IN MOTOR.CPP */

/*void sendWallValues(int leftDist, int rightDist, int frontDist) {
  char walls[3] = {'0', '0', '0'};
  int minimumDist = 30; // Minimum distance to determine if there is a wall on the side

  if (leftDist < minimumDist)
    walls[0] = '1';
  if (rightDist < minimumDist)
    walls[1] = '1';
  if (frontDist < minimumDist)
    walls[2] = '1';

  // for debugging
  for (int i = 0; i < 3; i++) {
    if (i != 2)
      Serial.print(walls[i]);
    else
      Serial.println(walls[i]);
  }

  Serial2.write(walls, 3);
} IN VLX.CPP */

/*void tcaselect(uint8_t i) {
  if (i > 7) return;

  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}IN TCA.CPP*/

/*void setupSensors() {
  tcaselect(0);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (0)");
    while (1);
  }
  tcaselect(1);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (1)");
    while (1);
  }
  tcaselect(2);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (2)");
    while (1);
  }
  tcaselect(3);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (3)");
    while (1);
  }
  tcaselect(4);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (4)");
    while (1);
  }
  tcaselect(5);
  if (tcs.begin()) {
    Serial.println("Found sensor");
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }
} IN TCS and VLX.cpp*/

/*int getSensorReadings(int sensorNum) {
  tcaselect(sensorNum);
  lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!

  //if (measure.RangeStatus != 4) {  // phase failures have incorrect data
  //Serial.print('L'); Serial.print(sensorNum); Serial.print(": "); Serial.print((measure.RangeMilliMeter) / 10); Serial.println(" ");
  //} else {
  //Serial.print('L'); Serial.print(sensorNum); Serial.print(": "); Serial.print("OOR"); Serial.println(" ");
  //}
  return measure.RangeMilliMeter / 10;
} IN VLX.CPP */

/*void alignLeft() {
  while (abs(getSensorReadings(3) - getSensorReadings(1)) > 0) {
    //Serial.println(abs(getSensorReadings(3) - getSensorReadings(1)));
    if (getSensorReadings(3) > getSensorReadings(1)) {
      ports[RIGHT].setMotorSpeed(120);
      ports[LEFT].setMotorSpeed(-120);
    }
    else {
      ports[RIGHT].setMotorSpeed(-120);
      ports[LEFT].setMotorSpeed(120);
    }
  }

  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void alignRight() {
  while (abs(getSensorReadings(4) - getSensorReadings(0)) > 0) {
    //Serial.println(abs(getSensorReadings(3) - getSensorReadings(1)));
    if (getSensorReadings(0) > getSensorReadings(4)) {
      ports[RIGHT].setMotorSpeed(120);
      ports[LEFT].setMotorSpeed(-120);
    }
    else {
      ports[RIGHT].setMotorSpeed(-120);
      ports[LEFT].setMotorSpeed(120);
    }
  }

  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void alignFront() {
  if (getSensorReadings(2) < 5) {
    while (getSensorReadings(2) < 5) {
      ports[RIGHT].setMotorSpeed(-120);
      ports[LEFT].setMotorSpeed(-120);
    }
  } else {
    while (getSensorReadings(2) > 5) {
      ports[RIGHT].setMotorSpeed(120);
      ports[LEFT].setMotorSpeed(120);
    }
  }

  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void alignRobot() {
  if ((getSensorReadings(0) < 30) && (getSensorReadings(4) < 30))
    alignRight();
  else if ((getSensorReadings(1) < 30) && (getSensorReadings(3) < 30))
    alignLeft();
  if (getSensorReadings(2) < 30)
    alignFront();
}

// Puts the robot in the center of the tile
void alignToTile() {
  double distFromCenter;
  double robotWidth = 17;
  int tileSize = 30;
  double turnDegrees = 70;
  int moveDistance;
  int wallVal;
  if ((getSensorReadings(0) < 30) && (getSensorReadings(4) < 30)) {
    alignRight();
    delay(7000);
    distFromCenter = (tileSize / 2) - (getSensorReadings(4) + (robotWidth / 2));
    wallVal = getSensorReadings(4);
    Serial.println("ALIGNING WITH RIGHT WALL");
    Serial.print(abs(distFromCenter));
    Serial.println(" cm away from the center of the tile.");
    Serial.print(tileSize / 2);
    Serial.print(" - (");
    Serial.print(wallVal);
    Serial.print(" + ");
    Serial.print(robotWidth / 2);
    Serial.println(')');
    if (distFromCenter > 0)
      doTurn('L', turnDegrees);
    else
      doTurn('R', turnDegrees);
    moveDistance = abs(distFromCenter) / cos(turnDegrees);
    Serial.print("Moving ");
    Serial.print(moveDistance);
    Serial.println(" cm forward.");
  }
  else if ((getSensorReadings(1) < 30) && (getSensorReadings(3) < 30)) {
    alignLeft();
    delay(7000);
    distFromCenter = (tileSize / 2) - (getSensorReadings(3) + (robotWidth / 2));
    wallVal = getSensorReadings(3);
    Serial.println("ALIGNING WITH LEFT WALL");
    Serial.print(abs(distFromCenter));
    Serial.println(" cm away from the center of the tile.");
    Serial.print(tileSize / 2);
    Serial.print(" - (");
    Serial.print(wallVal);
    Serial.print(" + ");
    Serial.print(robotWidth / 2);
    Serial.println(')');
    if (distFromCenter > 0)
      doTurn('R', turnDegrees);
    else
      doTurn('L', turnDegrees);
    moveDistance = abs(distFromCenter) / cos(turnDegrees);
    Serial.print("Moving ");
    Serial.print(moveDistance);
    Serial.println(" cm forward.");
  }
  if (getSensorReadings(2) < 30)
    alignFront();
} IN MOTOR.CPP */

/*bool stuckTest(int target) {
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
} IN RESCUESERVO.CPP */

#endif

#include "IMU.h"

int resetPinIMU = A6;
const int ROBOT_WIDTH = 17.5;
Adafruit_BNO055 bno;

void initIMU() {
  if (!bno.begin(Adafruit_BNO055::OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected .pp.. Check your wiring or I2C ADDR!");
    while (1);
  }

  delay(100);

  bno.setExtCrystalUse(true);
}

void reset() {
  Serial.println("Resetting.");
  digitalWrite(resetPinIMU, HIGH);
  digitalWrite(resetPinIMU, LOW);

  delayMicroseconds(30);

  digitalWrite(resetPinIMU, HIGH);

  bno.begin();
}

void turnAbs(char t) {
  //get BNO values
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  int pos = euler.x();
  //turning right
  if (t == 'r') {
    if (pos > 350 || pos < 10)
      turnAbs(90);
    else if (pos > 80 && pos < 100)
      turnAbs(180);
    else if (pos > 170 && pos < 190)
      turnAbs(270);
    else if (pos > 260 && pos < 280)
      turnAbs(0);

    //turning left
  } else if (t == 'l') {
    if (pos > 350 || pos < 10)
      turnAbs(270);
    else if (pos > 80 && pos < 100)
      turnAbs(0);
    else if (pos > 170 && pos < 190)
      turnAbs(90);
    else if (pos > 260 && pos < 280)
      turnAbs(180);
  }
}

void turnAbs(int degree) {
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int dir[4] = {0, 90, 180, 270};
  int fix;
  int curDir = euler.x();
  int targetDir = degree;
  double integral = 0.0;
  int error = targetDir - curDir;
  double pastError = 0;

  while (abs(error) > 2) {
    victim();
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    curDir = euler.x();
    error = targetDir - curDir;

    if (error > 180)
      error -= 360;
    else if (error < -180)
      error += 360;

    fix = (int)(PID(error, pastError, integral, 1.6667, .005, 0));
    if (fix > 0)
      fix += 80;
    else
      fix -= 80;

    Serial.print(fix);
    Serial.print("\tEuler: ");
    Serial.print(euler.x());
    Serial.print("\terror: ");
    Serial.println(error);

    ports[RIGHT].setMotorSpeed(fix);
    ports[LEFT].setMotorSpeed(-fix);
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void triangulation(int left, int right) {
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int distFromCenter;
  int angle;
  int forwardCm;
  int currAngle;

  //no walls
  if (left > 30 && right > 30) {
    goForwardTilesPID(1);
    return;
  }

  //closer to right wall
  if (left > right) {
    distFromCenter = 15 - (right + ROBOT_WIDTH / 2);
    angle = atan(30 / distFromCenter) * 360 / (2 * 3.1415927);
    forwardCm = sqrt(pow(distFromCenter, 2) + 900);
    currAngle = euler.x();
    turnAbs((int)(currAngle - angle + 360) % 360);
    goForwardPID(forwardCm);
    turnAbs(currAngle);

    //closer to left wall
  } else {
    distFromCenter = 15 - (left + ROBOT_WIDTH / 2);
    angle = atan(30 / distFromCenter) * 360 / (2 * 3.1415927);
    forwardCm = sqrt(pow(distFromCenter, 2) + 900);
    currAngle = euler.x();
    turnAbs((int)(currAngle + angle) % 360);
    goForwardPID(forwardCm);
    turnAbs(currAngle);
  }
}

#include "IMU.h"

int resetPinIMU = A6;
const int ROBOT_WIDTH = 18;
Adafruit_BNO055 bno;
int finishedRamp = 0;

void initIMU() {
  tcaselect(7);
  if (!bno.begin(Adafruit_BNO055::OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial3.print("Ooops, no BNO055 detected .pp.. Check your wiring or I2C ADDR!");
    while (1);
  }

  delay(100);

  bno.setExtCrystalUse(true);
}

void reset() {
  Serial3.println("Resetting.");
  digitalWrite(resetPinIMU, HIGH);
  digitalWrite(resetPinIMU, LOW);

  delayMicroseconds(30);

  digitalWrite(resetPinIMU, HIGH);

  bno.begin();
}

int getDirection(int dir) {
  if (dir <= 20 || dir >= 340)
    return 0;
  if (dir <= 115 && dir >= 70)
    return 90;
  if (dir <= 200 && dir >= 160)
    return 180;
  if (dir <= 290 && dir >= 250)
    return 270;
  return -1;
}

void turnAbs(char t) {
  //get BNO values
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  int pos = euler.x();
  //turning right
  if (t == 'r') {
    if (pos > 315 || pos < 45)
      turnAbs(90);
    else if (pos > 45 && pos < 135)
      turnAbs(180);
    else if (pos > 135 && pos < 225)
      turnAbs(270);
    else if (pos > 225 && pos < 315)
      turnAbs(0);

    //turning left
  } else if (t == 'l') {
    if (pos > 315 || pos < 45)
      turnAbs(270);
    else if (pos > 45 && pos < 135)
      turnAbs(0);
    else if (pos > 135 && pos < 225)
      turnAbs(90);
    else if (pos > 225 && pos < 315)
      turnAbs(180);
  }
}

void displayIMU() {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  while (true) {
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    Serial3.println((int)euler.x());
  }
}
void turnRight(int degree) {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int curr = euler.x();
  int target = (curr + degree) % 360;
  int error = target - curr;
  while (error >= 2) {
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    error = target - euler.x();
    //      Serial3.print("error: ");
    //      Serial3.println(error);
    ports[RIGHT].setMotorSpeed(-150);
    ports[LEFT].setMotorSpeed(150);
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void turnAbs(int degree) {
  unsigned long startTime;
  unsigned long endTime;

  int prev_count = 0;
  bool stalling = false;
  bool checking = false;
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int dir[4] = {0, 90, 180, 270};
  int fix;
  int curDir = euler.x();
  int targetDir = degree;
  double integral = 0.0;
  int error = targetDir - curDir;
  double pastError = 0;
  int startingError = error;
  bool shouldSendM = true;
  while (abs(error) >= 3 && !stalling) {
    //Serial3.println("In turnAbs degrees");
    victim();
    tcaselect(7);
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    curDir = euler.x();
    error = targetDir - curDir;
    if (error > 180) {
      error -= 360;
    } else if (error < -180)
      error = 360 + error;
    if(shouldSendM && abs(error)<=(7*abs(startingError))/10){
      //Serial3.println("Sending m");
      shouldSendM = false;
      delay(1);
      Serial2.write('m');
      delay(1);
    }
    if (ports[LEFT].count == prev_count && !checking) {
      //Serial3.println("set start time");
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
      //Serial3.println("checking false");
      checking = false;
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      //Serial3.println("motors might be stalling");
      endTime = millis();
      if (endTime - startTime > 1000 && getDirection((int)euler.x()) != -1) {
        Serial3.println("STALLING");
        stalling = true;
      }
    }
    prev_count = ports[LEFT].count;
    char c = obstacleDetect();
    if(c != '0'){
      int motorEncUse = LEFT;
      ports[motorEncUse].count=0;      
      while(ports[motorEncUse].count>((-360 / (D * PI)) * 3)){
        ports[RIGHT].setMotorSpeed(-80);
        ports[LEFT].setMotorSpeed(-80);
      }
    }
    fix = (int)(PID(error, pastError, integral, 2, 0.005, 0));
    if (fix > 0)
      fix += 80;
    else
      fix -= 80;
    //    Serial3.print(fix);
    //    Serial3.print("\tEuler: ");
    //    Serial3.print(euler.x());
    //    Serial3.print("\terror: ");
    //    Serial3.println(error);
    ports[RIGHT].setMotorSpeed(-fix);
    ports[LEFT].setMotorSpeed(fix);
    //Serial3.println(euler.x());
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}
void turnAbsNoVictim(int degree) {
  unsigned long startTime;
  unsigned long endTime;

  int prev_count = 0;
  bool stalling = false;
  bool checking = false;
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int dir[4] = {0, 90, 180, 270};
  int fix;
  int curDir = euler.x();
  int targetDir = degree;
  double integral = 0.0;
  int error = targetDir - curDir;
  double pastError = 0;
  while (abs(error) >= 2 && !stalling) {
    tcaselect(7);
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    curDir = euler.x();
    error = targetDir - curDir;
    if (error > 180) {
      error -= 360;
    } else if (error < -180)
      error = 360 + error;

    if (ports[LEFT].count == prev_count && !checking) {
      //Serial3.println("set start time");
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
      //Serial3.println("checking false");
      checking = false;
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      //Serial3.println("motors might be stalling");
      endTime = millis();
      if (endTime - startTime > 1000 && getDirection((int)euler.x()) != -1) {
        Serial3.println("STALLING");
        stalling = true;
      }
    }
    prev_count = ports[LEFT].count;

    fix = (int)(PID(error, pastError, integral, 1.6667, 0, 0));
    if (fix > 0)
      fix += 60;
    else
      fix -= 60;
    //    Serial3.print(fix);
    //    Serial3.print("\tEuler: ");
    //    Serial3.print(euler.x());
    //    Serial3.print("\terror: ");
    //    Serial3.println(error);
    ports[RIGHT].setMotorSpeed(-fix);
    ports[LEFT].setMotorSpeed(fix);
    //Serial3.println(euler.x());
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

bool triangulation(int left, int right) {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int distFromCenter;
  int angle;
  int forwardCm;
  int currAngle;
  int tileLength = 30;
  bool noBlack = true;
  //no walls
  if (left > 20 && right > 20 || left + ROBOT_WIDTH + right <25) {
    int di = getDirection(euler.x());
    if(di!=-1)
      turnAbsNoVictim(di);
    if (!goForwardTilesPID(1))
      return false;
    return true;
  }
  
  //closer to right wall
  if (left > right) {
    distFromCenter = (tileLength/2) - (right + ROBOT_WIDTH / 2);
    if (distFromCenter == 0)
      angle = 0;
    else
      angle = (90 - atan2(30, distFromCenter) * 360 / (2 * PI));
    forwardCm = sqrt(pow(distFromCenter, 2) + 900);
    if(getDirection(euler.x()!=-1))
      currAngle = getDirection(euler.x());
     else
      currAngle = euler.x();
    //    Serial3.print("RIGHT, distFromCenter: ");
    //    Serial3.print(distFromCenter);
    //    Serial3.print(" angle: ");
    //    Serial3.print(angle);
    //    Serial3.print(" forwardCM: ");
    //    Serial3.print(forwardCm);
    //    Serial3.print(" currAng: ");
    //    Serial3.println(currAngle);
    int ang = currAngle - angle;
    if (ang > 360) ang = ang % 360;
    if(ang < 0) ang = ang + 360;
    turnAbsNoVictim(ang);
    //Serial3.println("Done turn");
    noBlack = goForwardPID(forwardCm);
    //Serial3.println("Done forward");
    turnAbsNoVictim(currAngle);
    //Serial3.println("Done adjust");

    //closer to left wall
  } else {
    distFromCenter = (tileLength/2) - (left + ROBOT_WIDTH / 2);
    if (distFromCenter == 0)
      angle = 0;
    else
      angle = (90-atan2(30, distFromCenter) * 360 / (2 * PI));
    forwardCm = sqrt(pow(distFromCenter, 2) + 900);
    if(getDirection(euler.x()!=-1))
      currAngle = getDirection(euler.x());
    else
      currAngle = euler.x();
    //    Serial3.print("LEFT, distFromCenter: ");
    //    Serial3.print(distFromCenter);
    //    Serial3.print(" angle: ");
    //    Serial3.print(angle);
    //    Serial3.print(" forwardCM: ");
    //    Serial3.print(forwardCm);
    //    Serial3.print(" currAng: ");
    //    Serial3.println(currAngle);
    int ang = currAngle + angle;
    if (ang > 360) ang = ang % 360;
    if(ang < 0) ang = ang + 360;
    turnAbsNoVictim(ang);
    //Serial3.println("Done turn");
    noBlack = goForwardPID(forwardCm);
    //Serial3.println("Done forward");
    turnAbsNoVictim(currAngle);
    // Serial3.println("Done adjust");

  }
//  Serial3.print("noBlack: ");
//  Serial3.println((int)noBlack);
  return noBlack;
}

int isOnRamp() {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  //if(frontTof>50) return 0;
  if (euler.y() < -15) {
    int ang = euler.x();
    if(getDirection(ang)!=-1)
      turnAbs(getDirection(ang));
    return 2;
  }
  else if (euler.y() > 15) {
    int ang = euler.x();
    if(getDirection(ang)!=-1)
      turnAbs(getDirection(ang));
    return 1;
  }
  return 0;
}

bool notStable() {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  if (abs(euler.y()) > 2)
    return true;
  return false;
}

bool isOnSpeedBump() {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  if (euler.y() > 2)
    return true;
  return false;
}

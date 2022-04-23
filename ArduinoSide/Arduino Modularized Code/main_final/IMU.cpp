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

void displayIMU(){
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);  
  while(true){
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);  
    Serial.println(euler.x());
  }
}
void turnRight(int degree){
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);  
    int curr = euler.x();
    int target = curr+degree%360;
    int error = target-curr;
    while(error >=2){
      euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);  
      error = target-euler.x();
      Serial.print("error: ");
      Serial.println(error);
      ports[RIGHT].setMotorSpeed(-150);
      ports[LEFT].setMotorSpeed(150);
    }
    ports[RIGHT].setMotorSpeed(0);
    ports[LEFT].setMotorSpeed(0);
}

void turnAbs(int degree){
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);  
  int dir[4] = {0, 90, 180, 270};
  int fix;
  int curDir=euler.x();
  int targetDir=degree;
  double integral=0.0;
  int error=targetDir-curDir;
  double pastError = 0;
  while (abs(error)>=2) {
    //victim();
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    curDir=euler.x();
    error = targetDir-curDir;
    if(error>180){
      error-=360;
    }else if(error<-180)
      error=360+error;
    fix = (int)(PID(error, pastError, integral, 1.6667, 0.005, 0));
    if(fix>0)
      fix+=80;
    else 
      fix-=80;
    Serial.print(fix);
    Serial.print("\tEuler: ");
    Serial.print(euler.x());
    Serial.print("\terror: ");
    Serial.println(error);
    ports[RIGHT].setMotorSpeed(-fix);
    ports[LEFT].setMotorSpeed(fix);
    //Serial.println(euler.x());
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
    distFromCenter = abs(15 - (right + ROBOT_WIDTH / 2));
    if(distFromCenter==0)
      angle=0;
    else
      angle = (90-atan2(30, distFromCenter) * 360 / (2 * 3.1415927));
    forwardCm = sqrt(pow(distFromCenter, 2) + 900);
    currAngle = euler.x();
    Serial.print("RIGHT, distFromCenter: ");
    Serial.print(distFromCenter);
    Serial.print(" angle: ");
    Serial.print(angle);
    Serial.print(" forwardCM: ");
    Serial.print(forwardCm);
    Serial.print(" currAng: ");
    Serial.println(currAngle);
    turnAbs((int)(currAngle - angle + 360) % 360);
    Serial.println("Done turn");
    goForwardPID(forwardCm);
    Serial.println("Done forward");
    turnAbs(currAngle);
    Serial.println("Done adjust");

    //closer to left wall
  } else {
    distFromCenter = abs(15 - (left + ROBOT_WIDTH / 2));
    if(distFromCenter==0)
      angle=0;
    else
      angle = (90-atan2(30, distFromCenter) * 360 / (2 * 3.1415927));
    forwardCm = sqrt(pow(distFromCenter, 2) + 900);
    currAngle = euler.x();
    Serial.print("LEFT, distFromCenter: ");
    Serial.print(distFromCenter);
    Serial.print(" angle: ");
    Serial.print(angle);
    Serial.print(" forwardCM: ");
    Serial.print(forwardCm);
    Serial.print(" currAng: ");
    Serial.println(currAngle);
    turnAbs((int)(currAngle + angle) % 360);
     Serial.println("Done turn");
    goForwardPID(forwardCm);
    Serial.println("Done forward");
    turnAbs(currAngle);
    Serial.println("Done adjust");

  }
}

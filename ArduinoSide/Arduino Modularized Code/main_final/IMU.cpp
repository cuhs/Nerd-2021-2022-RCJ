#include "IMU.h"

//MeEncoderMotor leftMotor(18, PORT1B);
//MeEncoderMotor rightMotor(19, PORT2B);

//Adafruit_BNO055 bno;
//int resetPin = A6;

//MeMegaPiDCMotor leftMotor(PORT2B);
//MeMegaPiDCMotor rightMotor(PORT1B);

int resetPinIMU = A6;
Adafruit_BNO055 bno;


void initIMU() {
  pinMode(resetPinIMU, OUTPUT);
  digitalWrite(resetPinIMU, HIGH);

  if (!bno.begin(Adafruit_BNO055::OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }

  delay(100);

  bno.setExtCrystalUse(true);
}

void reset() {
  Serial.println("Resetting.");
  digitalWrite(resetPinIMU, LOW);

  delayMicroseconds(30);

  digitalWrite(resetPinIMU, HIGH);

  bno.begin();
}

void turnRight(int deg)
{
  int speed = 220;
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  deg = deg - 7;

  while (euler.x() < deg || euler.x() > 350) {
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    ports[RIGHT].setMotorSpeed(-speed);
    ports[LEFT].setMotorSpeed(speed);

    Serial.println(euler.x());
  }
  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
  reset();
}

void turnLeft(int deg)
{
  int speed = 220;
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  deg = deg - 7;

  while (euler.x() > 360 - deg || euler.x() < 15) {
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    ports[RIGHT].setMotorSpeed(speed);
    ports[LEFT].setMotorSpeed(-speed);
    Serial.println(euler.x());
  }
  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
  reset();
}

void turnRightPID(int deg)
{
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  double pastError = 0;
  double integral = 0;
  int fix = 0;

  deg = deg - 7;

  while (euler.x() < deg || euler.x() > 350) {
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

    fix = (int)(PID(deg - euler.x(), pastError, integral, 1, 0, 0));
    Serial.println("Deg: " + String(deg));
    Serial.println("Cur: " + String(euler.x()));
    Serial.println("Err: " + String(deg - euler.x()));
    Serial.println("Fix: " + String(fix));
    Serial.println("Lmt: " + String(60 + fix));
    Serial.println("Rmt: " + String(-(60 + fix)));
    Serial.println();

    ports[RIGHT].setMotorSpeed(-60 - fix);
    ports[LEFT].setMotorSpeed(60 + fix);

    //Serial.println(euler.x());
  }
  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
  reset();
}
void turnRightPID(char t){
  t = tolower(t);

  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  delay(10);

  float dir[4] = {0, 90, 180, 270};
  int range[4][2] = {{350, 10}, {80, 100}, {170, 190}, {260, 280}};
  char dirChar[4] = {'n', 'e', 's', 'w'};
  double pastError = 0;
  double integral = 0;
  int fix = 0;
  
}

void turnLeftPID(int deg)
{
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  double pastError = 0;
  double integral = 0;
  int fix = 0;

  deg = deg - 7;

  while (euler.x() > 360 - deg || euler.x() < 15) {
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

    fix = (int)(PID(abs(euler.x() - (360 - deg)), pastError, integral,
1, 0, 0));
    Serial.println(fix);
    Serial.print("Euler: ");
    Serial.println(euler.x());

    ports[RIGHT].setMotorSpeed(60 + fix);
    ports[LEFT].setMotorSpeed(-60 - fix);
    //Serial.println(euler.x());
  }
  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
  reset();
}

void turnAbs(char t) {

  t = tolower(t);

  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  delay(10);

  float dir[4] = {0, 90, 180, 270};
  int range[4][2] = {{350, 10}, {80, 100}, {170, 190}, {260, 280}};
  char dirChar[4] = {'n', 'e', 's', 'w'};

  int targetDir;
  int currDir;
  const int errorRoom = 1.25;

  int speed = 150;

  for (int i = 0; i < 4; i++) {

    if (range[i][0] < euler.x() && range[i][1] > euler.x()) {
      currDir = i;
      break;
    }
  }

  if (t == 'r') {
    Serial.print("turning right");
    currDir == 3 ? targetDir = 0 : targetDir = currDir + 1;

    if (targetDir == 0) {
      while (!((euler.x() > 360 - errorRoom &&  euler.x() <360) ||
(euler.x() < errorRoom && euler.x() > 0))) {
        euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
        ports[RIGHT].setMotorSpeed(-speed);
        ports[LEFT].setMotorSpeed(speed);
        Serial.println(euler.x());
      }
    }

    else {

      while (!(euler.x() > dir[targetDir] - errorRoom && euler.x() <
dir[targetDir] + errorRoom)) {
        euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
        ports[RIGHT].setMotorSpeed(-speed);
        ports[LEFT].setMotorSpeed(speed);
        Serial.println(euler.x());
      }
    }
  }

  else if (t == 'l') {
    Serial.println("turning left");
    currDir == 0 ? targetDir = 3 : targetDir = currDir - 1;

    if (targetDir == 0) {
      while (!((euler.x() > 360 - errorRoom &&  euler.x() <360) ||
(euler.x() < errorRoom && euler.x() > 0))) {
        euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
        ports[RIGHT].setMotorSpeed(speed);
        ports[LEFT].setMotorSpeed(-speed);
        Serial.println(euler.x());
      }
    }
    else {

      while (!(euler.x() > dir[targetDir] - errorRoom && euler.x() <
dir[targetDir] + errorRoom)) {
        euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
        ports[RIGHT].setMotorSpeed(speed);
        ports[LEFT].setMotorSpeed(-speed);
        Serial.println(euler.x());
      }
    }
  }

  else {
    Serial.println("U DIDNT PUT THE RIGHT LETTER YA FOOL!!!!!");
  }

  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
}

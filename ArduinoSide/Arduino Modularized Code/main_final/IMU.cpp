#include "IMU.h"

//MeEncoderMotor leftMotor(18, PORT1B);
//MeEncoderMotor rightMotor(19, PORT2B);

//Adafruit_BNO055 bno;
//int resetPin = A6;

//MeMegaPiDCMotor leftMotor(PORT2B);
//MeMegaPiDCMotor rightMotor(PORT1B);

int resetPinIMU = A6;
Adafruit_BNO055 bno;


void initIMU(){
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
  int speed = 250;
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  deg = deg-7;

  while(euler.x() < deg || euler.x()>350){
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
 int speed = 250;
 imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

 deg = deg-7;

  while(euler.x() > 360 - deg || euler.x() < 15){
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

  deg = deg-7;

  while(euler.x() < deg || euler.x()>350){
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

    fix = (int)(PID(deg-euler.x(),pastError,integral,1,0,0));
    Serial.println("Deg: " + String(deg));
    Serial.println("Cur: " + String(euler.x()));
    Serial.println("Err: " + String(deg-euler.x()));
    Serial.println("Fix: " + String(fix));
    Serial.println("Lmt: " + String(60 + fix));
    Serial.println("Rmt: " + String(-(60 + fix)));
    Serial.println();

    ports[RIGHT].setMotorSpeed(60+fix);
    ports[LEFT].setMotorSpeed(60+fix);
    
    //Serial.println(euler.x());
  }
    ports[LEFT].setMotorSpeed(0);
    ports[RIGHT].setMotorSpeed(0);
    reset();
}

void turnLeftPID(int deg)
{
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  double pastError = 0;
  double integral = 0;
  int fix = 0;

 deg = deg-7;

  while(euler.x() > 360 - deg || euler.x() < 15){
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

    fix = (int)(PID(euler.x()-(360-deg), pastError, integral, 0,0,0));
    Serial.println(fix);
      
    ports[RIGHT].setMotorSpeed(150);
    ports[LEFT].setMotorSpeed(-150);
    //Serial.println(euler.x());
  }
    ports[LEFT].setMotorSpeed(0);
    ports[RIGHT].setMotorSpeed(0);
    reset();
}

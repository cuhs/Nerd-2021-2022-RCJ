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
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  while(euler.x() < deg || euler.x()>350){
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    ports[RIGHT].setMotorSpeed(-200);
    ports[LEFT].setMotorSpeed(200);
    
    Serial.println(euler.x());
  }
    ports[LEFT].setMotorSpeed(0);
    ports[RIGHT].setMotorSpeed(0);
    reset();
}

void turnLeft(int deg)
{
 imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  while(euler.x() > 360 - deg || euler.x() < 15){
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    ports[RIGHT].setMotorSpeed(200);
    ports[LEFT].setMotorSpeed(-200);
    Serial.println(euler.x());
  }
    ports[LEFT].setMotorSpeed(0);
    ports[RIGHT].setMotorSpeed(0);
    reset();
}

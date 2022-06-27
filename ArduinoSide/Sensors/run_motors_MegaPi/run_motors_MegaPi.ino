#include "MeMegaPi.h"

MeMegaPiDCMotor leftMotor(PORT2B);
MeMegaPiDCMotor rightMotor(PORT1B);

//MeMegaPiDCMotor leftMotor(PORT2A);
//MeMegaPiDCMotor rightMotor(PORT2B);

void setup() {
  Serial.begin(9600);

}

void loop() {
  leftMotor.run(200);
  rightMotor.run(200);
//  delay(500);
//  leftMotor.run(0);
//  rightMotor.run(0);
//  delay(100);
//  leftMotor.run(-255);
//  rightMotor.run(255);
//  delay(500);
  
  Serial.println("running motors");

}

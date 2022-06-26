#include "Distance_Sensor.h"

VL53L0X lox;//Right: 0 Left: 1 Front: 2
VL53L0X sensor[numSensors];
int frontTof = 0;

//function to send wall values to the pi
void sendWallValues(int frontDist, int rightDist, int leftDist) {
  char walls[3] = {'0', '0', '0'};
  int minimumDist = 20; // Minimum distance to determine if there is a wall on the side
  //frontTof = frontDist;
  if (leftDist < minimumDist)
    walls[2] = '1';
  if (rightDist < minimumDist)
    walls[1] = '1';
  if (frontDist < minimumDist)
    walls[0] = '1';

  // for debugging
  Serial3.print("[");
  for (int i = 0; i < 3; i++) {
    Serial3.print(walls[i]);
    if (i != 4)
      Serial3.print(", "); //for formatting purposes, no technical meaning
    else
      Serial3.print("]");
  }
  Serial3.println();

  delay(1);
  Serial2.write(walls, 3);
  delay(1);
}

//max is eight sensors allowed, sets up ToF sensors
void setupSensors2() {
  if (numSensors > 8) {
    Serial3.println("Max number of sensors!");
    return;
  }
  for (int i = 0; i < numSensors; i++) {
    tcaselect(i);
    sensor[i].setTimeout(500);
    if (!sensor[i].init())
    {
      Serial3.print("Failed to detect and initalize sensor: ");
      Serial3.println(i);
      while (1) {}
    }
    sensor[i].startContinuous();
  }
}

//aligns the robot if there is a wall in front to 5cm from the wall
int alignFront(bool b) {
  int frontDist = getSensorReadings(2);
  int minimumDist = 25;
  int motorEncUse = LEFT;
  int initEncCount = ports[motorEncUse].count;
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);

  if (frontDist < minimumDist) {
    //go back
    while (frontDist < 5) {
      victim();
      ports[RIGHT].setMotorSpeed(-100);
      ports[LEFT].setMotorSpeed(-100);
      frontDist = getSensorReadings(2);
    }
    
    //go forward
    while (frontDist > 5) {
      victim();
      ports[RIGHT].setMotorSpeed(100);
      ports[LEFT].setMotorSpeed(100);
      frontDist = getSensorReadings(2);
    }
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
  return ((ports[motorEncUse].count - initEncCount)*D*PI)/360;
}

//overloaded alignFront
void alignFront(){
  alignFront(true);
}

//gets the sensor readings of a ToF sensor - right is 0, left is 1, front is 2
int getSensorReadings(int num) {
  tcaselect(num);
  int error = 0;
  
  if(num==0)
    error = 0;
  else if(num==1)
    error = 1;
  else if(num==2)
    error = 1;
  return lox.readRangeContinuousMillimeters()/10-error;
  //return lox.readRangeContinuousMillimeters() / 10;
}

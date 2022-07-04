#include "Distance_Sensor.h"

VL53L0X lox;//Right: 0 Left: 1 Front: 2
VL53L0X sensor[numSensors];

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
  SERIAL3_PRINT("[")
  for (int i = 0; i < 3; i++) {
    SERIAL3_PRINT(walls[i])
    if (i != 4){
      SERIAL3_PRINT(", ") //for formatting purposes, no technical meaning
    }else{
      SERIAL3_PRINT("]")
    }
  }
  SERIAL3_PRINTLN("")

  delay(1);
  Serial2.write(walls, 3);
  delay(1);
}

//max is eight sensors allowed, sets up ToF sensors
void setupSensors2() {
  if (numSensors > 8) {
    SERIAL3_PRINTLN("Max number of sensors!")
    return;
  }
  for (int i = 0; i < numSensors; i++) {
    tcaselect(i);
    sensor[i].setTimeout(500);
    if (!sensor[i].init())
    {
      SERIAL3_PRINT("Failed to detect and initalize sensor: ")
      SERIAL3_PRINTLN(i)
      while (1) {}
    }
    sensor[i].startContinuous();
  }
}

//aligns the robot if there is a wall in front to 5cm from the wall
int alignFront(bool b) {
  int frontDist = getSensorReadings(FRONT_TOF);
  int minimumDist = 25;
  int motorEncUse = LEFT;
  int initEncCount = ports[motorEncUse].count;

  //variables used for stall detection
  unsigned long startTime;
  unsigned long endTime;
  int prev_count = 0;
  bool stalling = false;
  bool checking = false;
  
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);

  if (frontDist < minimumDist && !stalling) {
    //go back
    while (frontDist < 5) {
      victim();
      ports[RIGHT].setMotorSpeed(-100);
      ports[LEFT].setMotorSpeed(-100);
      frontDist = getSensorReadings(FRONT_TOF);
    if (ports[LEFT].count == prev_count && !checking) {
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
      checking = false;
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      endTime = millis();
      if (endTime - startTime > 1000) {
        SERIAL3_PRINTLN("STALLING")
        stalling = true;
      }
    }
    prev_count = ports[LEFT].count;
    }
    
    //go forward
    while (frontDist > 5 && !stalling) {
      victim();
      ports[RIGHT].setMotorSpeed(100);
      ports[LEFT].setMotorSpeed(100);
      frontDist = getSensorReadings(FRONT_TOF);
    if (ports[LEFT].count == prev_count && !checking) {
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
      checking = false;
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      endTime = millis();
      if (endTime - startTime > 1000) {
        SERIAL3_PRINTLN("STALLING")
        stalling = true;
      }
    }
    prev_count = ports[LEFT].count;
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

#include "Distance_Sensor.h"

VL53L0X lox;//Right: 0 Left: 1 Front: 2
VL53L0X sensor[numSensors];
int frontTof = 0;

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
  Serial.print("[");
  for (int i = 0; i < 3; i++) {
    Serial.print(walls[i]);
    if (i != 4)
      Serial.print(", "); //for formatting purposes, no technical meaning
    else
      Serial.print("]");
  }
  Serial.println();

  delay(1);
  Serial2.write(walls, 3);
  delay(1);
}

//max is eight sensors allowed
void setupSensors2() {
  if (numSensors > 8) {
    Serial.println("Max number of sensors!");
    return;
  }
  for (int i = 0; i < numSensors; i++) {
    tcaselect(i);
    sensor[i].setTimeout(500);
    if (!sensor[i].init())
    {
      Serial.print("Failed to detect and initalize sensor: ");
      Serial.println(i);
      while (1) {}
    }
    sensor[i].startContinuous();
  }
}

void alignFront() {
  int frontDist = getSensorReadings(2);
  int minimumDist = 25;

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
}

int getSensorReadings(int num) {
  tcaselect(num);
  int error = 0;
  int readings[3];
  
  if(num==0)
    error = 2;
  else if(num==1)
    error = 1;
  else if(num==2)
    error = 1;
  if(num==0 || num == 1){
  for(int i = 0; i < 3; i++){
    readings[i] = lox.readRangeContinuousMillimeters()/10-error;
  }
  
  for(int i = 1; i < 3; i++){
    if(readings[i] < readings[i-1]){
      int temp = readings[i];
      readings[i] = readings[i-1];
      readings[i-1] = temp;
      --i;
    }
  }
  return readings[1];
  }else
    return lox.readRangeContinuousMillimeters()/10-error;
  //return lox.readRangeContinuousMillimeters() / 10;
}

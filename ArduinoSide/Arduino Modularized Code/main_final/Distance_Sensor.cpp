#include "Distance_Sensor.h"
VL53L0X lox;
VL53L0X sensor[numSensors];
//VL53L0X_RangingMeasurementData_t measure;
void sendWallValues(int frontDist, int rightDist, int leftDist) {
  char walls[3] = {'0', '0', '0'};
  int minimumDist = 15; // Minimum distance to determine if there is a wall on the side

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
      if(i!=4)
        Serial.print(", "); //for formatting purposes, no technical meaning
      else
        Serial.print("]");
  }
  Serial.println();
  Serial2.write(walls, 3);
}

void setupSensors() {
  tcaselect(0);
  if (!lox.init()) {
    Serial.println("Failed to boot VL53L0X (0)");
    while (1);
  }
  lox.startContinuous();
  tcaselect(1);
  if (!lox.init()) {
    Serial.println("Failed to boot VL53L0X (1)");
    while (1);
  }
  lox.startContinuous();
  tcaselect(2);
  if (!lox.init()) {
    Serial.println("Failed to boot VL53L0X (2)");
    while (1);
  }
  lox.startContinuous();
  tcaselect(3);
  if (!lox.init()) {
    Serial.println("Failed to boot VL53L0X (3)");
    while (1);
  }
  lox.startContinuous();
  tcaselect(4);
  if (!lox.init()) {
    Serial.println("Failed to boot VL53L0X (4)");
    while (1);
  }
  lox.startContinuous();
}

//max is eight sensors allowed 
void setupSensors2(){
  if(numSensors>8){
    Serial.println("Max number of sensors!");
    return;
  }
  for(int i = 0; i<numSensors; i++){
    tcaselect(i);
    sensor[i].setTimeout(500);
    if(!sensor[i].init())
    {
      Serial.print("Failed to detect and initalize sensor: ");
      Serial.println(i);
      while (1) {}
    }
    sensor[i].startContinuous();
  }
}

void alignSide(int leftDist, int rightDist){
   int minimumDist = 30; // Minimum distance to determine if there is a wall on the side
  if(leftDist < minimumDist && rightDist<minimumDist){
    if(rightDist>leftDist){
      while(abs(rightDist-leftDist) > 1){
        ports[RIGHT].setMotorSpeed(150);
        ports[LEFT].setMotorSpeed(-150);
      }
    }
    else{
      while(abs(rightDist-leftDist)>1){
        ports[RIGHT].setMotorSpeed(-150);
        ports[LEFT].setMotorSpeed(150);
      }
    }
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void alignFront(){
  int frontDist = getSensorReadings(2); 
  int minimumDist = 15;

  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
  
  if(frontDist < minimumDist){
    while(frontDist < 5){
      ports[RIGHT].setMotorSpeed(-150);
      ports[LEFT].setMotorSpeed(-150);
      frontDist = getSensorReadings(2);
    }
    while(frontDist>5){
      ports[RIGHT].setMotorSpeed(150);
      ports[LEFT].setMotorSpeed(150);
      frontDist = getSensorReadings(2);
      }
  }
      

  
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void triangulate(int leftDist, int rightDist){
  int minimumDist = 30;
  int tR;
  int tL;
  int travelDist = 0; 
  int angle = 0;
  if(leftDist < minimumDist){
    
    travelDist = sqrt(900+pow(abs(leftDist-tL),2));
    angle = atan2(30.0,abs(leftDist-tL));
    angle = angle*180/PI;

    if(leftDist-tL > 0){
      turnRight(angle);
      goForward(travelDist);
      turnLeft(angle);

    }
    else{
      turnLeft(angle);
      goForward(travelDist);
      turnRight(angle);


    }
  }
  
  else if(rightDist < minimumDist){
    travelDist = sqrt(900+pow(abs(rightDist-tR),2));
    angle = atan2(30,abs(rightDist-tR));
    angle = angle*180/PI;

    if(rightDist-tR > 0){
      turnLeft(angle);
      goForward(travelDist);
      turnRight(angle);

      
    }
    else{
      turnRight(angle);
      goForward(travelDist);
      turnLeft(angle);

    }
  }

  else{
    goForwardTiles(1);
  }
  
}

int getSensorReadings(int num) {
  tcaselect(num);
  return lox.readRangeContinuousMillimeters()/10;
}

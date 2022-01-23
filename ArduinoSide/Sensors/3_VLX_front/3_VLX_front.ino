

#include <Wire.h>
#include "VL53L0X.h"

#define TCAADDR 0x70

//enum obstacleStates {FARLEFT, LEFT, MID, RIGHT, FARRIGHT, NONE};
VL53L0X lox;


void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

void setup() {
  Serial.begin(9600);
  while (! Serial) {
    delay(1);
  }
  
  
  tcaselect(0);
  lox.setTimeout(500);
  lox.init();
  lox.startContinuous();
  /*if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X 1"));
    while(1);
  }*/
  tcaselect(1);
  lox.setTimeout(500);
  lox.init();
  lox.startContinuous();
  /*if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X 2"));
    while(1);
  }*/
  tcaselect(2);
  lox.setTimeout(500);
  lox.init();
  lox.startContinuous();
  /*if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X 3"));
    while(1);
  }*/
  
  
}

void loop() {
  //VL53L0X_RangingMeasurementData_t measure;
  //double m1;
  //double m2;
  //double m3;
  //obstacleStates st = NONE;
  
  tcaselect(0);
  Serial.print("Port 0: " + lox.readRangeContinuousMillimeters());
  if (lox.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
  tcaselect(1);
  Serial.print("Port 1: " + lox.readRangeContinuousMillimeters());
  if (lox.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
  tcaselect(2);
  Serial.print("Port 2: " + lox.readRangeContinuousMillimeters());
  if (lox.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
/*if(m2 <= (m1-10) && m2 <= (m3-10)){
  st = MID;
  Serial.print("Middle");
}else if(m1 <= (m2-10) && m1 <= (m3-10)){
  st = FARLEFT;
  Serial.print("Far Left");
}else if(m3 <= (m2-10) && m3 <= (m1-10)){
  st = FARRIGHT;
  Serial.print("Far Right");
}else if(m1 <= (m3-10) && m2 <= (m3-10)){
  st = LEFT;
  Serial.print("Left");
}else if(m3 <= (m1-10) && m2 <= (m1-10)){
  st = RIGHT;
  Serial.print("Right");
}else{
  st = NONE;
  Serial.print("None");
}*/
//Serial.print(m1); Serial.print(" ");
//Serial.print(m2); Serial.print(" ");  
//Serial.print(m3); Serial.println(" ");
}

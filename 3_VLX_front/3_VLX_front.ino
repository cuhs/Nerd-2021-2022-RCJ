

#include <Wire.h>
#include "Adafruit_VL53L0X.h"

#define TCAADDR 0x70

enum obstacleStates {FARLEFT, LEFT, MID, RIGHT, FARRIGHT, NONE};
Adafruit_VL53L0X lox = Adafruit_VL53L0X();


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
  lox.begin();
  /*if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X 1"));
    while(1);
  }*/
  tcaselect(1);
  lox.begin();
  /*if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X 2"));
    while(1);
  }*/
  tcaselect(2);
  lox.begin();
  /*if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X 3"));
    while(1);
  }*/
  
  
}

void loop() {
  VL53L0X_RangingMeasurementData_t measure;
  double m1;
  double m2;
  double m3;
  obstacleStates st = NONE;
  
  tcaselect(0);
  lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!
  //Serial.print(F("Distance Sensor 1(cm): ")); 
  if (measure.RangeStatus != 4) {  // phase failures have incorrect data
    m1 = (measure.RangeMilliMeter)/10;
    if(m1<0){
     m1=0;
    }
   // Serial.print(m1);
  } else {
    m1 = 50;
    //Serial.print(F(" out of range "));
  }
  tcaselect(1);
  lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!
  //Serial.print(F(" Distance Sensor 2(cm): ")); 
  if (measure.RangeStatus != 4) {  // phase failures have incorrect data
    m2 = (measure.RangeMilliMeter)/10;
    if(m2<0){
     m2=0;
    }
   // Serial.print(m2);
  } else {
    m2 = 50;
   // Serial.print(F(" out of range "));
  }
  tcaselect(2);
  lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!
  //Serial.print(F(" Distance Sensor 3(cm): ")); 
  if (measure.RangeStatus != 4) {  // phase failures have incorrect data
    m3 = (measure.RangeMilliMeter)/10;
    if(m3<0){
     m3=0;
    }
    //Serial.print(F(" Distance Sensor 3(cm): ")); Serial.println(m3);
  } else {
    m3 = 50;
    //Serial.println(F(" out of range "));
  }
if(m2 <= (m1-10) && m2 <= (m3-10)){
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
}
//Serial.print(m1); Serial.print(" ");
//Serial.print(m2); Serial.print(" ");  
//Serial.print(m3); Serial.println(" ");
}

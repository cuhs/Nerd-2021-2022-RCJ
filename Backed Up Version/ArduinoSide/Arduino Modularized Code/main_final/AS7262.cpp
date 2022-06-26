#include "AS7262.h"
uint16_t sensorValues[AS726x_NUM_CHANNELS];
Adafruit_AS726x ams;

void setupLightSensors(){
  tcaselect(3);
  if(!ams.begin()){
    Serial3.println("could not connect to sensor! Please check your wiring.");
    while(1);
  }
  ams.drvOn();
}

//detects if there is a silver or black tile - returns 1 if a black tile is detected, 2 for silver tile, and 0 if none are detected
int detectTiles(){
  tcaselect(3);
  ams.startMeasurement();
  bool rdy=false;
  while(!rdy){
    delay(5);
    rdy = ams.dataReady();
  }
  ams.readRawValues(sensorValues);
  uint8_t v=sensorValues[AS726x_VIOLET];
  uint8_t b=sensorValues[AS726x_BLUE];
  uint8_t g=sensorValues[AS726x_GREEN];
  uint8_t y=sensorValues[AS726x_YELLOW];
  uint8_t o=sensorValues[AS726x_ORANGE];
  uint8_t r=sensorValues[AS726x_RED];
  int avg = (v+b+g+y+o+r)/5;
  int range = findRange(v,b,g,y,o,r);
  if(range>500)
    return 0;
  if(range<=60 && avg <=60){
    //sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
    //Serial2.write(';');
    //Serial3.println("Saw Black");
    return 1;
  }else if(range >= 150){
    //sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
    //Serial2.write(';');
    //Serial3.println("Saw Silver");
    return 2;
  }
  return 0;
}

int maxSix(int a, int b, int c, int d, int e, int f){
  return max(max(max(a, b),max(c,d)),max(e,f));
}
int minSix(int a, int b, int c, int d, int e, int f){
  return min(min(min(a, b),min(c,d)),min(e,f));
}
int findRange(int a, int b, int c, int d, int e, int f){
  return maxSix(a,b,c,d,e,f)-minSix(a,b,c,d,e,f);
}

//gets the numerical range of color data
int getRange(){
  tcaselect(3);
  ams.startMeasurement();
  bool rdy=false;
  while(!rdy){
    delay(5);
    rdy = ams.dataReady();
  }
  ams.readRawValues(sensorValues);
  uint8_t v=sensorValues[AS726x_VIOLET];
  uint8_t b=sensorValues[AS726x_BLUE];
  uint8_t g=sensorValues[AS726x_GREEN];
  uint8_t y=sensorValues[AS726x_YELLOW];
  uint8_t o=sensorValues[AS726x_ORANGE];
  uint8_t r=sensorValues[AS726x_RED];
  return findRange(v,b,g,y,o,r);
}

/***************************************************************************
  This is a library for the Adafruit AS7262 6-Channel Visible Light Sensor

  This sketch reads the sensor

  Designed specifically to work with the Adafruit AS7262 breakout
  ----> http://www.adafruit.com/products/3779
  
  These sensors use I2C to communicate. The device's I2C address is 0x49
  Adafruit invests time and resources providing this open source code,
  please support Adafruit andopen-source hardware by purchasing products
  from Adafruit!
  
  Written by Dean Miller for Adafruit Industries.
  BSD license, all text above must be included in any redistribution
 ***************************************************************************/

#include <Wire.h>
#include "Adafruit_AS726x.h"
#define TCAADDR 0x70

extern "C" {
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}

//create the object
Adafruit_AS726x ams;

//buffer to hold raw values
uint16_t sensorValues[AS726x_NUM_CHANNELS];

//buffer to hold calibrated values (not used by default in this example)
//float calibratedValues[AS726x_NUM_CHANNELS];
void tcaselect(uint8_t i) {
  if (i > 7) return;

  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  
  Serial3.begin(9600);
  //while(!Serial3);
  Wire.begin();
  Serial3.println("in setup");
  // initialize digital pin LED_BUILTIN as an output.
  //begin and make sure we can talk to the sensor
  tcaselect(3);
  if(!ams.begin()){
    Serial3.println("could not connect to sensor! Please check your wiring.");
    while(1);
  }
    ams.drvOn();
  for(int i = 0; i < 10; i++){
    Serial3.println("Im about to start");
  }
}

void loop() {

  //read the device temperature
  uint8_t temp = ams.readTemperature();
 
  
   //uncomment this if you want to use the driver LED for readings
  ams.startMeasurement(); //begin a measurement
  
  //wait till data is available
  bool rdy = false;
  //int time = millis();
  while(!rdy){
    delay(5);
    rdy = ams.dataReady();
  }
//  time = millis()-time;
//  Serial3.print("Time for dataReady: "); Serial3.print(time);
  //ams.drvOff(); //uncomment this if you want to use the driver LED for readings

  //read the values!
  ams.readRawValues(sensorValues);

  //Serial3.print(" Temp: "); Serial3.print(temp);
  uint8_t v=sensorValues[AS726x_VIOLET];
  uint8_t b=sensorValues[AS726x_BLUE];
  uint8_t g=sensorValues[AS726x_GREEN];
  uint8_t y=sensorValues[AS726x_YELLOW];
  uint8_t o=sensorValues[AS726x_ORANGE];
  uint8_t r=sensorValues[AS726x_RED];
  if(maxSix(v,b,g,y,o,r)<500){
  Serial3.print(" Violet:"); Serial3.print(v); Serial3.print(" ");
  Serial3.print(" Blue:"); Serial3.print(b); Serial3.print(" ");
  Serial3.print(" Green:"); Serial3.print(g); Serial3.print(" ");
  Serial3.print(" Yellow:"); Serial3.print(y);Serial3.print(" ");
  Serial3.print(" Orange:"); Serial3.print(o); Serial3.print(" ");
  Serial3.print(" Red:"); Serial3.print(r); Serial3.print(" ");
  Serial3.print(" Avg:"); Serial3.println((v+b+g+y+o+r)/5);
  }
//printRange();
//detectTiles();
}

void detectTiles(){
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
  int range = maxSix(v,b,g,y,o,r)-minSix(v,b,g,y,o,r);
  if(range<=40 && avg <=15)
    Serial3.println("Black detected");
  else if(range >= 150)
    Serial3.println("Silver detected");
}

int maxSix(int a, int b, int c, int d, int e, int f){
  return max(max(max(a, b),max(c,d)),max(e,f));
}
int minSix(int a, int b, int c, int d, int e, int f){
  return min(min(min(a, b),min(c,d)),min(e,f));
}

void printRange(){
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
  int range = maxSix(v,b,g,y,o,r)-minSix(v,b,g,y,o,r);
  Serial3.print(" range: "); Serial3.println(range);
}

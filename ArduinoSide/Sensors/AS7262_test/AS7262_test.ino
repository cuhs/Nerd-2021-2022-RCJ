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
  Serial.begin(9600);
  while(!Serial);
  
  // initialize digital pin LED_BUILTIN as an output.
  //begin and make sure we can talk to the sensor
  tcaselect(3);
  if(!ams.begin()){
    Serial.println("could not connect to sensor! Please check your wiring.");
    while(1);
  }
    ams.drvOn();
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
//  Serial.print("Time for dataReady: "); Serial.print(time);
  //ams.drvOff(); //uncomment this if you want to use the driver LED for readings

  //read the values!
  ams.readRawValues(sensorValues);

  //Serial.print(" Temp: "); Serial.print(temp);
//  uint8_t v=sensorValues[AS726x_VIOLET];
//  uint8_t b=sensorValues[AS726x_BLUE];
//  uint8_t g=sensorValues[AS726x_GREEN];
//  uint8_t y=sensorValues[AS726x_YELLOW];
//  uint8_t o=sensorValues[AS726x_ORANGE];
//  uint8_t r=sensorValues[AS726x_RED];
//  
//  Serial.print(" Violet:"); Serial.print(v); Serial.print(" ");
//  Serial.print(" Blue:"); Serial.print(b); Serial.print(" ");
//  Serial.print(" Green:"); Serial.print(g); Serial.print(" ");
//  Serial.print(" Yellow:"); Serial.print(y);Serial.print(" ");
//  Serial.print(" Orange:"); Serial.print(o); Serial.print(" ");
//  Serial.print(" Red:"); Serial.print(r); Serial.print(" ");
//  Serial.print(" Avg:"); Serial.println((v+b+g+y+o+r)/5);
detectTiles();
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
    Serial.println("Black detected");
  else if(range >= 150)
    Serial.println("Silver detected");
}

int maxSix(int a, int b, int c, int d, int e, int f){
  return max(max(max(a, b),max(c,d)),max(e,f));
}
int minSix(int a, int b, int c, int d, int e, int f){
  return min(min(min(a, b),min(c,d)),min(e,f));
}

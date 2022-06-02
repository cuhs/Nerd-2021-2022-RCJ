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

//create the object
Adafruit_AS726x ams;

//buffer to hold raw values
uint16_t sensorValues[AS726x_NUM_CHANNELS];

//buffer to hold calibrated values (not used by default in this example)
//float calibratedValues[AS726x_NUM_CHANNELS];

void setup() {
  Serial.begin(9600);
  while(!Serial);
  
  // initialize digital pin LED_BUILTIN as an output.
  //pinMode(LED_BUILTIN, OUTPUT);
  pinMode(7, OUTPUT);
  digitalWrite(7,HIGH);
  //begin and make sure we can talk to the sensor
  if(!ams.begin()){
    Serial.println("could not connect to sensor! Please check your wiring.");
    while(1);
  }
}

void loop() {

  //read the device temperature
  uint8_t temp = ams.readTemperature();
 
  
  //ams.drvOn(); //uncomment this if you want to use the driver LED for readings
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
 // time = millis();
  ams.readRawValues(sensorValues);
//  time = millis() - time;
//  Serial.print(" Time for readRawValues: "); Serial.print(time);
  //ams.readCalibratedValues(calibratedValues);

  //Serial.print(" Temp: "); Serial.print(temp);
  uint8_t v=sensorValues[AS726x_VIOLET];
  uint8_t b=sensorValues[AS726x_BLUE];
  uint8_t g=sensorValues[AS726x_GREEN];
  uint8_t y=sensorValues[AS726x_YELLOW];
  uint8_t o=sensorValues[AS726x_ORANGE];
  uint8_t r=sensorValues[AS726x_RED];
  
  Serial.print(" Violet: "); Serial.print(v);
  Serial.print(" Blue: "); Serial.print(b);
  Serial.print(" Green: "); Serial.print(g);
  Serial.print(" Yellow: "); Serial.print(y);
  Serial.print(" Orange: "); Serial.print(o);
  Serial.print(" Red: "); Serial.print(r);
  Serial.print(" Avg: "); Serial.print((v+b+g+y+o+r)/5);
  Serial.println();
  Serial.println();
}

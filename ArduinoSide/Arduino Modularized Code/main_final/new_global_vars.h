#ifndef _global_vars_h_
#define _global_vars_h_

#include <MeMegaPi.h>
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>

//#define SERIAL3_DEBUGGING  // comment out to disable debugging

#ifdef SERIAL3_DEBUGGING
#define SERIAL3_PRINT(str) Serial3.print(str);
#define SERIAL3_PRINTLN(str) Serial3.println(str);
#define SERIAL3_BEGIN Serial3.begin(9600);
#else
#define SERIAL3_PRINT(str) Serial.print(str);
#define SERIAL3_PRINTLN(str) Serial.println(str);
#define SERIAL3_BEGIN 
#endif

extern int finishedRamp;
extern bool isHeat;
extern int rampTilesWent;
#endif

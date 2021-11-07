#ifndef _global_vars_h_
#define _global_vars_h_
#pragma once
#include <MeMegaPi.h>
#include <Arduino.h>
#include <Wire.h>
#include <utility/imumaths.h>

Adafruit_VL53L0X lox = Adafruit_VL53L0X();
Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_700MS, TCS34725_GAIN_1X);
Servo myservo; 
bool shouldRun = true;
int ct = 0;
#endif

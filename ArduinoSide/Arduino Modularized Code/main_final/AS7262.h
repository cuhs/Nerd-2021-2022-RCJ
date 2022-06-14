#ifndef _AS7262_
#define _AS7262_

#include <Wire.h>
#include "Adafruit_AS726x.h"
#include "TCA.h"

//create the object
extern Adafruit_AS726x ams;

//buffer to hold raw values
extern uint16_t sensorValues[AS726x_NUM_CHANNELS];

void setupLightSensors();
int detectTiles();
int maxSix(int,int,int,int,int,int);
int minSix(int,int,int,int,int,int);
int findRange(int,int,int,int,int,int);
int getRange();

#endif

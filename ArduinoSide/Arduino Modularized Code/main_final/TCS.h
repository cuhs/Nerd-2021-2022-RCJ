#ifndef TCS_DEF
#define TCS_DEF

#include "Adafruit_TCS34725.h"
#include "TCA.h"
#include "Distance_Sensor.h"

void setupTCSSensors();
void getValues();
bool detectBlack();
extern Adafruit_TCS34725 tcs;
extern const int TCSLEDpin;

#endif

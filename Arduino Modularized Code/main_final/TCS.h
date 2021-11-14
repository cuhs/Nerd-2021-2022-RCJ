#include "Adafruit_TCS34725.h"
#include "TCA.h"
void setupTCSSensors();
Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_700MS, TCS34725_GAIN_1X);

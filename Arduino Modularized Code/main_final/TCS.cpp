#include "TCS.h"
void setupTCSSensors() {
  tcaselect(5);
  if (tcs.begin()) {
    Serial.println("Found sensor");
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }
}

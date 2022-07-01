#include "TCS.h"

Adafruit_TCS34725 tcs;
const int TCSLEDpin = 48;

//sets up light sensors
void setupTCSSensors() {
  tcaselect(3);
  pinMode(TCSLEDpin, OUTPUT);
  digitalWrite(TCSLEDpin, HIGH);
  if (tcs.begin()) {
    SERIAL3_PRINTLN("Found sensor")
  } else {
    SERIAL3_PRINTLN("No TCS34725 found ... check your connections")
    while (1);
  }
}

//for debugging
void getValues() {
  tcaselect(3);
  uint16_t r, g, b, c, colorTemp, lux;

  tcs.getRawData(&r, &g, &b, &c);
  // colorTemp = tcs.calculateColorTemperature(r, g, b);
  colorTemp = tcs.calculateColorTemperature_dn40(r, g, b, c);
  lux = tcs.calculateLux(r, g, b);

//  SERIAL3_PRINT("Color Temp: "); SERIAL3_PRINT(colorTemp, DEC); SERIAL3_PRINT(" K - ");
//  SERIAL3_PRINT("Lux: "); SERIAL3_PRINT(lux, DEC); SERIAL3_PRINT(" - ");
//  SERIAL3_PRINT("R: "); SERIAL3_PRINT(r, DEC); SERIAL3_PRINT(" ");
//  SERIAL3_PRINT("G: "); SERIAL3_PRINT(g, DEC); SERIAL3_PRINT(" ");
//  SERIAL3_PRINT("B: "); SERIAL3_PRINT(b, DEC); SERIAL3_PRINT(" ");
//  SERIAL3_PRINT("C: "); SERIAL3_PRINT(c, DEC); SERIAL3_PRINT(" ");
//  SERIAL3_PRINTLN(" ");
  delay(20);
}

bool detectBlack(bool shouldM) {
  tcaselect(3);
  uint16_t r, g, b, c, lux;
  tcs.getRawData(&r, &g, &b, &c);
  lux = tcs.calculateLux(r, g, b);
//  SERIAL3_PRINT("lux: ");
//  SERIAL3_PRINTLN(lux);
  if (lux <= 1 && c <5) { //lux value changed
    if(shouldM){
      Serial2.write('m');
    }
    Serial2.write(';');
    Serial2.write('b');
    //sendWallValues(getSensorReadings(FRONT_TOF), getSensorReadings(RIGHT_TOF), getSensorReadings(LEFT_TOF));
    //Serial2.write(';');
    //SERIAL3_PRINTLN("Saw Black");
    return true;
  }
  return false;
}

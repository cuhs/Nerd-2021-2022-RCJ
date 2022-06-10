#include "TCS.h"

Adafruit_TCS34725 tcs;
const int TCSLEDpin = 48;

//sets up light sensors
void setupTCSSensors() {
  tcaselect(3);
  pinMode(TCSLEDpin, OUTPUT);
  digitalWrite(TCSLEDpin, HIGH);
  if (tcs.begin()) {
    Serial3.println("Found sensor");
  } else {
    Serial3.println("No TCS34725 found ... check your connections");
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

//  Serial3.print("Color Temp: "); Serial3.print(colorTemp, DEC); Serial3.print(" K - ");
//  Serial3.print("Lux: "); Serial3.print(lux, DEC); Serial3.print(" - ");
//  Serial3.print("R: "); Serial3.print(r, DEC); Serial3.print(" ");
//  Serial3.print("G: "); Serial3.print(g, DEC); Serial3.print(" ");
//  Serial3.print("B: "); Serial3.print(b, DEC); Serial3.print(" ");
//  Serial3.print("C: "); Serial3.print(c, DEC); Serial3.print(" ");
//  Serial3.println(" ");
  delay(20);
}

bool detectBlack(bool shouldM) {
  tcaselect(3);
  uint16_t r, g, b, c, lux;
  tcs.getRawData(&r, &g, &b, &c);
  lux = tcs.calculateLux(r, g, b);
//  Serial3.print("lux: ");
//  Serial3.println(lux);
  if (lux <= 1 && c <5) { //lux value changed
    if(shouldM){
      Serial2.write('m');
    }
    Serial2.write(';');
    Serial2.write('b');
    //sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
    //Serial2.write(';');
    Serial3.println("Saw Black");
    return true;
  }
  return false;
}

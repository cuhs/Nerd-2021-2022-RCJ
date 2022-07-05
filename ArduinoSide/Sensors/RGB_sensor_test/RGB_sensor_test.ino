#include "Adafruit_TCS34725.h"
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>

Adafruit_TCS34725 tcs;
#define TCAADDR 0x70

extern "C" {
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}

//selects MUX port
void tcaselect(uint8_t i) {
  if (i > 7) return;

  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  Serial3.begin(9600);
  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);
  tcs.begin();
  //tcs.setGain(TCS34725_GAIN_16X);
//  tcs.begin();
  tcaselect(6);
  delay(500);

}

void loop() {
  uint16_t r, g, b, c, colorTemp, lux;

  tcs.getRawData(&r, &g, &b, &c);
  // colorTemp = tcs.calculateColorTemperature(r, g, b);
//  colorTemp = tcs.calculateColorTemperature_dn40(r, g, b, c);
  lux = tcs.calculateLux(r, g, b);
  Serial3.print("Lux: ");
  Serial3.print(lux, DEC); Serial3.print(" ");
  Serial3.print("R: ");
  Serial3.print(r, DEC); Serial3.print(" ");
  Serial3.print("G: ");
  Serial3.print(g, DEC); Serial3.print(" ");
  Serial3.print("B: ");
  Serial3.print(b, DEC);
  Serial3.print(" ");
  Serial3.print("C: ");
  Serial3.print(c, DEC); Serial3.print(" ");
  Serial3.println();
//  Serial3.print("r/g: ");
//  Serial3.print((double)r/g);
//  Serial3.print(" r/b: ");
//  Serial3.print((double)r/b);
//  Serial3.print(" g/b: ");
//  Serial3.println((double)g/b);
//  delay(20);
// white: R: 625, G: 600 B: 550 C: 1025 Lux: 375
// black: R: 80, G: 48 B: 39 C: 160 Lux: 25
// silver: R: 600, G: 550, B: 450, C: 1025, Lux: 290

}

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
  Serial.begin(9600);
  pinMode(48, OUTPUT);
  digitalWrite(48, HIGH);
  tcs.begin();
  tcaselect(3);

}

void loop() {
  uint16_t r, g, b, c, colorTemp, lux;

  tcs.getRawData(&r, &g, &b, &c);
  // colorTemp = tcs.calculateColorTemperature(r, g, b);
  colorTemp = tcs.calculateColorTemperature_dn40(r, g, b, c);
  lux = tcs.calculateLux(r, g, b);

  Serial.print("Color Temp: "); Serial.print(colorTemp, DEC); Serial.print(" K - ");
  Serial.print("Lux: "); Serial.print(lux, DEC); Serial.print(" - ");
  Serial.print("R: "); Serial.print(r, DEC); Serial.print(" ");
  Serial.print("G: "); Serial.print(g, DEC); Serial.print(" ");
  Serial.print("B: "); Serial.print(b, DEC); Serial.print(" ");
  Serial.print("C: "); Serial.print(c, DEC); Serial.print(" ");
  Serial.println(" ");
  delay(20);

}

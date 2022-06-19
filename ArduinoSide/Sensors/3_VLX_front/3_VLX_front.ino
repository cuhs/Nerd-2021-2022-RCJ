/* This example shows how to use continuous mode to take
range measurements with the VL53L0X. It is based on
vl53l0x_ContinuousRanging_Example.c from the VL53L0X API.

The range readings are in units of mm. */

#include <Wire.h>
#include <VL53L0X.h>
#define TCAADDR 0x70
VL53L0X sensor[3];

void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}
void setup()
{
  Serial3.begin(9600);
  Wire.begin();
  tcaselect(0);
  sensor[0].setTimeout(500);
  if (!sensor[0].init())
  {
    Serial3.println("Failed to detect and initialize sensor!");
    while (1) {}
  }
  sensor[0].startContinuous();
  tcaselect(1);
  sensor[1].setTimeout(500);
  if (!sensor[1].init())
  {
    Serial3.println("Failed to detect and initialize sensor!");
    while (1) {}
  }
  sensor[1].startContinuous();
  tcaselect(2);
  sensor[2].setTimeout(500);
  if (!sensor[2].init())
  {
    Serial3.println("Failed to detect and initialize sensor!");
    while (1) {}
  }
  sensor[2].startContinuous();
  // Start continuous back-to-back mode (take readings as
  // fast as possible).  To use continuous timed mode
  // instead, provide a desired inter-measurement period in
  // ms (e.g. sensor.startContinuous(100)).
}

void loop()
{
  tcaselect(0);
  Serial3.print("Sensor0:" + String(sensor[0].readRangeContinuousMillimeters()));
  if (sensor[0].timeoutOccurred()) { Serial3.print(" TIMEOUT"); }

  //Serial3.println();
  tcaselect(1);
  Serial3.print(" Sensor1:" + String(sensor[1].readRangeContinuousMillimeters()));
  if (sensor[1].timeoutOccurred()) { Serial3.print(" TIMEOUT"); }

  //Serial3.println();
  tcaselect(2);
  Serial3.println(" Sensor2:" + String(sensor[2].readRangeContinuousMillimeters()));
  if (sensor[2].timeoutOccurred()) { Serial3.print(" TIMEOUT"); }

  Serial3.println();
}

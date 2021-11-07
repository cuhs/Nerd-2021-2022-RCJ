
#include "Distance_Sensor.cpp"
int getSensorReadings(int sensorNum) {
  tcaselect(sensorNum);
  lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!

  //if (measure.RangeStatus != 4) {  // phase failures have incorrect data
  //Serial.print('L'); Serial.print(sensorNum); Serial.print(": "); Serial.print((measure.RangeMilliMeter) / 10); Serial.println(" ");
  //} else {
  //Serial.print('L'); Serial.print(sensorNum); Serial.print(": "); Serial.print("OOR"); Serial.println(" ");
  //}
  return measure.RangeMilliMeter / 10;
}

void setupSensors() {
  tcaselect(0);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (0)");
    while (1);
  }
  tcaselect(1);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (1)");
    while (1);
  }
  tcaselect(2);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (2)");
    while (1);
  }
  tcaselect(3);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (3)");
    while (1);
  }
  tcaselect(4);
  if (!lox.begin()) {
    Serial.println("Failed to boot VL53L0X (4)");
    while (1);
  }
  
}

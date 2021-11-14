#include "Distance_Sensor.h"
void sendWallValues(int leftDist, int rightDist, int frontDist) {
  char walls[3] = {'0', '0', '0'};
  int minimumDist = 30; // Minimum distance to determine if there is a wall on the side

  if (leftDist < minimumDist)
    walls[0] = '1';
  if (rightDist < minimumDist)
    walls[1] = '1';
  if (frontDist < minimumDist)
    walls[2] = '1';

  // for debugging
  for (int i = 0; i < 3; i++) {
    if (i != 2)
      Serial.print(walls[i]);
    else
      Serial.println(walls[i]);
  }

  Serial2.write(walls, 3);
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

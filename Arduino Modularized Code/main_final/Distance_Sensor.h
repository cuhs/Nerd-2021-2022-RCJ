#include "Adafruit_VL53L0X.h"
void sendWallValues(int leftDist, int rightDist, int frontDist);
void setupSensors();
int getSensorReadings(int sensorNum);
Adafruit_VL53L0X lox = Adafruit_VL53L0X();
VL53L0X_RangingMeasurementData_t measure;

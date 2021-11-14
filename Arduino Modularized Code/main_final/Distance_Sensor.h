#ifndef _VLX_HEAD_
#define _VLX_HEAD_
#include "Adafruit_VL53L0X.h"
#include "TCA.h"
void sendWallValues(int leftDist, int rightDist, int frontDist);
void setupSensors();
int getSensorReadings(int sensorNum);
extern Adafruit_VL53L0X lox;
extern VL53L0X_RangingMeasurementData_t measure;
#endif

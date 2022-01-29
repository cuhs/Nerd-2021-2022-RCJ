#ifndef _VLX_HEAD_
#define _VLX_HEAD_
#include "VL53L0X.h"
#include "TCA.h"
void sendWallValues(int leftDist, int rightDist, int frontDist);
void setupSensors();
void setupSensors2();
int getSensorReadings(int sensorNum);
extern VL53L0X lox;
const int numSensors = 3;
extern VL53L0X sensor[numSensors]; //Change depending on number of sensors
//extern VL53L0X_RangingMeasurementData_t measure;
#endif

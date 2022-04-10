#ifndef _VLX_HEAD_
#define _VLX_HEAD_
#include "VL53L0X.h"
#include "TCA.h"
#include "motors.h"
#include "IMU.h"
#include "rescueServo.cpp"

void sendWallValues(int frontDist, int rightDist, int leftDist);
void setupSensors();
void setupSensors2();
void alignSide(int leftDist, int rightDist);
void triangulate(int leftDist, int rightDist);
void alignFront();
int getSensorReadings(int sensorNum);
extern VL53L0X lox;
const int numSensors = 3;
extern VL53L0X sensor[numSensors]; //Change depending on number of sensors
//extern VL53L0X_RangingMeasurementData_t measure;
#endif

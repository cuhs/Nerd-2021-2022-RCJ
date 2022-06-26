#ifndef _VLX_HEAD_
#define _VLX_HEAD_

#include "VL53L0X.h"
#include "TCA.h"
#include "motors.h"
#include "IMU.h"
#include "rescueServo.h"

void sendWallValues(int frontDist, int rightDist, int leftDist);
void setupSensors2();
int alignFront(bool);
void alignFront();
int getSensorReadings(int sensorNum);

const int numSensors = 3;
extern VL53L0X lox;
extern VL53L0X sensor[numSensors]; //Change depending on number of sensors

#endif

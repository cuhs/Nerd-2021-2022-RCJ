#ifndef _MOTORIMU_H_
#define _MOTORIMU_H_

#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include "motors.h"
#include "rescueServo.h"

void initIMU();
void reset();
void turnAbs(char t);
void turnAbs(int);
void turnAbsNoVictim(int);
bool triangulation(int, int);
bool isOnRamp();
bool notStable();
void displayIMU();
void turnRight(int);

extern int resetPinIMU;
extern Adafruit_BNO055 bno;

#endif

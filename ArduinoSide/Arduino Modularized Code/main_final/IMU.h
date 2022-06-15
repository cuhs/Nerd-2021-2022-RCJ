#ifndef _MOTORIMU_H_
#define _MOTORIMU_H_

#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include "motors.h"
#include "rescueServo.h"
#include "new_global_vars.h"
#include "TCA.h"
#include "limitswitch.h"

void initIMU();
void reset();
int getDirection(int);
void turnAbs(char t);
void turnAbs(int);
void turnAbsNoVictim(int);
bool triangulation(int, int);
int isOnRamp();
bool notStable();
void displayIMU();
void turnRight(int);
bool isNearTarget(int, int);
bool isOnSpeedBump();

extern int resetPinIMU;
extern Adafruit_BNO055 bno;

#endif

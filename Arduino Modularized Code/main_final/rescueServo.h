#ifndef _SERVO_
#define _SERVO_
//#include <Servo.h>
#include "new_global_vars.h"
extern Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards
//int pos = 0;    // variable to store the servo position
extern bool shouldRun;
extern int ct;

bool stuckTest(int target);
void wiggle(int target, int times);
void turnLeft();
void midPos();
void turnRight();
#endif

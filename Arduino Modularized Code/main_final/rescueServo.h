#include <Servo.h>
#include "new_global_vars.h"
Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards
//int pos = 0;    // variable to store the servo position
bool shouldRun = true;
int ct = 0;

bool stuckTest(int target);
void wiggle(int target, int times);
void turnLeft();
void midPos();
void turnRight();

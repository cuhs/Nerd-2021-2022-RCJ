#ifndef _SERVO_
#define _SERVO_
//#include <Servo.h>
#include "new_global_vars.h"
#include "motors.h"
#include "MLX.h"
extern Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards
//int pos = 0;    // variable to store the servo position
extern const int R_angle;
extern const int L_angle;
extern const int C_angle;

void wiggle(char angle);
void dropKits(char dir, int amt);
void setupServo();
void victim();
void RGB_color(int red_light_value, int green_light_value, int blue_light_value);

#endif

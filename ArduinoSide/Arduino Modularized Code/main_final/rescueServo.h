#ifndef _SERVO_
#define _SERVO_

#include "new_global_vars.h"
#include "motors.h"
#include "MLX.h"

extern Servo myservo;  // create servo object to control a servo
extern const int R_angle;
extern const int L_angle;
extern const int C_angle;

void turnTo(int);
void wiggle(char angle, int, int, int);
void dropKits(char dir, int amt, int, int, int);
void victim();
void victimForward(int);
void RGB_color(int red_light_value, int green_light_value, int blue_light_value, int, char);
void turnOnLED(bool,int,int,int);
bool stringchr(const char*, char);

#endif

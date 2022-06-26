#include "limitswitch.h"

void setupSwitches(){
  pinMode(LEFT_SWITCH, INPUT_PULLUP);
  pinMode(RIGHT_SWITCH, INPUT_PULLUP);
}

//detects if the limit switches are pressed - 'l' if the left is pressed, 'r' if the right is pressed
char obstacleDetect(){
  if((int)(digitalRead(LEFT_SWITCH))==0)
    return 'r';
  if((int)(digitalRead(RIGHT_SWITCH))==0)
    return 'l';
  return '0';
}

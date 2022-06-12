#include "limitswitch.h"

void setupSwitches(){
  pinMode(LEFT_SWITCH, INPUT_PULLUP);
  pinMode(RIGHT_SWITCH, INPUT_PULLUP);
}

char obstacleDetect(){
//  Serial3.print("left switch: ");
//  Serial3.print(digitalRead(LEFT_SWITCH));
//  Serial3.print("\tright switch: ");
//  Serial3.println(digitalRead(RIGHT_SWITCH));
  if((int)(digitalRead(LEFT_SWITCH))==0)
    return 'l';
  if((int)(digitalRead(RIGHT_SWITCH))==0)
    return 'r';

  return '0';
}

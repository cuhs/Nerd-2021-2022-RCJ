#include "limitswitch.h"

void setupSwitches(){
  pinMode(LEFT_SWITCH, INPUT_PULLUP);
  pinMode(RIGHT_SWITCH, INPUT_PULLUP);
}

char obstacleDetect(){
  Serial.print("left switch: ");
  Serial.print(digitalRead(LEFT_SWITCH));
  Serial.print("\tright switch: ");
  Serial.println(digitalRead(RIGHT_SWITCH));
  if((int)(digitalRead(LEFT_SWITCH))==0)
    return 'l';
  if((int)(digitalRead(RIGHT_SWITCH))==0)
    return 'r';

  return '0';
}

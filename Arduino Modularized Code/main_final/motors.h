#pragma once
#include <MeMegaPi.h>
#include <Arduino.h>
#define INIT_INTERRUPT(index)   attachInterrupt(digitalPinToInterrupt(ports[index].intPin), motorinterrupt<index>, RISING)
#define LEFT 1
#define RIGHT 0

const float WB = 23.285;
const float D = 6.45;

 
    MegaPiPort ports[] = { {PORT1B, 18, 31}, {PORT2B, 19, 38}, {PORT3B, 3, 49}, {PORT4B, 2, A1}};
    void doTurn(char dir, int deg);
    void goForward(int dist);
    void goForwardTiles(int tiles);
    void motorControl();
  void alignToTile();
  void alignRobot():

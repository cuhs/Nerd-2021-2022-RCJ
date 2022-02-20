#ifndef _MOTOR_H_
#define _MOTOR_H_
#define LEFT 1
#define RIGHT 0
#include "new_global_vars.h"
#include "Distance_Sensor.h"
#include "PID.h"
#include <MeMegaPi.h>
// For Turns and Movement
const double WB = 23.285; //23.285
const double D = 5.9; //6.9 6.5

void doTurn(char dir, int deg);
void goForward(int dist);
void goForwardTiles(int tiles);
void goForwardTilesPID(int tiles);
void getDist(int start);
void motorControl();
void alignLeft();
void alignRight();
//void alignFront();
void alignRobot();
void alignToTile();

class MegaPiPort: public MeMegaPiDCMotor {
  public:
    // Volatile used on class variables to read them from memory in case they changed since the last read
    bool  backwards; // For when the motor needs to be reversed
    volatile uint8_t port; // Motor port connected to MegaPi
    volatile uint8_t intPin; // Interrupt pin used with motor
    volatile uint8_t encPin; // Encoder pin for motor port
    volatile long    count; // Encoder count

    // Constructor
    MegaPiPort(uint8_t port_num, uint8_t interupt_pin, uint8_t encoder_pin)
      : MeMegaPiDCMotor(port_num), port(port_num), intPin(interupt_pin), encPin(encoder_pin), backwards(false) { };

    // Sets the speed of the motors
    inline void setMotorSpeed(int16_t spd) {
      // Set motor speed
      int true_speed = (backwards) ? -spd : spd;
      // Run specified speed
      MeMegaPiDCMotor::run(true_speed);
    };
};
extern MegaPiPort ports[];
extern char message[4];
// macro to attach the interrupt to the port
#define INIT_INTERRUPT_LEFT   attachInterrupt(digitalPinToInterrupt(ports[LEFT].intPin), motorinterruptleft, RISING)
#define INIT_INTERRUPT_RIGHT   attachInterrupt(digitalPinToInterrupt(ports[RIGHT].intPin), motorinterruptright, RISING)
//template <int PN>
void motorinterruptleft();
void motorinterruptright();
#endif

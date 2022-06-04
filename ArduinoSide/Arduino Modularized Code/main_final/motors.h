#ifndef _MOTOR_H_
#define _MOTOR_H_

#include "new_global_vars.h"
#include "Distance_Sensor.h"
#include "PID.h"
#include "rescueServo.h"
#include "AS7262.h"
#include "Distance_Sensor.h"
#include "IMU.h"
#include "limitswitch.h"
#include <MeMegaPi.h>

#define LEFT 1
#define RIGHT 0
// macro to attach the interrupt to the port
#define INIT_INTERRUPT_LEFT   attachInterrupt(digitalPinToInterrupt(ports[LEFT].intPin), motorinterruptleft, RISING)
#define INIT_INTERRUPT_RIGHT   attachInterrupt(digitalPinToInterrupt(ports[RIGHT].intPin), motorinterruptright, RISING)

// For Turns and Movement
const double WB = 16; //23.285
const double D = 7; //6.9 6.5

bool goForwardTilesPID(int tiles);
bool goForwardPID(int dist);
void plainGoForward(int dist);
void motorinterruptleft();
void motorinterruptright();
int rampMoveForward(char);

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
#endif

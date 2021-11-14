#define LEFT 1
#define RIGHT 0
#include "new_global_vars.h"
#include "Distance_Sensor.h"
#include <MeMegaPi.h>
// For Turns and Movement
float WB = 23.285;
float D = 6.45;
void doTurn(char dir, int deg);
void goForward(int dist);
void goForwardTiles(int tiles);
void getDist(int start);
void motorControl();
void alignLeft();
void alignRight();
void alignFront();
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
volatile  MegaPiPort ports[] = { {PORT1B, 18, 31}, {PORT2B, 19, 38}, {PORT3B, 3, 49}, {PORT4B, 2, A1}};
char message[4] = {'a', 'a', 'a', 'a'};
// macro to attach the interrupt to the port
#define INIT_INTERRUPT(index)   attachInterrupt(digitalPinToInterrupt(ports[index].intPin), motorinterrupt<index>, RISING)
template <int PN>

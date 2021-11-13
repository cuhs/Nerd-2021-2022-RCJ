/*#ifndef _global_vars_h_
#define _global_vars_h_

#include <MeMegaPi.h>
#include <Arduino.h> 
//#include <Servo.h>

#include <Wire.h> IN NEW GLOB VAR */
#include <Adafruit_Sensor.h>
/*#include <Adafruit_BNO055.h> 
#include <utility/imumaths.h> IN IMU.H*/

/*extern "C" {
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
} IN TCA.H*/
/*#include "Adafruit_VL53L0X.h" IN DISTANCESENSOR.h */
//#include "Adafruit_TCS34725.h" IN TCS.H

// Function prototypes
/*void doTurn(char dir, int deg);
void goForward(int dist);
void goForwardTiles(int tiles);
void getDist(int start);
void motorControl(); IN MOTORS.H */
//void sendWallValues(int leftDist, int rightDist, int frontDist); IN VLX.H
//void tcaselect(uint8_t i); IN TCA.H
//void setupSensors(); SPLIT INTO VLX AND TCS.H (NEEDS FIXING UP)
//int getSensorReadings(int sensorNum); IN VLX.H
/*void alignLeft();
void alignRight();
void alignFront();
void alignRobot(); IN MOTORS.H*/

//Adafruit_VL53L0X lox = Adafruit_VL53L0X(); IN VLX.H
//Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_700MS, TCS34725_GAIN_1X); in TCS.H
//VL53L0X_RangingMeasurementData_t measure; IN VLX.H

// I2C address of MUX
//#define TCAADDR 0x70 IN TCA.H

// MegaPi encoder class code
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

// ports[0] = port1 on the board
volatile  MegaPiPort ports[] = { {PORT1B, 18, 31}, {PORT2B, 19, 38}, {PORT3B, 3, 49}, {PORT4B, 2, A1}};

// macro to attach the interrupt to the port
#define INIT_INTERRUPT(index)   attachInterrupt(digitalPinToInterrupt(ports[index].intPin), motorinterrupt<index>, RISING)

#define LEFT 1
#define RIGHT 0

// For Turns and Movement
float WB = 23.285;
float D = 6.45;

// For Serial Communication
char message[4] = {'a', 'a', 'a', 'a'};

// For Servo
Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards
//int pos = 0;    // variable to store the servo position
bool shouldRun = true;
int ct = 0;

#endif

#include "new_global_vars.h"
#include "Distance_Sensor.h"
#include "IMU.h"
#include "TCA.h"
#include "TCS.h"
#include "motors.h"
#include "rescueServo.h"

//N E S W --> South always 0

void setup() {
  delay(100);
  Serial.begin(9600);
  Serial2.begin(9600);
  Wire.begin();

  setupServo();

  // macros
  INIT_INTERRUPT_LEFT;
  INIT_INTERRUPT_RIGHT;

  ports[RIGHT].backwards = true;


  Serial.println("--------------------STARTING NOW--------------------");
  setupSensors2();
  initIMU();

  Serial2.write('a');
  sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
}

void loop() {
  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    Serial.println("Message detected.");

    switch (incoming_byte) {
      case '{':
        Serial.println("{");
        break;

      case 'F':
        //get rid of semicolon
        Serial2.read();
        
        Serial.println("forward!");
        goForwardTilesPID(1);
        alignFront();
        Serial2.write(';');
        break;
        
      case 'L':
        //get rid of semicolon
        Serial2.read();
        
        Serial.println("left!");
        turnAbs('l');
        
        Serial2.write(';');
        break;

      case 'R':
        //get rid of semicolon
        Serial2.read();
        
        Serial.println("right!");
        turnAbs('r');
        
        Serial2.write(';');
        break;
        
      case '}':
        Serial.println("}");
        sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
        break;

      default:
        Serial.print("hmmm wut is this: ");
        Serial.println(incoming_byte);
        break;
    }
  }
}

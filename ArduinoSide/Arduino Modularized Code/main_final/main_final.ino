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
  setupTCSSensors();

  // macros
  INIT_INTERRUPT_LEFT;
  INIT_INTERRUPT_RIGHT;

  ports[RIGHT].backwards = true;


  Serial.println("--------------------STARTING NOW--------------------");
  setupSensors2();
  initIMU();
  delay(2000);
  Serial.println('a');
  Serial2.write('a');
  sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
}

void loop() {
 // triangulation(getSensorReadings(1), getSensorReadings(0));
//turnRight(90);
//delay(1000);
//turnAbs(270);
//while(true);
  //while(true) displayIMU();
  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    Serial.print("Message detected: ");
    Serial.println(incoming_byte);
    switch (incoming_byte) {
      case '{':
       // Serial.println("read {");
        break;
      case '*':
      case 'D':
      case 'F':
        //get rid of semicolon
        delay(1);
        Serial2.read();
        delay(1);
        
       // Serial.println("forward!");
        //goForwardTilesPID(1);
        if(triangulation(getSensorReadings(1), getSensorReadings(0))){
        alignFront();
        delay(1);
        Serial2.write(';');
        delay(1);
        Serial.println(';');
        }
        Serial.println("finished going forward");
        break;
        
      case 'L':
        //get rid of semicolon
        delay(1);
        Serial2.read();
        delay(1);
        
        //Serial.println("left!");
        turnAbs('l');

        delay(1);
        Serial2.write(';');
        delay(1);
        Serial.println(';');
        break;

      case 'R':
        //get rid of semicolon
        delay(1);
        Serial2.read();
        delay(1);
        
       // Serial.println("right!");
        turnAbs('r');

        delay(1);
        Serial2.write(';');
        delay(1);
        Serial.println(';');
        break;
        
      case '}':
        Serial.println("}");
        if(finishedRamp==1)
          Serial2.write('u');
        else if(finishedRamp==2)
          Serial2.write('d');
        finishedRamp=0;
        sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
        break;
      case 'Y': // 1 kit
        Serial.println("red/yellow");
        RGB_color(255, 0, 0); // Red
        dropKits('L', 1);
        break;

      case 'G': // 0 kits
        Serial.println("green");
        RGB_color(0, 255, 0); // Green
        break;

      case 'H': // 3 kits
        Serial.println("H");
        RGB_color(0, 0, 255); // Blue
        dropKits('L', 3);
        break;

      //turn left
      case 'S': // 2 kits
        Serial.println("S");
        RGB_color(0, 255, 255); // Cyan
        dropKits('L', 2);
        break;

      //turn right
      case 'U': // 0 kits
        Serial.println("U");
        RGB_color(255, 0, 255); // Magenta
        break;
        
      default:
        Serial.print("hmmm wut is this: ");
        Serial.println(incoming_byte);
        break;
    }
  }
}

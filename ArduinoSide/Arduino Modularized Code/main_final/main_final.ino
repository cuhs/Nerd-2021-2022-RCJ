#include "new_global_vars.h"
#include "Distance_Sensor.h"
#include "IMU.h"
#include "TCA.h"
#include "AS7262.h"
#include "motors.h"
#include "rescueServo.h"
#include "limitswitch.h"

//N E S W --> South always 0
void setup() {
  delay(100);
  Serial3.begin(9600);
  Serial2.begin(9600);
  Wire.begin();
  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
  setupLightSensors();
  setupSwitches();

  // macros
  INIT_INTERRUPT_LEFT;
  INIT_INTERRUPT_RIGHT;

  ports[RIGHT].backwards = true;


  Serial3.println("--------------------STARTING NOW--------------------");
  setupSensors2();
  initIMU();
  delay(1000);
  Serial3.println('a');
  Serial2.write('a');
  while(!Serial2.available());
  char c = Serial2.read();
  if(c=='a'){
    turnAbsNoVictim(90);
    if(getSensorReadings(0)<20)
      Serial2.write('1');
    else
      Serial2.write('0');
    turnAbsNoVictim(0);
  }
  sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
}

void loop() {
  //wait for the StereoPi to send a Serial message with directions or victims
  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    Serial3.print("Message detected: ");
    Serial3.println(incoming_byte);
    //make sure that if a victim is detected, it is within 25 cm from the robot
    if (!stringchr("YGHSUyghsu", incoming_byte) || (stringchr("yghsu", incoming_byte) && getSensorReadings(1) < 25) || (stringchr("YGHSU", incoming_byte) && getSensorReadings(0) < 25)) { //if letter is uppercase
    switch (incoming_byte) {
      case '{':
        break;
      case 'W'://message the pi sends when it sees an up ramp on the next tile in the map
        rampMoveForward('u');
        finishedRamp=0;
        delay(1);
        Serial2.write(';');
        delay(1);
        break;
      case 'M'://message the pi sends when it sees a down ramp on the next tile in the map
        rampMoveForward('d');
        finishedRamp=0;
        delay(1);
        Serial2.write(';');
        delay(1);
        break;
      case 'F'://message to go forward(triangulation)
        //get rid of semicolon
        delay(1);
        Serial2.read();
        delay(1);
        if(triangulation(getSensorReadings(1), getSensorReadings(0))){
        alignFront();
        delay(1);
        Serial2.write(';');
        delay(1);
        Serial3.println(';');
        }
        break;
        
      case 'L'://turn left
        //get rid of semicolon
        delay(1);
        Serial2.read();
        delay(1);
        turnAbs('l');
        //if(!isHeat){
        delay(1);
        Serial2.write(';');
        delay(1);
        Serial3.println(';');
        break;

      case 'R'://turn right
        //get rid of semicolon
        delay(1);
        Serial2.read();
        delay(1);
        turnAbs('r');
        //if(!isHeat){
        delay(1);
        Serial2.write(';');
        delay(1);
        Serial3.println(';');        
        break;
        
      case '}'://pi wants wall values to be sent from the arduino
        Serial3.println("}");
        if(finishedRamp==1)
          Serial2.write('u');
        else if(finishedRamp==2)
          Serial2.write('d');
        finishedRamp=0;
        delay(15);
        sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
        break;
      //victim messages
      case 'Y': // 1 kit
        Serial3.println("red/yellow");
        RGB_color(255, 0, 0, 1, 'R'); // Red
        //dropKits('R', 1);
        break;

      case 'G': // 0 kits
        Serial3.println("green");
        RGB_color(0, 255, 0, 0, 'R'); // Green
        break;

      case 'H': // 3 kits
        Serial3.println("H");
        RGB_color(0, 0, 255, 3, 'R'); // Blue
        //dropKits('R', 3);
        break;

      //turn left
      case 'S': // 2 kits
        Serial3.println("S");
        RGB_color(0, 255, 255, 2, 'R'); // Cyan
        //dropKits('R', 2);
        break;

      //turn right
      case 'U': // 0 kits
        Serial3.println("U");
        RGB_color(255, 0, 255, 0, 'R'); // Magenta
        break;
      case 'y': // 1 kit
        Serial3.println("red/yellow");
        RGB_color(255, 0, 0, 1, 'L'); // Red
        //dropKits('L', 1);
        break;

      case 'g': // 0 kits
        Serial3.println("green");
        RGB_color(0, 255, 0, 0, 'L'); // Green
        break;

      case 'h': // 3 kits
        Serial3.println("H");
        RGB_color(0, 0, 255, 3, 'L'); // Blue
        //dropKits('L', 3);
        break;

      //turn left
      case 's': // 2 kits
        Serial3.println("S");
        RGB_color(0, 255, 255, 2, 'L'); // Cyan
        //dropKits('L', 2);
        break;

      //turn right
      case 'u': // 0 kits
        Serial3.println("U");
        RGB_color(255, 0, 255, 0, 'R'); // Magenta
        break;
        
      default:
        Serial3.print("hmmm wut is this: ");
        Serial3.println(incoming_byte);
        break;
    }
    }
  }
}

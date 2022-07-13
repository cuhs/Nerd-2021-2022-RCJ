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
  SERIAL3_BEGIN
  //Serial.begin(9600);
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

  SERIAL3_PRINTLN("--------------------STARTING NOW--------------------")
  setupSensors2();
  initIMU();
  delay(1000);
  SERIAL3_PRINTLN('a')
  Serial.begin(9600);
  Serial2.write('a');
  while(!Serial2.available());
  char c = Serial2.read();
  if(c=='y' || c=='a'){
    turnAbsNoVictim(90);
    if(getSensorReadings(RIGHT_TOF)<20)
      Serial2.write('1');
    else
      Serial2.write('0');
    turnAbsNoVictim(0);
  }
  sendWallValues(getSensorReadings(FRONT_TOF), getSensorReadings(RIGHT_TOF), getSensorReadings(LEFT_TOF));
}

void loop() {
  //wait for the StereoPi to send a Serial message with directions or victims
  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    SERIAL3_PRINT("Message detected: ")
    SERIAL3_PRINTLN(incoming_byte)
    //make sure that if a victim is detected, it is within 25 cm from the robot
    bool isLeftVictim = stringchr("yghsu", incoming_byte);
    bool isRightVictim = stringchr("YGHSU", incoming_byte);
    if (!isLeftVictim && !isRightVictim || isLeftVictim && getSensorReadings(LEFT_TOF) < 25 || isRightVictim && getSensorReadings(RIGHT_TOF) < 25) { //if letter is uppercase
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
        if(triangulation(getSensorReadings(LEFT_TOF), getSensorReadings(RIGHT_TOF))){
        alignFront();
        delay(1);
        Serial2.write(';');
        delay(1);
        SERIAL3_PRINTLN(';')
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
        SERIAL3_PRINTLN(';')
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
        SERIAL3_PRINTLN(';')        
        break;
        
      case '}'://pi wants wall values to be sent from the arduino
        SERIAL3_PRINTLN("}")
        if(finishedRamp==1){
          Serial2.write('u');
          Serial2.write((char)rampTilesWent+'0');
        }else if(finishedRamp==2){
          Serial2.write('d');
          Serial2.write((char)rampTilesWent+'0');
        }
        rampTilesWent = 0;
        finishedRamp=0;
        delay(15);
        sendWallValues(getSensorReadings(FRONT_TOF), getSensorReadings(RIGHT_TOF), getSensorReadings(LEFT_TOF));
        break;
      //victim messages
      case 'Y': // 1 kit
        SERIAL3_PRINTLN("red/yellow")
        RGB_color(255, 0, 0, 1, 'R'); // Red
        //dropKits('R', 1);
        break;

      case 'G': // 0 kits
        SERIAL3_PRINTLN("green")
        RGB_color(0, 255, 0, 0, 'R'); // Green
        break;

      case 'H': // 3 kits
        SERIAL3_PRINTLN("H")
        RGB_color(0, 0, 255, 3, 'R'); // Blue
        //dropKits('R', 3);
        break;

      //turn left
      case 'S': // 2 kits
        SERIAL3_PRINTLN("S")
        RGB_color(0, 255, 255, 2, 'R'); // Cyan
        //dropKits('R', 2);
        break;

      //turn right
      case 'U': // 0 kits
        SERIAL3_PRINTLN("U")
        RGB_color(255, 0, 255, 0, 'R'); // Magenta
        break;
      case 'y': // 1 kit
        SERIAL3_PRINTLN("red/yellow")
        RGB_color(255, 0, 0, 1, 'L'); // Red
        //dropKits('L', 1);
        break;

      case 'g': // 0 kits
        SERIAL3_PRINTLN("green")
        RGB_color(0, 255, 0, 0, 'L'); // Green
        break;

      case 'h': // 3 kits
        SERIAL3_PRINTLN("H")
        RGB_color(0, 0, 255, 3, 'L'); // Blue
        //dropKits('L', 3);
        break;

      //turn left
      case 's': // 2 kits
        SERIAL3_PRINTLN("S")
        RGB_color(0, 255, 255, 2, 'L'); // Cyan
        //dropKits('L', 2);
        break;

      //turn right
      case 'u': // 0 kits
        SERIAL3_PRINTLN("U")
        RGB_color(255, 0, 255, 0, 'L'); // Magenta
        break;
        
      default:
        SERIAL3_PRINT("hmmm wut is this: ")
        SERIAL3_PRINTLN(incoming_byte)
        break;
    }
    }
  }
}

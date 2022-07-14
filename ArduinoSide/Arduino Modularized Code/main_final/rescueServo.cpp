#include "rescueServo.h"

Servo myservo;
const int R_angle = 165;
const int L_angle = 5;
const int C_angle = 82;

//turns the servo motor on our rescue kit dropper to a certain angle
void turnTo(int dir) {
  myservo.attach(A7, 550, 2600);
  myservo.write(dir);
}

//wiggles to make sure the rescue kit goes in and comes out correctly - flashes the LED while wiggling
void wiggle(int angle, int wiggleAmt, int rVal, int gVal, int bVal) { //1200 ms
  //SERIAL3_PRINTLN("In wiggle");
  bool isOn = false;
  for (int i = 1; i < wiggleAmt; i++) {
    if(i%2==1){
      turnOnLED(isOn = !isOn, rVal, gVal, bVal);
    }
    myservo.write(angle - i);
    delay(100);
    myservo.write(angle + i);
    delay(100);
  }
  //SERIAL3_PRINTLN("Done wiggle");
}


//turns on or off the LED depending on if lightUp is true or false
void turnOnLED(bool lightUp, int rVal, int gVal, int bVal){
  if(lightUp){
    analogWrite(47, rVal);
  analogWrite(43, gVal);
  analogWrite(42, bVal);
  }
  else{
    analogWrite(47, 0);
    analogWrite(43, 0);
    analogWrite(42, 0);
  }  
}

//drops rescue kits while flashing the LED
void dropKits(char dir, int amt, int rVal, int gVal, int bVal) {
  myservo.attach(A7, 550, 2600); // attaches the servo on pin A7 to the servo object
  if (dir == 'L') {
    for (int i = 0; i < amt; i++) {
      wiggle(C_angle, 7, rVal, gVal, bVal); //1200ms
      myservo.write(C_angle); 
      delay(100);
      myservo.write(L_angle); 
      wiggle(L_angle, 7, rVal, gVal, bVal); //1200ms
      delay(500);
    }
  } else if (dir == 'R') {
    for (int i = 0; i < amt; i++) {
      wiggle(C_angle, 7, rVal, gVal, bVal); //1200ms
      myservo.write(C_angle);
      delay(100);
      myservo.write(R_angle);
      wiggle(R_angle, 7, rVal, gVal, bVal); //1200ms
      delay(500);
    }
  }
  myservo.write(C_angle);
  wiggle(C_angle, 9, rVal, gVal, bVal); //1200ms
  myservo.detach();
}

//main dropping kits and flashing LED controller - stops the bot, flashes LED after dropping kits for enough time to make it a total of 5 seconds
void RGB_color(int rVal, int gVal, int bVal, int rescueKits, char dir) {
  Serial.println("RGB_COLOR");
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  turnAbsNoVictim(getDirection(euler.x(),9));
  
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
  if (rescueKits == 0) {
    for (int i = 0; i < 5; i++) {
      turnOnLED(true,rVal,gVal,bVal);
      delay(550);
      turnOnLED(false,rVal,gVal,bVal);
      delay(550);
    }   
  }
  else if(rescueKits == 1){
    dropKits(dir,rescueKits,rVal, gVal, bVal);
    delay(525);
     turnOnLED(true,rVal,gVal,bVal);
      delay(525);
      turnOnLED(false,rVal,gVal,bVal);
  }
  else {
    dropKits(dir, rescueKits, rVal, gVal, bVal);
  }
  
  turnOnLED(false,rVal,gVal,bVal);
}

//detects if the StereoPi sends a message indicating a victim detected or if the heat sensors detect a victim
void victim() {
  Serial3.println("in victim");
  //detect heat victim
  if (!isHeat) {
    Serial3.println("testing for heat victim");
    doHeatVictim(getHeatSensorReadings('L'), getHeatSensorReadings('R'));
  }
  //wait for if the pi sends a message indicating a victim being detected
  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    SERIAL3_PRINT("Victim Message Received: ")
    SERIAL3_PRINTLN(incoming_byte)
    //makes sure the robot is close enough to a wall when a victim is detected
    //bool isLeftVictim = stringchr("yghsu", incoming_byte);
    //bool isRightVictim = stringchr("YGHSU", incoming_byte);
    //if (!isLeftVictim && !isRightVictim || isLeftVictim && getSensorReadings(LEFT_TOF) < 25 || isRightVictim && getSensorReadings(RIGHT_TOF) < 25) { //if letter is uppercase
      //drops kits and flashes LED if victim is detected
      switch (incoming_byte) {//put getSensorReadings in each case
        case 'Y': // 1 kit
          if(getSensorReadings(RIGHT_TOF) < 25){
            SERIAL3_PRINTLN("red/yellow")
            RGB_color(255, 0, 0, 1, 'R'); // Red
          }
          break;

        case 'G': // 0 kits
          if(getSensorReadings(RIGHT_TOF) < 25){
            SERIAL3_PRINTLN("green")
            RGB_color(0, 255, 0, 0, 'R'); // Green
          }
          break;

        case 'H': // 3 kits
          if(getSensorReadings(RIGHT_TOF) < 25){
            SERIAL3_PRINTLN("H")
            RGB_color(0, 0, 255, 3, 'R'); // Blue
          }
          break;

        //turn left
        case 'S': // 2 kits
          if(getSensorReadings(RIGHT_TOF) < 25){
            SERIAL3_PRINTLN("S")
            RGB_color(0, 255, 255, 2, 'R'); // Cyan
          }
          break;

        //turn right
        case 'U': // 0 kits
          if(getSensorReadings(RIGHT_TOF) < 25){
            SERIAL3_PRINTLN("U")
            RGB_color(255, 0, 255, 0, 'R'); // Magenta
          }
          break;
        case 'y': // 1 kit
          if(getSensorReadings(LEFT_TOF) < 25){
            SERIAL3_PRINTLN("red/yellow")
            RGB_color(255, 0, 0, 1, 'L'); // Red
          }
          break;

        case 'g': // 0 kits
          if(getSensorReadings(LEFT_TOF) < 25){
            SERIAL3_PRINTLN("green")
            RGB_color(0, 255, 0, 0, 'L'); // Green
          }
          break;

        case 'h': // 3 kits
          if(getSensorReadings(LEFT_TOF) < 25){
            SERIAL3_PRINTLN("H")
            RGB_color(0, 0, 255, 3, 'L'); // Blue
          }
          break;

        //turn left
        case 's': // 2 kits
          if(getSensorReadings(LEFT_TOF) < 25){
            SERIAL3_PRINTLN("S")
            RGB_color(0, 255, 255, 2, 'L'); // Cyan
          }
          break;

        //turn right
        case 'u': // 0 kits
        if(getSensorReadings(LEFT_TOF) < 25){
          SERIAL3_PRINTLN("U")
          RGB_color(255, 0, 255, 0, 'L'); // Magenta
         }
          break;
        case '}':
          SERIAL3_PRINTLN("}")
          if(finishedRamp==1)
            Serial2.write('u');
          else if(finishedRamp==2)
            Serial2.write('d');
          finishedRamp=0;
          delay(15);
          sendWallValues(getSensorReadings(FRONT_TOF), getSensorReadings(RIGHT_TOF), getSensorReadings(LEFT_TOF));
          break;
        default:
          SERIAL3_PRINT("#2 hmmm wut is this: ")
          SERIAL3_PRINTLN(incoming_byte)
          break;
      }
    
  }
}

//stringchr returns true if char c is in string s
bool stringchr(const char *s, char c){
  for(int i = 0; s[i] != '\0'; i++){
    if(s[i]==c) return true;
  }
  return false;
}

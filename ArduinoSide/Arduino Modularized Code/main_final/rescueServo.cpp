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
  //Serial3.println("In wiggle");
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
  //Serial3.println("Done wiggle");
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
  wiggle(C_angle, 5, rVal, gVal, bVal); //1200ms
  myservo.detach();
}

//main dropping kits and flashing LED controller - stops the bot, flashes LED after dropping kits for enough time to make it a total of 5 seconds
void RGB_color(int rVal, int gVal, int bVal, int rescueKits, char dir) {
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
  //detect heat victim
  if (!isHeat) {
    doHeatVictim(getHeatSensorReadings('L'), getHeatSensorReadings('R'));
  }
  //wait for if the pi sends a message indicating a victim being detected
  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    Serial3.print("Victim Message Received: ");
    Serial3.println(incoming_byte);
    //makes sure the robot is close enough to a wall when a victim is detected
    if (!stringchr("YGHSUyghsu", incoming_byte) || (stringchr("yghsu", incoming_byte) && getSensorReadings(1) < 25) || (stringchr("YGHSU", incoming_byte) && getSensorReadings(0) < 25)) { //if letter is uppercase
      //drops kits and flashes LED if victim is detected
      switch (incoming_byte) {
        case 'Y': // 1 kit
          Serial3.println("red/yellow");
          RGB_color(255, 0, 0, 1, 'R'); // Red
          break;

        case 'G': // 0 kits
          Serial3.println("green");
          RGB_color(0, 255, 0, 0, 'R'); // Green
          break;

        case 'H': // 3 kits
          Serial3.println("H");
          RGB_color(0, 0, 255, 3, 'R'); // Blue
          break;

        //turn left
        case 'S': // 2 kits
          Serial3.println("S");
          RGB_color(0, 255, 255, 2, 'R'); // Cyan
          break;

        //turn right
        case 'U': // 0 kits
          Serial3.println("U");
          RGB_color(255, 0, 255, 0, 'R'); // Magenta
          break;
        case 'y': // 1 kit
          Serial3.println("red/yellow");
          RGB_color(255, 0, 0, 1, 'L'); // Red
          break;

        case 'g': // 0 kits
          Serial3.println("green");
          RGB_color(0, 255, 0, 0, 'L'); // Green
          break;

        case 'h': // 3 kits
          Serial3.println("H");
          RGB_color(0, 0, 255, 3, 'L'); // Blue
          break;

        //turn left
        case 's': // 2 kits
          Serial3.println("S");
          RGB_color(0, 255, 255, 2, 'L'); // Cyan
          break;

        //turn right
        case 'u': // 0 kits
          Serial3.println("U");
          RGB_color(255, 0, 255, 0, 'R'); // Magenta
          break;
        case '}':
          Serial3.println("}");
          if(finishedRamp==1)
            Serial2.write('u');
          else if(finishedRamp==2)
            Serial2.write('d');
          finishedRamp=0;
          delay(15);
          sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
          break;
        default:
          Serial3.print("#2 hmmm wut is this: ");
          Serial3.println(incoming_byte);
      }
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

//unused alternate victim function
void victimForward(int percentage) {
  if (!isHeat) {
    doHeatVictim(getHeatSensorReadings('L'), getHeatSensorReadings('R'));
  }

  if (Serial2.available()) {
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    Serial3.print("Victim Message Received: ");
    Serial3.println(incoming_byte);
    
    if (!stringchr("YGHSUyghsu", incoming_byte) || (stringchr("yghsu", incoming_byte) && getSensorReadings(1) < 35) || (stringchr("YGHSU", incoming_byte) && getSensorReadings(0) < 35)) { //if letter is uppercase
      if(stringchr("YGHSU\0", incoming_byte)){
        int distRight = getSensorReadings(0); 
        Serial3.print("sending the pi pre-victim values: ");
        Serial3.print(distRight/10 + '0');
        Serial3.print(distRight%10 + '0');
        Serial3.print(percentage/10 + '0');
        Serial3.println(percentage%10 + '0');
        Serial2.write(distRight/10 + '0');
        Serial2.write(distRight%10 + '0');
        Serial2.write(percentage/10 + '0');
        Serial2.write(percentage%10 + '0');
      }else if(stringchr("yghsu\0", incoming_byte)){
        int distLeft = getSensorReadings(1);
        Serial3.print("sending the pi pre-victim values: ");
        Serial3.print(distLeft/10 + '0');
        Serial3.print(distLeft%10 + '0');
        Serial3.print(percentage/10 + '0');
        Serial3.println(percentage%10 + '0');
        Serial2.write(distLeft/10 + '0');
        Serial2.write(distLeft%10 + '0');
        Serial2.write(percentage/10 + '0');
        Serial2.write(percentage%10 + '0');
      }else{
        Serial3.print("incoming_byte: ");
        Serial3.print(incoming_byte);
      }
      switch (incoming_byte) {
        case 'Y': // 1 kit
          Serial3.println("red/yellow");
          while(!Serial2.available());
          if(Serial2.read()=='y')
            RGB_color(255, 0, 0, 1, 'R'); // Red
          //dropKits('R', 1);
          break;

        case 'G': // 0 kits
          Serial3.println("green");
          while(!Serial2.available());
          if(Serial2.read()=='y')
          RGB_color(0, 255, 0, 0, 'R'); // Green
          break;

        case 'H': // 3 kits
          Serial3.println("H");
          while(!Serial2.available());
          if(Serial2.read()=='y')
          RGB_color(0, 0, 255, 3, 'R'); // Blue
          //dropKits('R', 3);
          break;

        //turn left
        case 'S': // 2 kits
          Serial3.println("S");
          while(!Serial2.available());
          if(Serial2.read()=='y')
          RGB_color(0, 255, 255, 2, 'R'); // Cyan
          //dropKits('R', 2);
          break;

        //turn right
        case 'U': // 0 kits
          Serial3.println("U");
          while(!Serial2.available());
          if(Serial2.read()=='y')
          RGB_color(255, 0, 255, 0, 'R'); // Magenta
          break;
        case 'y': // 1 kit
          Serial3.println("red/yellow");
          while(!Serial2.available());
          if(Serial2.read()=='y')
          RGB_color(255, 0, 0, 1, 'L'); // Red
          //dropKits('L', 1);
          break;

        case 'g': // 0 kits
          Serial3.println("green");
          while(!Serial2.available());
          if(Serial2.read()=='y')
          RGB_color(0, 255, 0, 0, 'L'); // Green
          break;

        case 'h': // 3 kits
          Serial3.println("H");
          while(!Serial2.available());
          if(Serial2.read()=='y')
          RGB_color(0, 0, 255, 3, 'L'); // Blue
          //dropKits('L', 3);
          break;

        //turn left
        case 's': // 2 kits
          Serial3.println("S");
          while(!Serial2.available());
          if(Serial2.read()=='y')
          RGB_color(0, 255, 255, 2, 'L'); // Cyan
          //dropKits('L', 2);
          break;

        //turn right
        case 'u': // 0 kits
          Serial3.println("U");
          while(!Serial2.available());
          if(Serial2.read()=='y')
          RGB_color(255, 0, 255, 0, 'R'); // Magenta
          break;
        case '}':
          Serial3.println("}");
          if(finishedRamp==1)
            Serial2.write('u');
          else if(finishedRamp==2)
            Serial2.write('d');
          finishedRamp=0;
          delay(15);
          sendWallValues(getSensorReadings(2), getSensorReadings(0), getSensorReadings(1));
          break;
        default:
          Serial3.print("#2 hmmm wut is this: ");
          Serial3.println(incoming_byte);
      }
    }
  }
}

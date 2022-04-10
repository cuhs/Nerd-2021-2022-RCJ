#include "rescueServo.h"
Servo myservo;
bool shouldRun = true;
//midPos: 60
 bool stuckTest(int target) {
  int ang = myservo.read();
  //Serial.println(ang);
  if (!(ang > target - 1 && ang < target + 1)) {
    return true;
  }
  return false;

}

void setupServo(){
  myservo.attach(A8, 300, 2400); // attaches the servo on pin A8 to the servo object
  //myservo.attach(A6);
}
void wiggle(int target, int times) {

  for (int i = 1; i < times; i++) {
    myservo.write(target + i);
    delay(200);
    myservo.write(target - i);
    delay(200);
  }
  myservo.write(target);
  //}
  if (stuckTest(target)) {
    shouldRun = false;
  }
}

void servoTurnLeft() {
  myservo.write(0);

  delay(500);
  wiggle(0, 5);
}

void servoMidPos() {
  myservo.write(60);
  delay(500);
  wiggle(60, 5);
}


void servoTurnRight() {

  myservo.write(173);
  delay(500);
  //Serial.print(myservo.read());
  wiggle(173, 5);
}

void victim(){

if(Serial2.available()){
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);

    ports[RIGHT].setMotorSpeed(0);
    ports[LEFT].setMotorSpeed(0);
    
 switch (incoming_byte){
      case 'R': 
        Serial.println("red/yellow"); 
        break;
      case 'G': 
        Serial.println("green"); 
        break; 
      case 'H':
        Serial.println("H");
        break; 
        //turn left
      case 'S':
       Serial.println("S");
       break; 
       //turn right
      case 'U':
        Serial.println("U"); 
        break;
      default:
       Serial.println("hmmm wut is this");
    }
    }
}
    

#include "new_global_vars.h"
#include "Distance_Sensor.h"
#include "IMU.h"
//#include "TCA.h"
//#include "TCS.h"
#include "motors.h"
//#include "rescueServo.h"

  char values[5] = {'1','0','0','0','1'};
  //last 1;
  //N E S W --> South always 0


void setup() {
  delay(1);
  Serial.begin(9600);
  Serial2.begin(9600);
  //Wire.begin();
  //Serial2.write('a');
  //pinMode(A6, OUTPUT);
  //INIT_INTERRUPT_LEFT;
  //INIT_INTERRUPT_RIGHT;
  //ports[RIGHT].backwards = true;
  Serial.println("--------------------STARTING NOW--------------------");
  setupSensors();
  //myservo.attach(A8, 490, 2400); // attaches the servo on pin A8 to the servo object
  //midPos();
  Serial2.write('a');
  Serial2.write(values,3);


}



void loop() {


  if(Serial2.available()){
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    Serial.println("Message detected.");
    
    switch (incoming_byte){
      case '{': 
        Serial.println("{"); break;
      case 'F': 
        Serial.println("forward!"); 
        goForwardTiles(1);
        break; 
      case 'L':
        Serial.println("left!");
        turnLeft(90);
        break; 
        //turn left
      case 'R':
       Serial.println("right!"); 
       turnRight(90);
       break; 
       //turn right
      case ';':
        Serial.println(";"); 
        break;
      case '}': 
        Serial.println("}"); 
        Serial2.write(values,3);
        break;
        //sendwall values 
      default:
       Serial.println("hmmm wut is this");

    }
  }

}

#include "new_global_vars.h"
#include "Distance_Sensor.h"
#include "IMU.h"
#include "TCA.h"
#include "TCS.h"
#include "motors.h"
#include "rescueServo.h"
//#include "rescueServo.h"
// this is comment
  //last 1;
  //N E S W --> South always 0

void setup() {
  delay(100);
  Serial.begin(9600);
  Serial2.begin(9600);
  Wire.begin();
  setupServo();
  //Serial2.write('a');
  //pinMode(A6, OUTPUT);
  
  INIT_INTERRUPT_LEFT;
  INIT_INTERRUPT_RIGHT;
  ports[RIGHT].backwards = true;
  
  Serial.println("--------------------STARTING NOW--------------------");
  
  setupSensors2();
  initIMU();
  
  Serial2.write('a');
  //Serial.print(getSensorReadings(0) + " " + getSensorReadings(1) + " " + getSensorReadings(2)); 
  sendWallValues(getSensorReadings(2),getSensorReadings(0),getSensorReadings(1));



}



void loop() {

//  goForwardTilesPID(1);
//  delay(5000);
  
  
  if(Serial2.available()){
    delay(1);
    char incoming_byte = Serial2.read();
    delay(1);
    Serial.println("Message detected.");
    
    switch (incoming_byte){
      case '{': 
        Serial.println("{"); break;
      case 'F':
      Serial2.read(); 
        Serial.println("forward!"); 
        goForwardTilesPID(1);
        alignFront();
                Serial2          .write(';');

        break; 
      case 'L':
            Serial2.read(); 
        Serial.println("left!");
        //turnLeft(90);
        turnAbs('l');
                Serial2.write(';');

        break; 
        //turn left
      case 'R':
            Serial2.read(); 
       Serial.println("right!"); 
       //turnRight(90);
       turnAbs('r');
               Serial2.write(';');

       break; 
       //turn right
      case ';':
        Serial.println(";"); 
        Serial2.write(';');

        break;
      case '}': 
        Serial.println("}"); 
        sendWallValues(getSensorReadings(2),getSensorReadings(0),getSensorReadings(1));
        break;
        //sendwall values 
      default:
       Serial.println("hmmm wut is this");
    
    }
  }
  

}

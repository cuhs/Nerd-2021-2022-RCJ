#include "new_global_vars.h"
#include "Distance_Sensor.h"
#include "IMU.h"
#include "TCA.h"
#include "TCS.h"
#include "motors.h"
//#include "rescueServo.h"
// this is comment
  //last 1;
  //N E S W --> South always 0

void setup() {
  delay(100);
  Serial.begin(9600);
  Serial2.begin(9600);
  Wire.begin();
  
  //Serial2.write('a');
  //pinMode(A6, OUTPUT);
  
  INIT_INTERRUPT_LEFT;
  INIT_INTERRUPT_RIGHT;
  ports[RIGHT].backwards = true;
  
  Serial.println("--------------------STARTING NOW--------------------");
  
  setupSensors2();
  initIMU();
  
  //myservo.attach(A8, 490, 2400); // attaches the servo on pin A8 to the servo object
  //midPos();
  
  Serial2.write('a');
  //Serial.print(getSensorReadings(0) + " " + getSensorReadings(1) + " " + getSensorReadings(2)); 
  sendWallValues(getSensorReadings(0),getSensorReadings(1),getSensorReadings(2));



}



void loop() {

  /*for(int i = 0; i<254; i++){
     ports[RIGHT].setMotorSpeed(i);
     ports[LEFT].setMotorSpeed(i);
     Serial.println(i);
     delay(100);
  }*/
    //imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

    //euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  //Serial.println(euler.x());

  //turnLeftPID(90);
  //while(1){};
  
  //delay(1000);
  //turnLeft(90);
  //delay(1000);

  //goForwardTiles(1);
  //delay(5000);

  goForwardTilesPID(1);
  delay(5000);

  //goForwardTiles(1);
  //delay(10000);
  //ports[RIGHT].setMotorSpeed(220);
  //ports[LEFT].setMotorSpeed(-220);

    //triangulate(getSensorReadings(0),getSensorReadings(1));

    //turnAbs('r');
    //delay(2500);
    //turnAbs('l');
    //delay(2500);

  /*
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
        //goForwardTilesPID(1);
        //alignFront();
        delay(5000);
        break; 
      case 'L':
        Serial.println("left!");
        //turnLeft(90);
        delay(5000);
        break; 
        //turn left
      case 'R':
       Serial.println("right!"); 
       //turnRight(90);
       delay(5000);
       break; 
       //turn right
      case ';':
        Serial.println(";"); 
        Serial2.write(';');

        break;
      case '}': 
        Serial.println("}"); 
        //sendWallValues(getSensorReadings(0),getSensorReadings(1),getSensorReadings(2));
        break;
        //sendwall values 
      default:
       Serial.println("hmmm wut is this");
    
    }
  }*/

}

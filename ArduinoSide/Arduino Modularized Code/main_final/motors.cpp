#include "motors.h"

char message[4] = {'a', 'a', 'a', 'a'};
MegaPiPort ports[] = { {PORT1B, 18, 31}, {PORT2B, 19, 38}, {PORT3B, 3, 49}, {PORT4B, 2, A1}};

//goes forward a certain amount of tiles
bool goForwardTilesPID(int tiles) {
  return goForwardPID(tiles * 30);
}

//moving forward function for if the robot is on a ramp or stairs - 'u' for up, 'd' for down
int rampMoveForward(char dir) {
  SERIAL3_PRINTLN("in rampMoveForward")
  int motorSpeed = 0;
  int motorEncUse = LEFT;
  //sets motorSpeed and finishedRamp based on if it is down or up
  if (dir == 'u') {
    motorSpeed = 150;
    finishedRamp = 1;
  } else if (dir == 'd') {
    motorSpeed = 90;
    finishedRamp = 2;
  }

  //variables used to calculated distance travelled
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  turnAbsNoVictim(getDirection(euler.x()));
  int startingEnc = ports[motorEncUse].count;
  int avgAng = 0;
  int itCt = 0;

  //moves forward until the robot is on a ramp - used when the StereoPi tells the Arduino there is a ramp ahead
  while (isOnRamp() == 0 && getSensorReadings(FRONT_TOF) > 5) {
      ports[LEFT].setMotorSpeed(motorSpeed);
      ports[RIGHT].setMotorSpeed(motorSpeed);
    if(Serial2.available()) Serial2.read();
  }

  //moves forward until the robot is not on the ramp
  euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int target = getDirection(euler.x());
  while (notStable() && getSensorReadings(FRONT_TOF) > 5) {
    ports[LEFT].setMotorSpeed(motorSpeed);
    ports[RIGHT].setMotorSpeed(motorSpeed);
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    //increments avgAng and itCt in order to later calculate average angle
    int ca = euler.y();
    if(abs(ca)>15){
      avgAng += ca;
      ++itCt;
    }

    //if any victims are detected, get rid of them because there shouldn't be victims on a ramp
    if(Serial2.available()) Serial2.read();
  }

  //calculate cm travelled on the ramp
  int amountTravelled = ((ports[motorEncUse].count-startingEnc)*D*PI)/360;
  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
  //calculate average angled
  avgAng = avgAng/itCt;
  //calculate horizontal distance in cm travelled
  amountTravelled = amountTravelled*cos((abs(avgAng)*PI)/180);
  amountTravelled += alignFront(true);
  return amountTravelled;
}

//goes forward without PID and without doing anything else(like victim)
void plainGoForward(int dist, int motorSpeed){
  int motorEncUse = LEFT;
  int initEnc = ports[motorEncUse].count;
  double enc = ((360 / (D * PI)) * dist) + initEnc;
  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(FRONT_TOF) > 5)) {
    ports[RIGHT].setMotorSpeed(motorSpeed);
    ports[LEFT].setMotorSpeed(motorSpeed);
    int ramp = isOnRamp();
    if(ramp==1)
      rampMoveForward('u');
    else if(ramp==2)
      rampMoveForward('d');
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

//moves backwards
void moveBackwards(int initEnc){
  //variables used for stall detection
  unsigned long startTime;
  unsigned long endTime;
  int prev_count = 0;
  bool stalling = false;
  bool checking = false;
  while(ports[LEFT].count > initEnc && !stalling){
    ports[LEFT].setMotorSpeed(-100);
    ports[RIGHT].setMotorSpeed(-100);
     //stall detection
    if (ports[LEFT].count == prev_count && !checking) {
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
      checking = false;
      startTime = millis();
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      endTime = millis();
      if (endTime - startTime > 1000) {
        SERIAL3_PRINTLN("STALLING")
        stalling = true;
      }
    }
    prev_count = ports[LEFT].count;
  }
  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
}

bool goForwardPID(int dist) {
  //variables used for stall detection
  unsigned long startTime;
  unsigned long endTime;
  int prev_count = 0;
  bool stalling = false;
  bool checking = false;
  
  bool shouldSendM = true;
  int curEnc = 0;

  int tileSize = 30; // Set to 30
  int motorEncUse = LEFT;
  //variables used for PID
  double pastError = 0;
  double integral = 0;
  int fix = 0;
  bool whatToReturn = true;
  int whatTile = 0;
  int angIncrease = 0;

  //used to determine if a silver tile is detected and differentiate between false identifications
  bool seesSilver = false;
  bool isSilver = false;
  int silvCt = 0;
  int totCt = 0;

  ports[motorEncUse].count = 0;

  //calculate amount of encoders needed to move forward
  double enc = ((360 / (D * PI)) * dist);
  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(FRONT_TOF) > 5) && !stalling) {
    //tests for victims
    victim();
    //sees if the robot is on a ramp
    int onRamp = isOnRamp();
    if (onRamp == 1) {
      int beforeEnc = (ports[motorEncUse].count*D*PI)/360;
      int amtOfRamp = rampMoveForward('u');
      //if the horizontal distance travelled is less than 40, we determine that the robot went on stairs and not a ramp - we make it go forward until it goes down the stairs and then sends how many tiles it went
      if(amtOfRamp<65 && amtOfRamp >5){
        //amtOfRamp += rampMoveForward('d');
        if(amtOfRamp%30>=15)
          amtOfRamp+=30;
        //if(shouldSendM)
        amtOfRamp += beforeEnc;
        delay(1);
        //tells pi that there was stairs, sends tiles travelled on stairs
        SERIAL3_PRINT("Stairs ")
        SERIAL3_PRINTLN(amtOfRamp/30);
        Serial2.write('s');
        if(amtOfRamp/30 > 0) amtOfRamp -= 30;
        Serial2.write((char)(amtOfRamp/30)+'0');

        //no ramp
        finishedRamp = 0;
        if(amtOfRamp/30==0) continue;
        return true;
      }else if(amtOfRamp <= 5){
        finishedRamp = 0;
      }else{
        SERIAL3_PRINT("ramp")
        return true;
      }
    } else if (onRamp == 2) {
      //see above comments for onRamp == 1(going down instead of going up)
      int beforeEnc = (D*PI*ports[motorEncUse].count)/360;
      int amtOfRamp = rampMoveForward('d');
      if(amtOfRamp<65 && amtOfRamp > 5){
        delay(1);
        Serial2.write('s');
        if(amtOfRamp%30>=15)
          amtOfRamp+=30;
        //if(shouldSendM)
        amtOfRamp += beforeEnc;
        if(amtOfRamp/30 >0) amtOfRamp -=30;
        Serial2.write((char)(amtOfRamp/30)+'0');
        SERIAL3_PRINT("stairs ")
        SERIAL3_PRINTLN(amtOfRamp/30);
        finishedRamp = 0;
        if(amtOfRamp/30==0) continue;
        return true;
      }else if(amtOfRamp <= 5){
        finishedRamp = 0;
      }else{
        SERIAL3_PRINTLN("ramp");
        return true;
      }
    }
    whatTile = 0;
    bool onSB = isOnSpeedBump();
    if(onSB){ 
      angIncrease = 150;
      SERIAL3_PRINTLN("Speed increase on SB");
    }
    whatTile = detectTiles();
    if (whatTile == 1 && !checking) {
      //detected black - sends m if no m was sent yet, then semicolon and 'b'
      if(shouldSendM){
        Serial2.write('m');
      }
      Serial2.write(';');
      Serial2.write('b');
      moveBackwards(0);
      delay(1);
      Serial2.read();
      delay(1);
      return false;
    }else if(whatTile==2 && !onSB && abs(ports[motorEncUse].count)>=(5*enc)/10 && !checking){
      //checks to make sure seeing silver is not a misdetection - turns 25 degrees to the right and to the left, if at least one more of those situations detect silver, it is a silver tile
//      seesSilver = true;
//      tcaselect(7);
//      imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
//      int theCurrAngle = getDirection(euler.x());
//      int silvCheck = 0;
//      int initialCt = ports[motorEncUse].count;
//      turnAbsNoVictim((theCurrAngle + 30)%360);
//      silvCheck += detectTiles();
//      turnAbsNoVictim((theCurrAngle + 330)%360);
//      silvCheck += detectTiles();
//      
//      if(silvCheck >= 2){
//        isSilver = true;
//        whatToReturn = false;
//        shouldSendM=false;
//        turnAbsNoVictim(theCurrAngle);
//      }       
        silvCt++;
    }
    if(abs(ports[motorEncUse].count)>=(5*enc)/10 && !checking && !onSB)
      totCt++;
    //sends m if it hasn't yet and if the robot is 50% done with going forward
    if(shouldSendM && abs(ports[motorEncUse].count)>=(5*enc)/10){
      SERIAL3_PRINTLN("Sending m")
      shouldSendM = false;
      delay(1);
      Serial2.write('m');
      delay(1);
    }
    //detects obstacle and turns accordingly
    char c = obstacleDetect();
    if(c=='l'){
      curEnc = ports[motorEncUse].count;
      while(obstacleDetect()!='0'){
        ports[LEFT].setMotorSpeed(120);
        ports[RIGHT].setMotorSpeed(-140);
      }
      ports[motorEncUse].count = curEnc;
    }else if(c=='r'){
      curEnc = ports[motorEncUse].count;
      while(obstacleDetect()!='0'){
        ports[LEFT].setMotorSpeed(-140);
        ports[RIGHT].setMotorSpeed(120);
      }
      ports[motorEncUse].count = curEnc;
    }
    //stall detection
    if (ports[LEFT].count == prev_count && !checking) {
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
      checking = false;
      startTime = millis();
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      endTime = millis();
      if (endTime - startTime > 1000) {
        SERIAL3_PRINTLN("STALLING")
        stalling = true;
      }else if(endTime - startTime > 500){
        angIncrease = 150;
        SERIAL3_PRINTLN("Speed up stall");
        SERIAL3_PRINTLN("Stall increase speed")
      }
    }
    prev_count = ports[LEFT].count;
    
    fix = (int)(PID(enc - abs(ports[motorEncUse].count), pastError, integral, 0.2, 0.005, 0));
    //speeds up more if the robot is on a speed bump
    ports[RIGHT].setMotorSpeed(fix + 30 + angIncrease);
    ports[LEFT].setMotorSpeed(fix + 30 + angIncrease);
    angIncrease = 0;

  }
  //sends messages to the StereoPi if a silver tile was detected
  if((double)(silvCt)/totCt>0.4){
    isSilver = true;
    whatToReturn = false;
  }else{
    isSilver = false;
    whatToReturn = true;
  }
  delay(10);
  if(isSilver){
    SERIAL3_PRINT("sending t")
    Serial2.write(';');
    Serial2.write('t');
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
  return whatToReturn;
}

void motorinterruptleft() {
  if (ports[LEFT].backwards)
    (digitalRead(ports[LEFT].encPin)) ? ports[LEFT].count++ : ports[LEFT].count--;
  else
    (digitalRead(ports[LEFT].encPin)) ? ports[LEFT].count-- : ports[LEFT].count++;
}

void motorinterruptright() {
  if (ports[RIGHT].backwards)
    (digitalRead(ports[RIGHT].encPin)) ? ports[RIGHT].count++ : ports[RIGHT].count--;
  else
    (digitalRead(ports[RIGHT].encPin)) ? ports[RIGHT].count-- : ports[RIGHT].count++;
}

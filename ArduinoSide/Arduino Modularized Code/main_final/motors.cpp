#include "motors.h"

char message[4] = {'a', 'a', 'a', 'a'};
MegaPiPort ports[] = { {PORT1B, 18, 31}, {PORT2B, 19, 38}, {PORT3B, 3, 49}, {PORT4B, 2, A1}};

//goes forward a certain amount of tiles
bool goForwardTilesPID(int tiles) {
  return goForwardPID(tiles * 30);
}

//moving forward function for if the robot is on a ramp or stairs - 'u' for up, 'd' for down
int rampMoveForward(char dir) {
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
  int startingEnc = ports[motorEncUse].count;
  int avgAng = 0;
  int itCt = 0;

  //moves forward until the robot is on a ramp - used when the StereoPi tells the Arduino there is a ramp ahead
  while (isOnRamp() == 0) {
      ports[LEFT].setMotorSpeed(motorSpeed);
      ports[RIGHT].setMotorSpeed(motorSpeed);
    if(Serial2.available()) Serial2.read();
  }

  //moves forward until the robot is not on the ramp
  while (notStable()) {
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
  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(2) > 5)) {
    ports[RIGHT].setMotorSpeed(motorSpeed);
    ports[LEFT].setMotorSpeed(motorSpeed);
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
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

  //used to determine if a silver tile is detected and differentiate between false identifications
  bool seesSilver = false;
  bool isSilver = false;

  ports[motorEncUse].count = 0;

  //calculate amount of encoders needed to move forward
  double enc = ((360 / (D * PI)) * dist);
  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(2) > 5) && !stalling) {
    //tests for victims
    victim();
    //sees if the robot is on a ramp
    int onRamp = isOnRamp();
    if (onRamp == 1) {
      int amtOfRamp = rampMoveForward('u');
      int beforeEnc = (ports[motorEncUse].count*D*PI)/360;
      //if the horizontal distance travelled is less than 40, we determine that the robot went on stairs and not a ramp - we make it go forward until it goes down the stairs and then sends how many tiles it went
      if(amtOfRamp<40){
        amtOfRamp += rampMoveForward('d');
        if(amtOfRamp%30>=10)
          amtOfRamp+=30;
        amtOfRamp += beforeEnc;
        delay(1);
        //tells pi that there was stairs, sends tiles travelled on stairs
        Serial2.write('s');
        Serial2.write((char)(amtOfRamp/30)+'0');

        //no ramp
        finishedRamp = 0;
      }
      return true;
    } else if (onRamp == 2) {
      //see above comments for onRamp == 1(going down instead of going up)
      int beforeEnc = (D*PI*ports[motorEncUse].count)/360;
      int amtOfRamp = rampMoveForward('d');
      if(amtOfRamp<40){
        delay(1);
        Serial2.write('s');
        if(amtOfRamp%30>=15)
          amtOfRamp+=30;
        amtOfRamp += beforeEnc;
        Serial2.write((char)(amtOfRamp/30)+'0');
        
        finishedRamp = 0;
      }
      return true;
    }

    //detects if there is a black or silver tile, but only if whatToReturn is true(indicates that no black or silver tile has been detected yet)
    if(whatToReturn)
      whatTile = detectTiles();
    if (whatTile == 1) {
      //detected black - sends m if no m was sent yet, then semicolon and 'b'
      if(shouldSendM){
        Serial2.write('m');
      }
      Serial2.write(';');
      Serial2.write('b');
      while (ports[motorEncUse].count > 0) {
        ports[RIGHT].setMotorSpeed(-80);
        ports[LEFT].setMotorSpeed(-80);
      }
      ports[RIGHT].setMotorSpeed(0);
      ports[LEFT].setMotorSpeed(0);
      delay(1);
      Serial2.read();
      delay(1);
      return false;
    }else if(!seesSilver && whatTile==2 && whatToReturn && abs(ports[motorEncUse].count)>=(6*enc)/10){// speed bump - turns slightly to make sure it is silver and not speed bump
      //checks to make sure seeing silver is not a misdetection - turns 25 degrees to the right and to the left, if at least one more of those situations detect silver, it is a silver tile
      seesSilver = true;
      tcaselect(7);
      imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
      int theCurrAngle = euler.x();
      int silvCheck = 0;
      turnAbsNoVictim((theCurrAngle + 25)%360);
      silvCheck += detectTiles();
      turnAbsNoVictim((theCurrAngle + 335)%360);
      silvCheck += detectTiles();
      
      if(silvCheck >= 2){
        isSilver = true;
        whatToReturn = false;
        shouldSendM=false;
        turnAbsNoVictim(theCurrAngle);
      }else{
        //if it was a false silver detection, we determine that the robot was probably on a speed bump, so we back up and speed up in order to go through it
        turnAbsNoVictim(theCurrAngle);
        while (ports[motorEncUse].count > 0) {
          ports[RIGHT].setMotorSpeed(-80);
          ports[LEFT].setMotorSpeed(-80);
        }
        ports[RIGHT].setMotorSpeed(0);
        ports[LEFT].setMotorSpeed(0);
        plainGoForward(28, 200);
      }
      
    }
    //sends m if it hasn't yet and if the robot is 50% done with going forward
    if(shouldSendM && abs(ports[motorEncUse].count)>=(5*enc)/10){
      Serial3.println("Sending m");
      shouldSendM = false;
      delay(1);
      Serial2.write('m');
      delay(1);
    }
    //detects obstacle and turns accordingly
    char c = obstacleDetect();
    if(c=='l'){
      curEnc = ports[motorEncUse].count;
      while(obstacleDetect()=='l'){
        ports[LEFT].setMotorSpeed(120);
        ports[RIGHT].setMotorSpeed(-140);
      }
      ports[motorEncUse].count = curEnc;
    }else if(c=='r'){
      curEnc = ports[motorEncUse].count;
      while(obstacleDetect()=='r'){
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
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      endTime = millis();
      if (endTime - startTime > 1000) {
        Serial3.println("STALLING");
        stalling = true;
      }
    }
    prev_count = ports[LEFT].count;
    
    fix = (int)(PID(enc - abs(ports[motorEncUse].count), pastError, integral, 0.25, 0.005, 0));
    //speeds up more if the robot is on a speed bump
    int angIncrease = 0;
    if(isOnSpeedBump())
      angIncrease = 40;

    ports[RIGHT].setMotorSpeed(fix + 30 + angIncrease);
    ports[LEFT].setMotorSpeed(fix + 30 + angIncrease);

  }
  //sends messages to the StereoPi if a silver tile was detected
  delay(10);
  if(isSilver){
    Serial3.print("sending t");
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

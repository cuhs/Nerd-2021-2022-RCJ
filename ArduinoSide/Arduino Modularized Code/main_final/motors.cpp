#include "motors.h"

char message[4] = {'a', 'a', 'a', 'a'};
MegaPiPort ports[] = { {PORT1B, 18, 31}, {PORT2B, 19, 38}, {PORT3B, 3, 49}, {PORT4B, 2, A1}};

bool goForwardTilesPID(int tiles) {
  return goForwardPID(tiles * 30);
}

int rampMoveForward(char dir) {
//  int Lspeed = 0;
//  int KP = 2;
//  int Rspeed = 0;
  int motorSpeed = 0;
  //int theAng = 0;
  int motorEncUse = LEFT;
  if (dir == 'u') {
    motorSpeed = 140;
    finishedRamp = 1;
  } else if (dir == 'd') {
    motorSpeed = 90;
    finishedRamp = 2;
  }
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
//  int angle = euler.x();
//  angle=getDirection(angle);
//  double error;
//  double pastError=0;
//  double integral=0;
  //int currAng;
  int startingEnc = ports[motorEncUse].count;
  int avgAng = 0;
  int itCt = 0;
  while (isOnRamp() == 0) {
//    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
//    currAng=euler.x();
//    if(currAng>345)
//      currAng=currAng-360;
//    error = angle - currAng;
//    int fix = PID(error, pastError, integral, KP, 0, 0);
//    int obsFix = 0;
//    char c = obstacleDetect();
    //if(c=='r' || c == 'l') obsFix = 50;
//    if(fix>0){
//      
//      ports[LEFT].setMotorSpeed(Lspeed+fix);
////      if(c=='l')
////        ports[RIGHT].setMotorSpeed(-120);
////      else if(c=='r')
////        ports[LEFT].setMotorSpeed(-120);
//    //  else{
//        ports[RIGHT].setMotorSpeed(Rspeed-fix);
//      //}
//    }
//    else{
//      ports[RIGHT].setMotorSpeed(Rspeed+fix);
////      if(c=='r')
////        ports[LEFT].setMotorSpeed(-120);
////      else if(c=='l')
////        ports[RIGHT].setMotorSpeed(-120);
//     // else{
//        ports[LEFT].setMotorSpeed(Lspeed-fix);
//      //}
//    }
      ports[LEFT].setMotorSpeed(motorSpeed);
      ports[RIGHT].setMotorSpeed(motorSpeed);
    if(Serial2.available()) Serial2.read();
//    Serial3.print("target: ");
//    Serial3.print(angle);
//    Serial3.print(" error: ");
//    Serial3.print(error);
//    Serial3.print(" curr ang: ");
//    Serial3.print(currAng);
//    Serial3.print(" fix: ");
//    Serial3.println(fix);
  }
  
  while (notStable()) {
//    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
//    currAng=euler.x();
//    if(currAng>345)
//      currAng=currAng-360;
//    error = angle - currAng;
//    int fix = PID(error, pastError, integral, KP, 0, 0);
//    if(fix>0){
//      ports[RIGHT].setMotorSpeed(Rspeed-fix);
//      ports[LEFT].setMotorSpeed(Lspeed+fix);
//    }
//    else{
//      ports[LEFT].setMotorSpeed(Lspeed-fix);
//      ports[RIGHT].setMotorSpeed(Rspeed+fix);
//    }
    ports[LEFT].setMotorSpeed(motorSpeed);
    ports[RIGHT].setMotorSpeed(motorSpeed);
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    int ca = euler.y();
    if(abs(ca)>15){
      avgAng += ca;
      ++itCt;
    }
    if(Serial2.available()) Serial2.read();
//    Serial3.print("target: ");
//    Serial3.print(angle);
//    Serial3.print(" error: ");
//    Serial3.print(error);
//    Serial3.print(" curr ang: ");
//    Serial3.print(currAng);
//    Serial3.print(" fix: ");
//    Serial3.println(fix);
  }
  int amountTravelled = ((ports[motorEncUse].count-startingEnc)*D*PI)/360;
  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
  avgAng = avgAng/itCt;
//  //plainGoForward(5);
//  Serial3.print("Angle: ");
//  Serial3.print(avgAng);
//  Serial3.print(" amttravelled: ");
//  Serial3.println(amountTravelled*cos((abs(avgAng)*PI)/180));
  alignFront();
  
  return amountTravelled*cos((abs(avgAng)*PI)/180);
}

void plainGoForward(int dist){
  int motorEncUse = LEFT;
  ports[motorEncUse].count = 0;
  double enc = ((360 / (D * PI)) * dist);
  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(2) > 5)) {
    ports[RIGHT].setMotorSpeed(100);
    ports[LEFT].setMotorSpeed(100);
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

bool goForwardPID(int dist) {
  unsigned long startTime;
  unsigned long endTime;

  int prev_count = 0;
  bool stalling = false;
  bool checking = false;
  bool shouldSendM = true;
  int curEnc = 0;

  int tileSize = 30; // Set to 30
  int motorEncUse = LEFT;

  double pastError = 0;
  double integral = 0;
  int fix = 0;
  bool whatToReturn = true;
  int whatTile = 0;
  bool seesSilver = false;
  bool isSilver = false;

  ports[motorEncUse].count = 0;

  double enc = ((360 / (D * PI)) * dist);
  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(2) > 5) && !stalling) {
    victim();
    int onRamp = isOnRamp();
    if (onRamp == 1) {
      //      //Serial2.write('u');
      //      while (notStable()) {
      //        ports[RIGHT].setMotorSpeed(210);
      //        ports[LEFT].setMotorSpeed(210);
      //      }
      //      ports[RIGHT].setMotorSpeed(0);
      //      ports[LEFT].setMotorSpeed(0);
      //      finishedRamp=1;
      int amtOfRamp = rampMoveForward('u');
      int beforeEnc = (ports[motorEncUse].count*D*PI)/360;
//      Serial3.print("AmtOfRamp pre down: ");
//      Serial3.println(amtOfRamp);
      if(amtOfRamp<40){
        amtOfRamp += rampMoveForward('d');
        if(amtOfRamp%30>=15)
          amtOfRamp+=30;
        amtOfRamp += beforeEnc;
        delay(1);
        Serial2.write('s');
//        Serial3.print(" (amtOfRamp/30)+'0': ");
//        Serial3.print((amtOfRamp/30)+'0');
//        Serial3.print(" (char)(amtOfRamp/30)+'0': ");
//        Serial3.print((char)(amtOfRamp/30)+'0');
//        Serial3.print(" amtOfRamp: ");
//        Serial3.println(amtOfRamp);
        Serial2.write((char)(amtOfRamp/30)+'0');
        plainGoForward(5);
        alignFront();
        finishedRamp = 0;
      }
      return true;
    } else if (onRamp == 2) {
      //Serial2.write('d');
      //      while(notStable()){
      //        ports[RIGHT].setMotorSpeed(150);
      //        ports[LEFT].setMotorSpeed(150);
      //      }
      //       ports[RIGHT].setMotorSpeed(0);
      //       ports[LEFT].setMotorSpeed(0);
      //       finishedRamp=2;
      int beforeEnc = (D*PI*ports[motorEncUse].count)/360;
      int amtOfRamp = rampMoveForward('u');
      if(amtOfRamp<40){
        delay(1);
        Serial2.write('s');
        if(amtOfRamp%30>=15)
          amtOfRamp+=30;
        amtOfRamp += beforeEnc;
//        Serial3.print(" (amtOfRamp/30)+'0': ");
//        Serial3.print((amtOfRamp/30)+'0');
//        Serial3.print(" (char)(amtOfRamp/30)+'0': ");
//        Serial3.println((char)(amtOfRamp/30)+'0');
//        Serial2.write((char)(amtOfRamp/30)+'0');
        Serial2.write((char)(amtOfRamp/30)+'0');
        plainGoForward(5);
        alignFront();
        
        finishedRamp = 0;
      }
      return true;
    }
    if(whatToReturn)
      whatTile = detectTiles();
    if (whatTile == 1) {
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
//      Serial3.print("in whatTile==2 ");
//      Serial3.println((int)whatToReturn);
      seesSilver = true;
      tcaselect(7);
      imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
      int theCurrAngle = euler.x();
      turnAbsNoVictim((theCurrAngle + 30)%360);
      if(detectTiles() == 2){
        isSilver = true;
        whatToReturn = false;
        shouldSendM=false;
      }
      turnAbsNoVictim(theCurrAngle);
    }
//    Serial3.print("whatToReturn: ");
//    Serial3.println((int)whatToReturn);
    if(shouldSendM && abs(ports[motorEncUse].count)>=(5*enc)/10){
      Serial3.println("Sending m");
      shouldSendM = false;
      delay(1);
      Serial2.write('m');
      delay(1);
    }
    char c = obstacleDetect();
//    Serial3.print("obstacleDetect: ");
//    Serial3.println(c);
    if(c=='l'){
      curEnc = ports[motorEncUse].count;
//      tcaselect(7);
//      imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
//      int dir = getDirection(euler.x());
      while(obstacleDetect()=='l'){
        ports[LEFT].setMotorSpeed(120);
        ports[RIGHT].setMotorSpeed(-140);
      }
//      if(dir!=-1) turnAbsNoVictim(dir);
      ports[motorEncUse].count = curEnc;
    }else if(c=='r'){
      curEnc = ports[motorEncUse].count;
//      tcaselect(7);
//      imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
//      int dir = getDirection(euler.x());
      while(obstacleDetect()=='r'){
        ports[LEFT].setMotorSpeed(-140);
        ports[RIGHT].setMotorSpeed(120);
      }
//      if(dir!=-1) turnAbsNoVictim(dir);
      ports[motorEncUse].count = curEnc;
    }
    if (ports[LEFT].count == prev_count && !checking) {
//      Serial3.println("set start time");
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
//      Serial3.println("checking false");
      checking = false;
    }
    if (ports[LEFT].count == prev_count && !stalling) {
//      Serial3.println("motors might be stalling");
      endTime = millis();
      if (endTime - startTime > 1000) {
        Serial3.println("STALLING");
        stalling = true;
      }
    }
    prev_count = ports[LEFT].count;
    //Serial3.print(enc);
    //Serial3.print(' ');
    //Serial3.print(getSensorReadings(2));
    //Serial3.print(' ');
    //Serial3.println(abs(ports[motorEncUse].count));

    
    fix = (int)(PID(enc - abs(ports[motorEncUse].count), pastError, integral, 0.25, 0.005, 0));
    int angIncrease = 0;
    if(isOnSpeedBump())
      angIncrease = 40;
    //Serial3.println(fix);

    ports[RIGHT].setMotorSpeed(fix + 30 + angIncrease);
    ports[LEFT].setMotorSpeed(fix + 30 + angIncrease);

  }
  //Serial3.println("Finished going forward(in motors)");
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

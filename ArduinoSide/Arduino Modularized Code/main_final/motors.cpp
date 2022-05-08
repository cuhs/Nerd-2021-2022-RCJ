#include "motors.h"

char message[4] = {'a', 'a', 'a', 'a'};
MegaPiPort ports[] = { {PORT1B, 18, 31}, {PORT2B, 19, 38}, {PORT3B, 3, 49}, {PORT4B, 2, A1}};

bool goForwardTilesPID(int tiles) {
  return goForwardPID(tiles * 30);
  //  Serial.println("in goForwardTilesPID");
  //  int tileSize = 30; // Set to 30
  //  int motorEncUse = LEFT;
  //
  //  double pastError = 0;
  //  double integral = 0;
  //  int fix = 0;
  //
  //  ports[motorEncUse].count = 0;
  //  double enc = ((360 / (D * PI)) * tileSize * tiles);
  //  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(2) > 5)) {
  //    victim();
  //
  //    if (detectBlack()) {
  //      Serial.println("SAW BLACK");
  //      while (ports[motorEncUse].count > 0) {
  //        ports[RIGHT].setMotorSpeed(-80);
  //        ports[LEFT].setMotorSpeed(-80);
  //      }
  //      //Serial2.write('b');
  //      ports[RIGHT].setMotorSpeed(0);
  //      ports[LEFT].setMotorSpeed(0);
  //      return false;
  //    }
  //
  //    fix = (int)(PID(enc - abs(ports[motorEncUse].count), pastError, integral, 0.362, 0.005, 1));
  //    //Serial.println(fix);
  //
  //    ports[RIGHT].setMotorSpeed(fix + 40);
  //    ports[LEFT].setMotorSpeed(fix + 40);
  //
  //  }
  //  ports[RIGHT].setMotorSpeed(0);
  //  ports[LEFT].setMotorSpeed(0);
  //  return true;
}

bool rampMoveForward(char dir){
  int Lspeed = 0;
  int Rspeed = 0;
  if(dir=='u'){
    Lspeed=210;
    Rspeed=210;
    finishedRamp=1;
  }else if(dir=='d'){
    Lspeed=150;
    Rspeed=150;
    finishedRamp=2;
  }
  while(notStable()){
    ports[LEFT].setMotorSpeed(Lspeed);
    ports[RIGHT].setMotorSpeed(Rspeed);
    if(getSensorReadings(0)>getSensorReadings(1)){
      Lspeed++;
      Rspeed--;
    }else{
      Rspeed++;
      Lspeed--;
    }
  }
  ports[LEFT].setMotorSpeed(0);
  ports[RIGHT].setMotorSpeed(0);
  return true;
  
}

bool goForwardPID(int dist) {
  unsigned long startTime;
  unsigned long endTime;

  int prev_count = 0;
  bool stalling = false;
  bool checking = false;

  int tileSize = 30; // Set to 30
  int motorEncUse = LEFT;

  double pastError = 0;
  double integral = 0;
  int fix = 0;

  ports[motorEncUse].count = 0;

  double enc = ((360 / (D * PI)) * dist);

  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(2) > 5) && !stalling) {
    Serial.println("In go forward PID");
    victim();
    int onRamp = isOnRamp();
    if (onRamp==1) {
//      //Serial2.write('u');
//      while (notStable()) {
//        ports[RIGHT].setMotorSpeed(210);
//        ports[LEFT].setMotorSpeed(210);
//      }
//      ports[RIGHT].setMotorSpeed(0);
//      ports[LEFT].setMotorSpeed(0);
//      finishedRamp=1;
      rampMoveForward('u');
      return true;
    }else if(onRamp==2){
      //Serial2.write('d');
//      while(notStable()){
//        ports[RIGHT].setMotorSpeed(150);
//        ports[LEFT].setMotorSpeed(150);
//      }
//       ports[RIGHT].setMotorSpeed(0);
//       ports[LEFT].setMotorSpeed(0);
//       finishedRamp=2;
       rampMoveForward('d');
       return true;
    }
    if (detectBlack()) {
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
    }
    if (ports[LEFT].count == prev_count && !checking) {
      Serial.println("set start time");
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
      Serial.println("checking false");
      checking = false;
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      Serial.println("motors might be stalling");
      endTime = millis();
      if (endTime - startTime > 1000) {
        Serial.println("STALLING");
        stalling = true;
      }
    }
    prev_count = ports[LEFT].count;
    Serial.print(enc);
    Serial.print(' ');
    Serial.print(getSensorReadings(2));
    Serial.print(' ');
    Serial.println(abs(ports[motorEncUse].count));


    fix = (int)(PID(enc - abs(ports[motorEncUse].count), pastError, integral, 0.362, 0.015, 1));
    //Serial.println(fix);

    ports[RIGHT].setMotorSpeed(fix + 40);
    ports[LEFT].setMotorSpeed(fix + 40);

  }
  Serial.println("Finished going forward(in motors)");
  delay(10);
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
  return true;
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

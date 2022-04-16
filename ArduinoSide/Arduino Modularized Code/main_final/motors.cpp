#include "motors.h"
char message[4] = {'a', 'a', 'a', 'a'};
MegaPiPort ports[] = { {PORT1B, 18, 31}, {PORT2B, 19, 38}, {PORT3B, 3, 49}, {PORT4B, 2, A1}};
void doTurn(char dir, int deg) {
  ports[RIGHT].count = 0;
  if (dir == 'L') {
    Serial.print("Left turn ");
    Serial.print(deg);
    Serial.println(" degrees.");
    while (abs(ports[0].count) < (WB / D) * deg) { //300 for 90 deg turn 600 for 180 deg turn
      ports[RIGHT].setMotorSpeed(120);
      ports[LEFT].setMotorSpeed(-120);
    }
  } else {
    Serial.print("Right turn ");
    Serial.print(deg);
    Serial.println(" degrees.");
    while (abs(ports[0].count) < (WB / D) * deg) { //300 for 90 deg turn 600 for 180 deg turn
      ports[RIGHT].setMotorSpeed(-120);
      ports[LEFT].setMotorSpeed(120);
    }
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void goForward(int dist) {
  ports[RIGHT].count = 0;
  Serial.print("Forward ");
  Serial.print(dist);
  Serial.println(" centimeters.");
  while (abs(ports[0].count) < (360 / (D * PI))*dist) {
    ports[RIGHT].setMotorSpeed(200);
    ports[LEFT].setMotorSpeed(200);
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void goForwardTiles(int tiles) {
  int tileSize = 30; // Set to 30
  int motorEncUse = 1;
  ports[motorEncUse].count = 0;
  Serial.print("Forward ");
  Serial.print(tiles);
  Serial.print(" tiles. (");
  Serial.print(tiles * 30);
  Serial.println(" centimeters)");

  int enc = ((360 / (D * PI)) * tileSize * tiles);

  while (((abs(ports[motorEncUse].count) < (360 / (D * PI)) * tileSize * tiles)) && (getSensorReadings(2) > 5)) {
    Serial.print(enc);
    Serial.print(' ');
    Serial.println(abs(ports[motorEncUse].count));
    //    if (Serial.available() >= 1) {
    //      if (Serial.read() == 'v') {
    //        char side = Serial.read();
    //        int kits = (Serial.read() - '0');
    //        Serial.print("Side: ");
    //        Serial.println(side);
    //        Serial.print("Kits: ");
    //        Serial.println(kits);
    //        //victim stuff
    //      }
    //    } else {
    ports[RIGHT].setMotorSpeed(200);
    ports[LEFT].setMotorSpeed(200);
    //    }
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
  //delay(1000);
  //Serial.println('f');
  //Serial2.write('f');
}

void goForwardTilesPID(int tiles) {
  int tileSize = 30; // Set to 30
  int motorEncUse = LEFT;
  
  double pastError = 0;
  double integral = 0;
  int fix = 0;
  
  ports[motorEncUse].count = 0;

  double enc = ((360 / (D * PI)) * tileSize * tiles);

  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(2) > 5)) {

    victim();
    if(detectBlack()){
      while(ports[motorEncUse].count>0){
        ports[RIGHT].setMotorSpeed(-80);
        ports[LEFT].setMotorSpeed(-80);
      }
      
    }
    Serial.print(enc);
    Serial.print(' ');
    Serial.println(abs(ports[motorEncUse].count));

    fix = (int)(PID(enc-abs(ports[motorEncUse].count), pastError, integral, 0.362, 0.0, 1));
    Serial.println(fix);
    
    ports[RIGHT].setMotorSpeed(fix+40);
    ports[LEFT].setMotorSpeed(fix+40);
    
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
  
}
// VVVVV incorporates PID wall following, still in progress
void goForwardTiles2(int tiles) {
  int target = 11;
  int Ftarget = 5;
  int kp = 14;
  int Lspeed, Rspeed;
  int motorSpeed = 100;
  int error;
  int tileSize = 30; // Set to 30
  ports[RIGHT].count = 0;
  Serial.print("Forward ");
  Serial.print(tiles);
  Serial.print(" tiles. (");
  Serial.print(tiles * 30);
  Serial.println(" centimeters)");
  while (((abs(ports[0].count) < (360 / (D * PI)) * tileSize * tiles)) && (getSensorReadings(2) > 5)) {
    if (getSensorReadings(3) < 2 * target && (abs(getSensorReadings(3) - getSensorReadings(1)) < target * 2)) {
      error = target - getSensorReadings(3);
      Lspeed = motorSpeed + error * kp;
      Rspeed = motorSpeed - error * kp;

      ports[RIGHT].setMotorSpeed(Rspeed);
      ports[LEFT].setMotorSpeed(Lspeed);
      Serial.print(Lspeed);
      Serial.print(" + ");
      Serial.println(Rspeed);

    } else if (getSensorReadings(4) < 2 * target && (abs(getSensorReadings(4) - getSensorReadings(0)) < target * 2)) {
      error = target - getSensorReadings(4);
      Lspeed = motorSpeed - error * kp;
      Rspeed = motorSpeed + error * kp;

      ports[RIGHT].setMotorSpeed(Rspeed);
      ports[LEFT].setMotorSpeed(Lspeed);
      Serial.print(Lspeed);
      Serial.print(" + ");
      Serial.println(Rspeed);
    } else {
      ports[RIGHT].setMotorSpeed(100);
      ports[LEFT].setMotorSpeed(100);
    }
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void motorControl() {

  Serial.println("Running Motor Control.");
  // Read in the incoming messages
  for (int x = 0; x < 4; x++) {
    message[x] = 'a';
  }

  while (Serial2.available() > 0) {
    if (message[0] == '$') {
      Serial2.write('d');
      break;
    }
    for (int x = 0; x < 4; x++) {
      delay(1);
      message[x] = Serial2.read();
      Serial.print(x);
      Serial.print(": ");
      Serial.println(message[x]);
      if (message[0] == '$')
        break;
    }
    Serial.println("a");
    if (message[0] == 'L' || message[0] == 'R')
      doTurn(message[0], (message[1] - '0') * 10 + (message[2] - '0'));
    if (message[0] == 'F') {
      if (message[1] == 'T') {
        goForwardTiles(message[2] - '0');
      } else {
        goForward(message[1] - '0');
      }
    }
    Serial.println("b");
    alignRobot();
    Serial.println("c");
  }
}

void alignLeft() {
  while (abs(getSensorReadings(3) - getSensorReadings(1)) > 0) {
    //Serial.println(abs(getSensorReadings(3) - getSensorReadings(1)));
    if (getSensorReadings(3) > getSensorReadings(1)) {
      ports[RIGHT].setMotorSpeed(120);
      ports[LEFT].setMotorSpeed(-120);
    }
    else {
      ports[RIGHT].setMotorSpeed(-120);
      ports[LEFT].setMotorSpeed(120);
    }
  }

  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

void alignRight() {
  while (abs(getSensorReadings(4) - getSensorReadings(0)) > 0) {
    //Serial.println(abs(getSensorReadings(3) - getSensorReadings(1)));
    if (getSensorReadings(0) > getSensorReadings(4)) {
      ports[RIGHT].setMotorSpeed(120);
      ports[LEFT].setMotorSpeed(-120);
    }
    else {
      ports[RIGHT].setMotorSpeed(-120);
      ports[LEFT].setMotorSpeed(120);
    }
  }

  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}
/*
void alignFront() {
  if (getSensorReadings(2) < 5) {
    while (getSensorReadings(2) < 5) {
      ports[RIGHT].setMotorSpeed(-120);
      ports[LEFT].setMotorSpeed(-120);
    }
  } else {
    while (getSensorReadings(2) > 5) {
      ports[RIGHT].setMotorSpeed(120);
      ports[LEFT].setMotorSpeed(120);
    }
  }

  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}*/

void alignRobot() {
  if ((getSensorReadings(0) < 30) && (getSensorReadings(4) < 30))
    alignRight();
  else if ((getSensorReadings(1) < 30) && (getSensorReadings(3) < 30))
    alignLeft();
  if (getSensorReadings(2) < 30)
    alignFront();
}

void alignToTile() {
  double distFromCenter;
  double robotWidth = 17;
  int tileSize = 30;
  double turnDegrees = 70;
  int moveDistance;
  int wallVal;
  if ((getSensorReadings(0) < 30) && (getSensorReadings(4) < 30)) {
    alignRight();
    delay(7000);
    distFromCenter = (tileSize / 2) - (getSensorReadings(4) + (robotWidth / 2));
    wallVal = getSensorReadings(4);
    Serial.println("ALIGNING WITH RIGHT WALL");
    Serial.print(abs(distFromCenter));
    Serial.println(" cm away from the center of the tile.");
    Serial.print(tileSize / 2);
    Serial.print(" - (");
    Serial.print(wallVal);
    Serial.print(" + ");
    Serial.print(robotWidth / 2);
    Serial.println(')');
    if (distFromCenter > 0)
      doTurn('L', turnDegrees);
    else
      doTurn('R', turnDegrees);
    moveDistance = abs(distFromCenter) / cos(turnDegrees);
    Serial.print("Moving ");
    Serial.print(moveDistance);
    Serial.println(" cm forward.");
  }
  else if ((getSensorReadings(1) < 30) && (getSensorReadings(3) < 30)) {
    alignLeft();
    delay(7000);
    distFromCenter = (tileSize / 2) - (getSensorReadings(3) + (robotWidth / 2));
    wallVal = getSensorReadings(3);
    Serial.println("ALIGNING WITH LEFT WALL");
    Serial.print(abs(distFromCenter));
    Serial.println(" cm away from the center of the tile.");
    Serial.print(tileSize / 2);
    Serial.print(" - (");
    Serial.print(wallVal);
    Serial.print(" + ");
    Serial.print(robotWidth / 2);
    Serial.println(')');
    if (distFromCenter > 0)
      doTurn('R', turnDegrees);
    else
      doTurn('L', turnDegrees);
    moveDistance = abs(distFromCenter) / cos(turnDegrees);
    Serial.print("Moving ");
    Serial.print(moveDistance);
    Serial.println(" cm forward.");
  }
  if (getSensorReadings(2) < 30)
    alignFront();
}
//template <int PN>
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

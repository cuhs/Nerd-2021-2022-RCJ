#include "motors.h"

char message[4] = {'a', 'a', 'a', 'a'};
MegaPiPort ports[] = { {PORT1B, 18, 31}, {PORT2B, 19, 38}, {PORT3B, 3, 49}, {PORT4B, 2, A1}};

bool goForwardTilesPID(int tiles) {
  Serial.println("in goForwardTilesPID");
  int tileSize = 30; // Set to 30
  int motorEncUse = LEFT;

  double pastError = 0;
  double integral = 0;
  int fix = 0;

  ports[motorEncUse].count = 0;
  double enc = ((360 / (D * PI)) * tileSize * tiles);
  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(2) > 5)) {
    victim();

    if (detectBlack()) {
      Serial.println("SAW BLACK");
      while (ports[motorEncUse].count > 0) {
        ports[RIGHT].setMotorSpeed(-80);
        ports[LEFT].setMotorSpeed(-80);
      }
      //Serial2.write('b');
      ports[RIGHT].setMotorSpeed(0);
      ports[LEFT].setMotorSpeed(0);
      return false;
    }

    fix = (int)(PID(enc - abs(ports[motorEncUse].count), pastError, integral, 0.362, 0.005, 1));
    //Serial.println(fix);

    ports[RIGHT].setMotorSpeed(fix + 40);
    ports[LEFT].setMotorSpeed(fix + 40);

  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
  return true;
}

bool goForwardPID(int dist) {
  int tileSize = 30; // Set to 30
  int motorEncUse = LEFT;

  double pastError = 0;
  double integral = 0;
  int fix = 0;

  ports[motorEncUse].count = 0;

  double enc = ((360 / (D * PI)) * dist);

  while ((abs(ports[motorEncUse].count) < enc) && (getSensorReadings(2) > 5)) {

    victim();
    if (detectBlack()) {
      while (ports[motorEncUse].count > 0) {
        ports[RIGHT].setMotorSpeed(-80);
        ports[LEFT].setMotorSpeed(-80);
      }
      return false;
    }
    //Serial.print(enc);
//    Serial.print(' ');
//    Serial.println(abs(ports[motorEncUse].count));

    fix = (int)(PID(enc - abs(ports[motorEncUse].count), pastError, integral, 0.362, 0.005, 1));
    //Serial.println(fix);

    ports[RIGHT].setMotorSpeed(fix + 40);
    ports[LEFT].setMotorSpeed(fix + 40);

  }
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

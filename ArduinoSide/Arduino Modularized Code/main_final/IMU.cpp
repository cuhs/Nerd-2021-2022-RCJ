#include "IMU.h"


const int ROBOT_WIDTH = 19;
Adafruit_BNO055 bno;
//indicates if the robot has went on a ramp - 1 means up, 2 means down, 0 means didn't do ramp
int finishedRamp = 0;

//initializes the IMU
void initIMU() {
  tcaselect(7);
  if (!bno.begin(Adafruit_BNO055::OPERATION_MODE_IMUPLUS))
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    SERIAL3_PRINT("Ooops, no BNO055 detected .pp.. Check your wiring or I2C ADDR!")
    while (1);
  }

  delay(100);

  bno.setExtCrystalUse(true);
}

//resets the IMU - currently not in use
void reset() {
  SERIAL3_PRINTLN("Resetting.")
  digitalWrite(resetPinIMU, HIGH);
  digitalWrite(resetPinIMU, LOW);

  delayMicroseconds(30);

  digitalWrite(resetPinIMU, HIGH);

  bno.begin();
}

//gets the nearest direction the robot is facing(0, 90, 180, or 270) if the robot is within 20 degrees of one of the 4 directions
int getDirection(int dir) {
  return getDirection(dir, 4);
}

//gets the nearest direction the robot is facing like the above overloaded function if the robot is within 5*factor degrees of one of the 4 directions
int getDirection(int dir, int factor){
  if (dir <= 5*factor || dir >= 360-(5*factor))
    return 0;
  if (dir <= 90+(factor*5) && dir >= 90-(factor*5))
    return 90;
  if (dir <= 180+(factor*5) && dir >= 180-(factor*5))
    return 180;
  if (dir <= 270+(factor*5) && dir >= 270-(factor*5))
    return 270;
  return -1;
}

//returns true if the robot's angle is near a target angle
bool isNearTarget(int dir, int target){
  if(target > 350 || target < 10){
    if(dir > 340 || dir < 20) return true;
    else
      return false;
  }
  if(abs(target - dir) < 20) return true;
  return false;
}

//overloaded function that makes the robot turn right or left depending on its current angular position
void turnAbs(char t) {
  //get BNO values
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  int pos = euler.x();
  //turning right
  if (t == 'r') {
    if (pos >= 315 || pos < 45)
      turnAbs(90);
    else if (pos >= 45 && pos < 135)
      turnAbs(180);
    else if (pos >= 135 && pos < 225)
      turnAbs(270);
    else if (pos >= 225 && pos < 315)
      turnAbs(0);

    //turning left
  } else if (t == 'l') {
    if (pos >= 315 || pos < 45)
      turnAbs(270);
    else if (pos >= 45 && pos < 135)
      turnAbs(0);
    else if (pos >= 135 && pos < 225)
      turnAbs(90);
    else if (pos >= 225 && pos < 315)
      turnAbs(180);
  }
}

//displays IMU values - can be used for debugging
void displayIMU() {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  while (true) {
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    SERIAL3_PRINTLN((int)euler.x())
  }
}

//turns right - currently not used
void turnRight(int degree) {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int curr = euler.x();
  int target = (curr + degree) % 360;
  int error = target - curr;
  while (error >= 2) {
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    error = target - euler.x();
    ports[RIGHT].setMotorSpeed(-150);
    ports[LEFT].setMotorSpeed(150);
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

//turns to an absolute angular position in degrees passed by parameter - will turn right or left depending on which is closer
void turnAbs(int degree) {
  //variables used for stall detection
  unsigned long startTime;
  unsigned long endTime;
  int prev_count = 0;
  bool stalling = false;
  bool checking = false;

  //variables used for PID turning
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int dir[4] = {0, 90, 180, 270};
  int fix;
  int curDir = euler.x();
  int targetDir = degree;
  double integral = 0.0;
  int error = targetDir - curDir;
  double pastError = 0;
  int startingError = error;
  SERIAL3_PRINT("curDir: ")
  SERIAL3_PRINTLN(curDir)
  SERIAL3_PRINT("targetDir: ")
  SERIAL3_PRINTLN(targetDir)
  //variable used to determine when the arduino should send an 'm' to the pi
  bool shouldSendM = true;
  while (abs(error) >= 3 && !stalling) {

    //checks serial and heat sensors to see if any victims were seen and act accordingly
    victim();
    tcaselect(7);
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    curDir = euler.x();
    error = targetDir - curDir;
    //makes sure that the robot will turn left or right depending on which way would be closer to the target angle
    if (error > 180) {
      error -= 360;
    } else if (error < -180)
      error = 360 + error;

    //sends 'm' if the robot is 50% done with its turn
    if(shouldSendM && abs(error)<=(7*abs(startingError))/10){
      shouldSendM = false;
      delay(1);
      Serial2.write('m');
      delay(1);
    }
    //checks if the robot is stalling
    if (ports[LEFT].count == prev_count && !checking) {
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
      checking = false;
      startTime = millis();
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      endTime = millis();
      if (endTime - startTime > 1000 && isNearTarget((int)euler.x(), targetDir)) {
        SERIAL3_PRINTLN("STALLING")
        stalling = true;
      }
    }

    //if the limit switch is pressed in, goes back slightly before finishing the turn
    prev_count = ports[LEFT].count;
    fix = (int)(PID(error, pastError, integral, 2, 0.005, 0));
    if (fix > 0)
      fix += 80;
    else
      fix -= 80;
    ports[RIGHT].setMotorSpeed(-fix);
    ports[LEFT].setMotorSpeed(fix);
    //SERIAL3_PRINTLN(euler.x());
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

//turnAbs but it does not send any 'm', test for obstacles, or test for victims - used for minor turn adjustments such as that used in triangulation
void turnAbsNoVictim(int degree) {
  unsigned long startTime;
  unsigned long endTime;

  int prev_count = 0;
  bool stalling = false;
  bool checking = false;
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int dir[4] = {0, 90, 180, 270};
  int fix;
  int curDir = euler.x();
  int targetDir = degree;
  double integral = 0.0;
  int error = targetDir - curDir;
  double pastError = 0;
  while (abs(error) >= 2 && !stalling) {
    tcaselect(7);
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    curDir = euler.x();
    error = targetDir - curDir;
    if (error > 180) {
      error -= 360;
    } else if (error < -180)
      error = 360 + error;

    if (ports[LEFT].count == prev_count && !checking) {
      //SERIAL3_PRINTLN("set start time");
      startTime = millis();
      checking = true;
    } else if (ports[LEFT].count != prev_count) {
      //SERIAL3_PRINTLN("checking false");
      checking = false;
      startTime = millis();
    }
    if (ports[LEFT].count == prev_count && !stalling) {
      //SERIAL3_PRINTLN("motors might be stalling");
      endTime = millis();
      if (endTime - startTime > 1000 && isNearTarget((int)euler.x(), targetDir)) {
        SERIAL3_PRINTLN("STALLING")
        stalling = true;
      }
    }
    prev_count = ports[LEFT].count;

    fix = (int)(PID(error, pastError, integral, 1.6667, 0, 0));
    if (fix > 0)
      fix += 60;
    else
      fix -= 60;
    //    SERIAL3_PRINT(fix);
    //    SERIAL3_PRINT("\tEuler: ");
    //    SERIAL3_PRINT(euler.x());
    //    SERIAL3_PRINT("\terror: ");
    //    SERIAL3_PRINTLN(error);
    ports[RIGHT].setMotorSpeed(-fix);
    ports[LEFT].setMotorSpeed(fix);
    //SERIAL3_PRINTLN(euler.x());
  }
  ports[RIGHT].setMotorSpeed(0);
  ports[LEFT].setMotorSpeed(0);
}

//the main going forward controller - turns using trigonometry in order to center the robot in each tile when it goes forward
bool triangulation(int left, int right) {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  int distFromCenter;
  int angle;
  int forwardCm;
  int currAngle;
  int tileLength = 30;
  bool noBlack = true;
  //if no walls, turn to the nearest direction(0,90,180,270) and go forward without triangulation
  if (left > 20 && right > 20 || left + ROBOT_WIDTH + right <25) {
    int di = getDirection(euler.x(),9);
    if(di!=-1)
      turnAbsNoVictim(di);
    if (!goForwardTilesPID(1))
      return false;
    return true;
  }
  
  //if closer to right wall
  if (left > right) {
    //calculates distance of the robot from the center of the tile
    distFromCenter = (tileLength/2) - (right + ROBOT_WIDTH / 2);
    if (distFromCenter == 0)
      angle = 0;
    else
      angle = (90 - atan2(30, distFromCenter) * 360 / (2 * PI)); // finds the angle the robot needs to turn in order to move to the center of the next tile
    //uses pythagorean thereom to calculate how much it needs to move forward after turning to move to center of the next tile
    forwardCm = sqrt(pow(distFromCenter, 2) + 900);
    //saves the angle the robot is in before triangulation
    if(getDirection(euler.x(),9)!=-1)
      currAngle = getDirection(euler.x(),9);
     else
      currAngle = euler.x();
    int targetAng = currAngle - angle;
    if (targetAng > 360) targetAng = targetAng % 360;
    if(targetAng < 0) targetAng = targetAng + 360;
    //does initial turn
    turnAbsNoVictim(targetAng);
    //goes forward the amount calculated above - returns true if there is no black tile detected and false if there is a black tile detected
    noBlack = goForwardPID(forwardCm);
    //turns back to the original angle
    turnAbsNoVictim(currAngle);
    //closer to left wall
  } else {
    //see above comments for if the right wall is closer - pretty much the same, except the angle that the robot needs to turn is added instead of subtracted from the initial angle
    distFromCenter = (tileLength/2) - (left + ROBOT_WIDTH / 2);
    if (distFromCenter == 0)
      angle = 0;
    else
      angle = (90-atan2(30, distFromCenter) * 360 / (2 * PI));
    forwardCm = sqrt(pow(distFromCenter, 2) + 900);
    if(getDirection(euler.x(),9)!=-1)
      currAngle = getDirection(euler.x(),9);
    else
      currAngle = euler.x();
    int targetAng = currAngle + angle;
    if (targetAng > 360) targetAng = targetAng % 360;
    if(targetAng < 0) targetAng = targetAng + 360;
    turnAbsNoVictim(targetAng);
    noBlack = goForwardPID(forwardCm);
    turnAbsNoVictim(currAngle);
  }
  return noBlack;
}

//tests to see if the robot is on a ramp - return 1 if it is going up and 2 if it is going down
//turns to the nearest direction(0,90,180,270) if it detects a ramp
int isOnRamp() {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  //if(frontTof>50) return 0;
  if (euler.y() < -15) {
    return 2;
  }
  else if (euler.y() > 15) {
    return 1;
  }
  return 0;
}


//detects if the robot is stable - y direction is at or very close to 0
bool notStable() {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  if (abs(euler.y()) > 2)
    return true;
  return false;
}

bool isOnSpeedBump() {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  if (euler.y() > 4 || abs(euler.z()) > 4)
    return true;
  return false;
}

bool shouldSpeedUp() {
  tcaselect(7);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  if (euler.y() > 5)
    return true;
  return false;
}

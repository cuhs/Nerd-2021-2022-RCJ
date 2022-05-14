#include "MLX.h"

Adafruit_MLX90614 mlx = Adafruit_MLX90614();

void setupHeatSensors() {
  mlx.begin();
}

int getHeatSensorReadings(char side) {
  if (side == 'L')
    tcaselect(4);
  if (side == 'R')
    tcaselect(5);
  return (int)mlx.readObjectTempC();
}

void doHeatVictim(int leftTemp, int rightTemp) {
  if (leftTemp > 27) {
    ports[LEFT].setMotorSpeed(0);
    ports[RIGHT].setMotorSpeed(0);
    delay(1);
    Serial2.write("x");
    delay(1);
    while(!Serial2.available());
    char c = Serial2.read();
    if(c=='y')
      dropKits('L', 1);
  }
  if (rightTemp > 27) {
    ports[LEFT].setMotorSpeed(0);
    ports[RIGHT].setMotorSpeed(0);
    delay(1);
    Serial2.write("X");
    delay(1);
   while(!Serial2.available());
    char c = Serial2.read();
    if(c=='y')
      dropKits('R', 1);
  }
}

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
  if (leftTemp > (int)mlx.readAmbientTempC() + 8) {
    ports[LEFT].setMotorSpeed(0);
    ports[RIGHT].setMotorSpeed(0);
    dropKits('L', 1);
    delay(1);
    Serial2.write("!");
    delay(1);
  }
  if (rightTemp > (int)mlx.readAmbientTempC() + 8) {
    ports[LEFT].setMotorSpeed(0);
    ports[RIGHT].setMotorSpeed(0);
    dropKits('R', 1);
    delay(1);
    Serial2.write("!");
    delay(1);
  }
}

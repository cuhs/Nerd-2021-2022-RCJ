#include "MLX.h"

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
bool isHeat = false;

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
  if (leftTemp > (int)mlx.readAmbientTempC() + 4) {
    delay(1);
    Serial2.write('x');
    delay(1);
    while(!Serial2.available());
    char c = Serial2.read();
    if(c=='y'){
      ports[LEFT].setMotorSpeed(0);
      ports[RIGHT].setMotorSpeed(0);
      //isHeat = true;
      RGB_color(255,165,0,1,'L');
    }
      //dropKits('L', 1);
  }
  if (rightTemp > (int)mlx.readAmbientTempC() + 4) {
    delay(1);
    Serial2.write('X');
    delay(1);
   while(!Serial2.available());
    char c = Serial2.read();
    if(c=='y'){
      //isHeat = true;
      ports[LEFT].setMotorSpeed(0);
      ports[RIGHT].setMotorSpeed(0);
      RGB_color(255,165,0,1,'R');
    }
      //dropKits('R', 1);
  }
}

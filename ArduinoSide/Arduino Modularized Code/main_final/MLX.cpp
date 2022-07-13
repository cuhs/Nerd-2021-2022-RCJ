#include "MLX.h"

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
bool isHeat = false;

//sets up heat sensors
void setupHeatSensors() {
  mlx.begin();
}

//gets readings from heat sensors
int getHeatSensorReadings(char side) {
  if (side == 'L')
    tcaselect(4);
  if (side == 'R')
    tcaselect(5);
  return (int)mlx.readObjectTempC();
}

//detects heat victim if the object temperature is more than 4 degrees C more than the ambient temperature
//writes a 'x' or 'X'(depending on if it is left or right) to the pi, which will send a 'y' if the heat victim was not yet detected
void doHeatVictim(int leftTemp, int rightTemp) {
  if (leftTemp > (int)mlx.readAmbientTempC() + 8) {
    delay(1);
    Serial2.write('x');
    delay(1);
    while(!Serial2.available());
    char c = Serial2.read();
    //Serial.println("Arduino sees heat");
    if(c=='y'){
      isHeat = true;
      //Serial.println("Pi confirm heat");
      ports[LEFT].setMotorSpeed(0);
      ports[RIGHT].setMotorSpeed(0);
      //isHeat = true;
      RGB_color(255,165,0,1,'L');
    }
      //dropKits('L', 1);
  }
  if (rightTemp > (int)mlx.readAmbientTempC() + 8) {
    delay(1); 
    Serial2.write('X');
    delay(1);
   while(!Serial2.available());
    char c = Serial2.read();
    //Serial.println("Arduino sees heat");
    if(c=='y'){
      isHeat = true;
      //Serial.println("Pi confirm heat");
      //isHeat = true;
      ports[LEFT].setMotorSpeed(0);
      ports[RIGHT].setMotorSpeed(0);
      RGB_color(255,165,0,1,'R');
    }
      //dropKits('R', 1);
  }
}

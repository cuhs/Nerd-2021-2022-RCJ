#include "MLX.h"

Adafruit_MLX90614 mlx = Adafruit_MLX90614();

void setupHeatSensors() {
  mlx.begin();
}

int getHeatSensorReadings(int num) {
  tcaselect(num);
  return (int)mlx.readObjectTempC();
}

void doHeatVictim(int leftTemp, int rightTemp) {
  if (leftTemp > (int)mlx.readAmbientTempC() + 9)
    dropKits('L', 1);
  if (rightTemp > (int)mlx.readAmbientTempC() + 9)
    dropKits('R', 1);
}

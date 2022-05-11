#ifndef _MLX_HEAD_
#define _MLX_HEAD_

#include <Adafruit_MLX90614.h>
#include "TCA.h"
#include "rescueServo.h"

void setupHeatSensors();
int getHeatSensorReadings(char);
void doHeatVictim(int leftTemp, int rightTemp);

extern Adafruit_MLX90614 mlx;

#endif

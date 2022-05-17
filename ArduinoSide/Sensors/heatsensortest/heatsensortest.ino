//#include <Arduino.h>
//#include <Adafruit_MLX90614.h>
//
//void setup() {
//  Serial.begin(9600);
//
//}
//
//void loop() {
//  Adafruit_MLX90614 mlx = Adafruit_MLX90614();
//  double temp = mlx.readObjectTempC();
//
//  Serial.print("temp: ");
//  Serial.println(temp);
//
//}

#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include "Adafruit_TCS34725.h"
#include <Arduino.h>

Adafruit_TCS34725 tcs;
#define TCAADDR 0x70

Adafruit_MLX90614 mlx = Adafruit_MLX90614();

extern "C" {
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}

//selects MUX port
void tcaselect(uint8_t i) {
  if (i > 7) return;

  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

int getHeatSensorReadings() {
  return (int)mlx.readObjectTempC();
}

void setup() {
  Serial.begin(9600);

  Serial.println("Adafruit MLX90614 test");

  tcs.begin();
  tcaselect(5);
  
  mlx.begin();
}

void loop() {
  Serial.print("Ambient = "); Serial.print(mlx.readAmbientTempC());
  Serial.print("*C\tObject = "); Serial.print(mlx.readObjectTempC()); Serial.println("*C");
  Serial.print("Ambient = "); Serial.print(mlx.readAmbientTempF());
  Serial.print("*F\tObject = "); Serial.print(mlx.readObjectTempF()); Serial.println("*F");

  Serial.println();
  delay(500);
//  if(getHeatSensorReadings() > (int)mlx.readAmbientTempC() + 9)
//    Serial.println("victim");
//   else
//    Serial.println("no victim");
}

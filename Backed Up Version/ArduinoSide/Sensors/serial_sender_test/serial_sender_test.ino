#include <Arduino.h>

void setup() {
  Serial.begin(9600);
  Serial2.begin(9600);
  Serial2.write('a');
  Serial.println("--------------------STARTING NOW--------------------");

}

void loop() {
  char message;
  
  if (Serial2.available()) {
    message = Serial2.read();
    Serial.print("Recieved message: ");
    Serial.println(message);
    delay(500);
  }
}

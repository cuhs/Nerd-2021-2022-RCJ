#include <Arduino.h>

const int switchPin1 = 6;
const int switchPin2 = 9;

void setup() {
  Serial.begin(9600);
  pinMode(switchPin1, INPUT_PULLUP);
  pinMode(switchPin2, INPUT_PULLUP);

}

void loop() {
  Serial.print("Switch 1: ");
  Serial.print((int)digitalRead(switchPin1));
  Serial.print("\tSwitch 2: ");
  Serial.println((int)digitalRead(switchPin2));
  delay(10);

}

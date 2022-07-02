#include "TCA.h"

//selects MUX port
void tcaselect(uint8_t i) {//make static var
  static uint8_t lastPort;
  if(i==lastPort) return;
  if (i > 7) return;

  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
  lastPort = i;
}

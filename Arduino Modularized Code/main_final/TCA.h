extern "C" {
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}
void tcaselect(uint8_t i);
#define TCAADDR 0x70

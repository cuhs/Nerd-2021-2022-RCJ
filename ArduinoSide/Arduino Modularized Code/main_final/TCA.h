#ifndef _TCA_HEAD_
#define _TCA_HEAD_
#include "new_global_vars.h"
extern "C" {
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}
void tcaselect(uint8_t i);
#define TCAADDR 0x70
#endif

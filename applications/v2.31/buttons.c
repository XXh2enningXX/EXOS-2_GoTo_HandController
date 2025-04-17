
#include "buttons.h"

static int pressed = 0;

void ScanButtons(void) {
    // TODO: read actual GPIOs
    pressed = 0;
}
int ButtonPressed(int code) {
    return (pressed == code);
}

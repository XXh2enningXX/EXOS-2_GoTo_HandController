// utils.c
#include "utils.h"

void InitHardware(void) {
    // TODO: Init GPIOs, UARTs, LCD, etc.
}

void DelayMs(int ms) {
    volatile int i;
    for (i = 0; i < ms * 6000; i++) {
        __asm__("nop");
    }
}


#include "lcd.h"
#include <stdio.h>
#include <stdarg.h>

void InitLCD(void) {
    // Init LCD Pins + Sequenz
}
void LCD_Clear(void) {
    // Clear screen
}
void LCD_Print(const char* fmt, ...) {
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args); // Debug placeholder
    va_end(args);
}

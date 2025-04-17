
#include "motor.h"
#include "buttons.h"
#include "lcd.h"
#include "utils.h"

int main(void) {
    InitHardware();         // UART, LCD, Buttons
    InitMotorControl();     // UART1 init
    InitLCD();

    int speed = 1;
    int tracking = 0;

    while (1) {
        ScanButtons();

        if (ButtonPressed(BTN_LEFT)) {
            StartSlewRA(-speed);
        } else if (ButtonPressed(BTN_RIGHT)) {
            StartSlewRA(speed);
        } else {
            StopSlewRA();
        }

        if (ButtonPressed(BTN_UP)) {
            StartSlewDEC(speed);
        } else if (ButtonPressed(BTN_DOWN)) {
            StartSlewDEC(-speed);
        } else {
            StopSlewDEC();
        }

        if (ButtonPressed(BTN_ENTER)) {
            tracking = !tracking;
            if (tracking) {
                StartTracking();
            } else {
                StopTracking();
            }
        }

        for (int i = 1; i <= 5; i++) {
            if (ButtonPressed(BTN_0 + i)) {
                speed = 1 << (i - 1);  // 1,2,4,8,16
            }
        }

        LCD_Clear();
        LCD_Print("Speed: %dx\n", speed);
        LCD_Print("Tracking: %s", tracking ? "ON" : "OFF");

        DelayMs(200); // debounce & UI refresh
    }
}

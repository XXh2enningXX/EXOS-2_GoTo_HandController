
#include "motor.h"
#include "buttons.h"
#include "lcd.h"
#include "utils.h"

typedef enum {
    MODE_NORMAL,
    MODE_MENU
} AppMode;

AppMode currentMode = MODE_NORMAL;

int main(void) {
    InitHardware();         // UART, LCD, Buttons
    InitMotorControl();     // UART1 init
    InitLCD();

    int speed = 1;
    int tracking = 0;

    while (1) {
        void HandleInput() {
            if (ButtonPressed(BTN_F)) {
                currentMode = (currentMode == MODE_MENU) ? MODE_NORMAL : MODE_MENU;
            }
        
            if (currentMode == MODE_NORMAL) {
                if (ButtonPressed(BTN_0)) {
                    StopSlewRA(); StopSlewDEC(); StopTracking();
                }
        
                for (int i = 1; i <= 9; i++) {
                    if (ButtonPressed(BTN_0 + i)) {
                        speed = 1 << (i - 1); // 1, 2, 4, 8, 16, ...
                    }
                }
        
                if (ButtonPressed(BTN_LEFT))  StartSlewRA(-speed);
                if (ButtonPressed(BTN_RIGHT)) StartSlewRA(speed);
                if (ButtonPressed(BTN_UP))    StartSlewDEC(speed);
                if (ButtonPressed(BTN_DOWN))  StartSlewDEC(-speed);
        
                if (ButtonPressed(BTN_ENTER)) {
                    tracking = !tracking;
                    tracking ? StartTracking() : StopTracking();
                }
            }
            else if (currentMode == MODE_MENU) {
                if (ButtonPressed(BTN_UP))    selectedMenuItem--;
                if (ButtonPressed(BTN_DOWN))  selectedMenuItem++;
                if (selectedMenuItem < 0) selectedMenuItem = 0;
                if (selectedMenuItem >= MENU_ITEM_COUNT) selectedMenuItem = MENU_ITEM_COUNT - 1;
        
                if (ButtonPressed(BTN_ENTER)) {
                    switch (selectedMenuItem) {
                        case 0: StartTracking(); break;
                        case 1: StopTracking(); break;
                        case 2: tracking_speed = 1; break; // Sidereal
                        case 3: tracking_speed = 2; break; // Solar
                        case 4: tracking_speed = 3; break; // Lunar
                    }
                    currentMode = MODE_NORMAL;
                }
            }
        }
        

        void UpdateDisplay(void) {
            LCD_Clear();
            if (currentMode == MODE_NORMAL) {
                LCD_Print("Speed: %dx\\n", speed);
                LCD_Print("Tracking: %s", tracking ? "ON" : "OFF");
            } else if (currentMode == MODE_MENU) {
                for (int i = 0; i < MENU_ITEM_COUNT; i++) {
                    if (i == selectedMenuItem) {
                        LCD_Print("> %s\\n", menuItems[i]);
                    } else {
                        LCD_Print("  %s\\n", menuItems[i]);
                    }
                }
            }
        }
        

        DelayMs(200); // debounce & UI refresh
    }
}

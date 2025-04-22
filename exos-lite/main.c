
#include <stddef.h>        // Für NULL
#include "FreeRTOS.h"
#include "task.h"
#include "menu.h"
#include "input.h"
#include "motor.h"
#include "lcd.h"

void AppMainTask(void* pvParameters) {
    InitLCD();
    InitMotor();
    InitInput();

    LCD_Clear();
    LCD_Print("EXOS Lite Ready");

    for (;;) {
        HandleInput();
        HandleMenu();
        vTaskDelay(pdMS_TO_TICKS(100)); // 100 ms Refresh
    }
}

int main(void) {
    xTaskCreate(AppMainTask, "App", 512, NULL, 2, NULL);
    vTaskStartScheduler();

    while (1); // Sollte nie erreicht werden
}

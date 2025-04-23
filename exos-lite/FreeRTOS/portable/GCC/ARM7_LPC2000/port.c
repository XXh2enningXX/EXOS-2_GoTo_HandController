#include "FreeRTOS.h"
#include "task.h"
#include "lpc214x.h"

void vPortEnterCritical(void) {}
void vPortExitCritical(void) {}

void vTickISR(void) {}

// Wird von FreeRTOS intern benötigt
StackType_t *pxPortInitialiseStack(
    StackType_t *pxTopOfStack,
    TaskFunction_t pxCode,
    void *pvParameters)
{
    // Minimal-Dummy: Stack einfach zurückgeben
    return pxTopOfStack;
}

// Scheduler starten
BaseType_t xPortStartScheduler(void)
{
    vPortISRStartFirstTask();
    return 0; // Nur Dummy
}

// Wird nie wirklich gebraucht, da kein Multicore oder echtes OS
void vPortEndScheduler(void) {}

void vPortISRStartFirstTask(void) {
    // Hier müsste man ARM-spezifisches ASM schreiben
}

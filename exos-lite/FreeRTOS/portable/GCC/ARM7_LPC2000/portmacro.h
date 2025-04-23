
#ifndef PORTMACRO_H
#define PORTMACRO_H

#define portDISABLE_INTERRUPTS()
#define portENABLE_INTERRUPTS()

#define portENTER_CRITICAL() vPortEnterCritical()
#define portEXIT_CRITICAL() vPortExitCritical()

#ifndef portTICK_RATE_MS
#define portTICK_RATE_MS ( ( TickType_t ) 1000 / configTICK_RATE_HZ )
#define portSTACK_GROWTH          (-1)
#define portYIELD()               asm volatile ("NOP")

#define portNOP()                 asm volatile ("NOP")

#define portBYTE_ALIGNMENT        8
#define portMAX_DELAY             ( ( TickType_t ) 0xffffffffUL )

void vPortEnterCritical(void);
void vPortExitCritical(void);
void vTickISR(void);
void vPortISRStartFirstTask(void);

#endif /* PORTMACRO_H */

#ifndef PORTMACRO_H
#define PORTMACRO_H

#define portDISABLE_INTERRUPTS()
#define portENABLE_INTERRUPTS()

#define portENTER_CRITICAL() vPortEnterCritical()
#define portEXIT_CRITICAL() vPortExitCritical()

#define portSTACK_GROWTH          (-1)
#define portYIELD()               asm volatile ("NOP")
#define portNOP()                 asm volatile ("NOP")
#define portBYTE_ALIGNMENT        8
#define portMAX_DELAY             ( ( TickType_t ) 0xffffffffUL )

void vPortEnterCritical(void);
void vPortExitCritical(void);
void vTickISR(void);
void vPortISRStartFirstTask(void);

#define portTASK_FUNCTION_PROTO( vFunction, pvParameters ) void vFunction( void *pvParameters )
#define portTASK_FUNCTION( vFunction, pvParameters )       void vFunction( void *pvParameters )

#endif /* PORTMACRO_H */
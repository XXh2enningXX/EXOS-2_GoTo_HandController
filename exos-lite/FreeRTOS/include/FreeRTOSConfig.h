#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

#include <stdint.h>  // Für uint32_t usw.
#include <stddef.h>  // Für size_t

/*-----------------------------------------------------------
 * Application specific definitions.
 *
 * Adjust these for your hardware and application.
 *----------------------------------------------------------*/

#define configUSE_PREEMPTION            1
#define configUSE_IDLE_HOOK             0
#define configUSE_TICK_HOOK             0
#define configCPU_CLOCK_HZ              ( ( unsigned long ) 60000000 )
#define configTICK_RATE_HZ              ( ( unsigned long ) 1000 )
#define configMAX_PRIORITIES            5
#define configMINIMAL_STACK_SIZE        ( ( unsigned short ) 128 )
#define configTOTAL_HEAP_SIZE           ( ( size_t ) ( 5 * 1024 ) )
#define configMAX_TASK_NAME_LEN         16
#define configUSE_TRACE_FACILITY        0
#define configUSE_16_BIT_TICKS          0
#define configIDLE_SHOULD_YIELD         1
#define configUSE_MUTEXES               1
#define configUSE_RECURSIVE_MUTEXES     0
#define configUSE_COUNTING_SEMAPHORES   0
#define configUSE_TIMERS                0
#define configCHECK_FOR_STACK_OVERFLOW  0
#define configUSE_MALLOC_FAILED_HOOK    0
#define configGENERATE_RUN_TIME_STATS   0

// Interrupt priorities
#define configKERNEL_INTERRUPT_PRIORITY         1
#define configMAX_SYSCALL_INTERRUPT_PRIORITY    4

#define INCLUDE_vTaskDelay                 1
#define INCLUDE_vTaskDelete                1
#define INCLUDE_vTaskSuspend               1
#define INCLUDE_vTaskPrioritySet           1
#define INCLUDE_uxTaskPriorityGet          1
#define INCLUDE_vTaskDelayUntil            1
#define INCLUDE_xTaskGetIdleTaskHandle     0
#define INCLUDE_xTaskGetSchedulerState     1


// Required type definitions
typedef int32_t BaseType_t;
typedef uint32_t UBaseType_t;
typedef uint32_t TickType_t;
typedef uint32_t StackType_t;

#endif /* FREERTOS_CONFIG_H */

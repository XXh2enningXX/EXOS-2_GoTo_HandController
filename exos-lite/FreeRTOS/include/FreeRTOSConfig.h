#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

#define configUSE_PREEMPTION            1
#define configUSE_IDLE_HOOK             0
#define configUSE_TICK_HOOK             0
#define configCPU_CLOCK_HZ              ( ( unsigned long ) 60000000 ) // 60 MHz CPU-Takt
#define configTICK_RATE_HZ              ( ( TickType_t ) 1000 )        // 1 ms Ticks
#define configMAX_PRIORITIES            5
#define configMINIMAL_STACK_SIZE        ( ( unsigned short ) 128 )
#define configTOTAL_HEAP_SIZE           ( ( size_t ) ( 5 * 1024 ) )     // 5 KB Heap
#define configMAX_TASK_NAME_LEN         16
#define configUSE_TRACE_FACILITY        0
#define configUSE_16_BIT_TICKS          0
#define configIDLE_SHOULD_YIELD         1

// Synchronisation
#define configUSE_MUTEXES               1
#define configUSE_COUNTING_SEMAPHORES   0
#define configUSE_RECURSIVE_MUTEXES     0

// Software Timer (optional)
#define configUSE_TIMERS                0

// Interrupt Prioritäten (nicht bei ARM7 relevant, aber Pflichtfelder)
#define configKERNEL_INTERRUPT_PRIORITY         1
#define configMAX_SYSCALL_INTERRUPT_PRIORITY    4

// Hook-Funktionen deaktivieren
#define configCHECK_FOR_STACK_OVERFLOW  0
#define configUSE_MALLOC_FAILED_HOOK    0

// Für Debug optional:
#define configGENERATE_RUN_TIME_STATS   0

#endif /* FREERTOS_CONFIG_H */

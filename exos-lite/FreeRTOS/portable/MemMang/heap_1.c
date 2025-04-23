
#include "FreeRTOS.h"
#include <stddef.h>

#define HEAP_SIZE configTOTAL_HEAP_SIZE
static uint8_t heap[HEAP_SIZE];
static size_t index = 0;

void *pvPortMalloc(size_t size) {
    if ((index + size) > HEAP_SIZE) return NULL;
    void* ptr = &heap[index];
    index += size;
    return ptr;
}

void vPortFree(void* ptr) {
    // heap_1: keine Freigabe
}

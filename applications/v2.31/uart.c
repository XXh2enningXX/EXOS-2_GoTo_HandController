
#include "uart.h"
volatile char* UART1 = (char*)0xE0010000;

void uart1_init(int dummy) {
    // Init UART1 (simplified)
}
void uart1_send(unsigned char* data, unsigned char len) {
    for (int i = 0; i < len; i++) {
        // send byte
    }
}

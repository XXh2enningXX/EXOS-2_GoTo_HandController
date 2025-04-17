
#include "motor.h"
#include "uart.h"

void InitMotorControl(void) {
    uart1_init(0);
}

void send_motor_command(unsigned char id, int speed) {
    unsigned char packet[] = { 0x55, 0xAA, 0x01, 0x03, 0x05, id, (unsigned char)speed };
    uart1_send(packet, 7);
}

void StartSlewRA(int speed) {
    send_motor_command(1, speed);
}
void StopSlewRA(void) {
    send_motor_command(1, 0);
}
void StartSlewDEC(int speed) {
    send_motor_command(2, speed);
}
void StopSlewDEC(void) {
    send_motor_command(2, 0);
}
void StartTracking(void) {
    send_motor_command(1, 1);
    send_motor_command(2, 0);
}
void StopTracking(void) {
    send_motor_command(1, 0);
    send_motor_command(2, 0);
}

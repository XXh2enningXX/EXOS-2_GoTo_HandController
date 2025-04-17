
#ifndef MOTOR_H
#define MOTOR_H

void InitMotorControl(void);
void StartSlewRA(int speed);
void StopSlewRA(void);
void StartSlewDEC(int speed);
void StopSlewDEC(void);
void StartTracking(void);
void StopTracking(void);

#endif

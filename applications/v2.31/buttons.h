
#ifndef BUTTONS_H
#define BUTTONS_H

#define BTN_LEFT  1
#define BTN_RIGHT 2
#define BTN_UP    3
#define BTN_DOWN  4
#define BTN_ENTER 5
#define BTN_0     10

void ScanButtons(void);
int ButtonPressed(int code);

#endif

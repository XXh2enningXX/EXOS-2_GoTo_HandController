// hardware.h
#ifndef HARDWARE_H
#define HARDWARE_H

// Temporärer Ersatz für my_types.h
typedef unsigned char  u8;
typedef unsigned short u16;
typedef unsigned int   u32;

void lpc_hw_init(void);
void lcd_display_clear(void);
void lcd_display_write_string(const char *str, int line, int column);

#endif

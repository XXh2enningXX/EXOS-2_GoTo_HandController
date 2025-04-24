#include <LPC214x.h>
#include "hardware.h" // ehemals file1f30.c

int main(void) {
    lpc_hw_init();  // Initialisiert Clock, GPIOs, Display usw.

    lcd_display_clear();                // Bildschirm löschen
    lcd_display_write_string("Hallo!", 0, 0);  // Zeile 0, Spalte 0

    while (1);  // Endlosschleife, System bleibt aktiv
}

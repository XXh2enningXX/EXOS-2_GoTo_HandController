/* linker.ld - Für LPC2148 mit 512KB Flash, 32KB RAM */
MEMORY
{
  FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 512K
  RAM (rwx)  : ORIGIN = 0x40000000, LENGTH = 32K
}

SECTIONS
{
  .text : {
    *(.vectors)
    *(.text*)
    *(.rodata*)
  } > FLASH

  .data : {
    *(.data*)
  } > RAM AT > FLASH

  .bss : {
    *(.bss*)
    *(COMMON)
  } > RAM

  .stack (COPY) : {
    _stack = .;
  } > RAM
}

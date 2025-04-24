
CC=arm-none-eabi-gcc
CFLAGS=-mcpu=arm7tdmi -nostdlib -Wall -Wextra -Os -I. -IFreeRTOS/include -IFreeRTOS/portable/GCC/ARM7_LPC2000
LDFLAGS=-T linker.ld

OBJS=main.o hardware.o menu.o input.o motor.o lcd.o lib/dummy_lib.o FreeRTOS/list.o FreeRTOS/portable/GCC/ARM7_LPC2000/port.o FreeRTOS/tasks.o FreeRTOS/queue.o FreeRTOS/portable/MemMang/heap_1.o

all: main.elf main.hex

main.elf: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS) -o main.elf

main.hex: main.elf
	arm-none-eabi-objcopy -O ihex $< $@

clean:
	rm -f *.o *.elf *.hex

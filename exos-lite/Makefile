
CC=arm-none-eabi-gcc
CFLAGS=-mcpu=arm7tdmi -nostdlib -Wall -Wextra -Os -I. -IFreeRTOS/include -IFreeRTOS/portable/GCC/ARM7_LPC214x
LDFLAGS=-T linker.ld

OBJS=main.o menu.o input.o motor.o lcd.o FreeRTOS/portable/GCC/ARM7_LPC214x/port.o FreeRTOS/list.o FreeRTOS/tasks.o FreeRTOS/queue.o FreeRTOS/portable/MemMang/heap_1.o

all: main.elf main.hex

main.elf: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

main.hex: main.elf
	arm-none-eabi-objcopy -O ihex $< $@

clean:
	rm -f *.o *.elf *.hex

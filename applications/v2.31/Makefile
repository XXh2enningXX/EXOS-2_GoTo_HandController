
CC=arm-none-eabi-gcc
CFLAGS=-mcpu=arm7tdmi -nostdlib -Wall -Wextra -Os
LDFLAGS=-T linker.ld

OBJS=main.o motor.o buttons.o lcd.o uart.o utils.o

all: main.elf main.hex

main.elf: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

main.hex: main.elf
	arm-none-eabi-objcopy -O ihex $< $@

clean:
	rm -f *.o *.elf *.hex

# main.py – Steuerung für RA/DEC Motoren über HBX
# Läuft auf Raspberry Pi Pico (MicroPython)

import machine
from lookup import CMD_RA, CMD_DEC  # aus deinem lookup.py

# UART1 initialisieren
# Pins ggf. anpassen (GPIO4=TX, GPIO5=RX ist nur ein Beispiel)
uart = machine.UART(1, baudrate=9600, tx=machine.Pin(8), rx=machine.Pin(9))

def send_frame(frame: bytes):
    """Schickt ein einzelnes Frame über UART1."""
    uart.write(frame)

def set_speed(axis: str, speed: int):
    """
    Setzt die Geschwindigkeit für die angegebene Achse.
    axis: 'ra' oder 'dec'
    speed: -9 … +9
    """
    if axis.lower() == "ra":
        table = CMD_RA
    elif axis.lower() == "dec":
        table = CMD_DEC
    else:
        print("Unbekannte Achse:", axis)
        return

    key = str(speed)
    if key in table:
        frame = table[key]
        send_frame(frame)
        print(f"Sende {axis.upper()} speed {speed}: {frame.hex(' ').upper()}")
    else:
        print(f"Keine Frame für {axis} speed {speed} definiert.")

def stop_all():
    """Stoppt beide Achsen."""
    set_speed("ra", 0)
    set_speed("dec", 0)

def repl_loop():
    """Einfache Eingabe über USB-Konsole."""
    print("HBX-Sim Pico bereit.")
    print("Befehle: ra <speed>, dec <speed>, stop")
    
    uart.write(b"Test123\r\n")

    while True:
        try:
            cmd = input(">> ").strip().split()
            if not cmd:
                continue

            if cmd[0] == "stop":
                stop_all()
            elif cmd[0] in ("ra", "dec") and len(cmd) == 2:
                axis = cmd[0]
                try:
                    speed = int(cmd[1])
                    set_speed(axis, speed)
                except ValueError:
                    print("Ungültige Geschwindigkeit:", cmd[1])
            elif cmd[0] == "q":
                stop_all()
                print("Beendet mit q.")
                break
            else:
                print("Unbekannter Befehl:", " ".join(cmd))
        except KeyboardInterrupt:
            stop_all()
            print("Beendet.")
            break

# Hauptprogramm starten
if __name__ == "__main__":
    repl_loop()

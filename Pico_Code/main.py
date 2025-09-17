import sys, uselect
import lookup  # deine Lookup-Tabelle

# Poll-Objekt für non-blocking Konsoleneingaben
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

def read_input_line():
    res = poll.poll(0)  # 0 = non-blocking
    if res:
        line = sys.stdin.readline()
        return line.strip()
    return ""

def send_frame(frame):
    # TODO: hier deine UART / I2C / GPIO Ausgabe einsetzen
    print("Sende Frame:", frame)

def handle_command(cmd):
    parts = cmd.split()
    if not parts:
        return
    if parts[0] == "ra":
        if len(parts) > 1:
            speed = parts[1]
            frame = lookup.CMD_RA.get(speed)
            if frame:
                send_frame(frame)
            else:
                print("Unbekannte RA-Speed:", speed)
    elif parts[0] == "dec":
        if len(parts) > 1:
            speed = parts[1]
            frame = lookup.CMD_DEC.get(speed)
            if frame:
                send_frame(frame)
            else:
                print("Unbekannte DEC-Speed:", speed)
    elif parts[0] == "q":
        print("Beende HBX-Sim Pico")
        raise SystemExit
    else:
        print("Unbekannter Befehl:", cmd)

def main():
    print("HBX-Sim Pico läuft.")
    print("Befehle über USB-Konsole:")
    print("  ra <speed>   (z.B. ra 16, ra -64, ra 0)")
    print("  dec <speed>  (z.B. dec 8, dec -128, dec 0)")
    print("  q            (beenden)")

    while True:
        cmd = read_input_line()
        if cmd:
            handle_command(cmd)

if __name__ == "__main__":
    main()

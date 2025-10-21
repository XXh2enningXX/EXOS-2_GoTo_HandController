# log_only.py — Motorsteuerung initialisieren & Logging starten
from machine import UART, Pin
import utime
from lookup import CMD_RA, CMD_DEC

# ---------------- UART und Pins ----------------
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
ra_ra2 = Pin(7, Pin.OUT)
dec_ra2 = Pin(6, Pin.OUT)

# ---------------- Hilfsfunktionen ----------------
def send_frame(frame: bytes):
    uart.write(frame)

def _hexstr(b: bytes) -> str:
    return " ".join(f"{x:02X}" for x in b)

def _now_ms():
    return utime.ticks_ms()

# ---------------- Initialisierung der Montierung ----------------
def init_mount():
    print("Initialisiere Motorsteuerung ...")
    ra_ra2.value(0)
    dec_ra2.value(1)
    utime.sleep_ms(25)
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0xFF]))
    utime.sleep_ms(20)
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x44]))
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x64]))
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x04]))
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x24]))
    utime.sleep_ms(30)
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x10]))
    utime.sleep_ms(140)
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x30]))
    print("... Initialisierung abgeschlossen.")

# ---------------- Status-Abfrage-Frames ----------------
INQ_RA  = bytes.fromhex("55 AA 01 01 04")
INQ_DEC = bytes.fromhex("55 AA 01 01 24")

# ---------------- RX-Parser ----------------
class RxParser:
    def __init__(self):
        self.state = 0
        self.len = 0
        self.buf = bytearray()

    def feed(self, b: int):
        if self.state == 0:
            if b == 0x55: self.state = 1
        elif self.state == 1:
            self.state = 2 if b == 0xAA else 0
        elif self.state == 2:
            self.state = 3 if b == 0x01 else 0
        elif self.state == 3:
            if b < 32:
                self.len = b
                self.buf = bytearray()
                self.state = 4
            else:
                self.state = 0
        elif self.state == 4:
            self.buf.append(b)
            if len(self.buf) == self.len:
                pkt = bytes([0x55, 0xAA, 0x01, self.len]) + bytes(self.buf)
                self.state = 0
                return pkt
        return None

def _drain_and_log(f, parser: RxParser, timeout_ms: int):
    t0 = _now_ms()
    while utime.ticks_diff(_now_ms(), t0) < timeout_ms:
        if uart.any():
            b = uart.read(1)
            if not b:
                continue
            pkt = parser.feed(b[0])
            if pkt:
                f.write(f"{_now_ms():010d} RX {_hexstr(pkt)}\n")
        else:
            utime.sleep_ms(1)

# ---------------- Logging-Funktion ----------------
def log_run(duration_s=60, ra_speed="1", dec_speed="0",
            cycle_ms=290, gap_ms=20, log_prefix="ra_dec_log"):
    ra_cmd = CMD_RA.get(ra_speed)
    dec_cmd = CMD_DEC.get(dec_speed)
    if ra_cmd is None or dec_cmd is None:
        raise ValueError("Ungültige RA/DEC Speed: '0'..'9' oder '-1'..'-9'")

    parser = RxParser()
    fname = f"{log_prefix}_{utime.time()}.txt"

    with open(fname, "w") as f:
        f.write("# t_ms KIND HEX\n")
        f.write(f"# RA_SPEED={ra_speed} DEC_SPEED={dec_speed}\n")

        # initiale Slew-Frames
        send_frame(ra_cmd); f.write(f"{_now_ms():010d} TX {_hexstr(ra_cmd)}\n"); utime.sleep_ms(gap_ms)
        send_frame(dec_cmd); f.write(f"{_now_ms():010d} TX {_hexstr(dec_cmd)}\n"); utime.sleep_ms(gap_ms)
        _drain_and_log(f, parser, 50)

        t_end = utime.ticks_add(_now_ms(), duration_s * 1000)
        while utime.ticks_diff(t_end, _now_ms()) > 0:
            t_cycle = _now_ms()

            uart.write(INQ_RA);  f.write(f"{_now_ms():010d} TX {_hexstr(INQ_RA)}\n");  utime.sleep_ms(gap_ms)
            _drain_and_log(f, parser, 30)
            uart.write(INQ_DEC); f.write(f"{_now_ms():010d} TX {_hexstr(INQ_DEC)}\n"); utime.sleep_ms(gap_ms)
            _drain_and_log(f, parser, 30)

            send_frame(ra_cmd);  f.write(f"{_now_ms():010d} TX {_hexstr(ra_cmd)}\n");  utime.sleep_ms(gap_ms)
            send_frame(dec_cmd); f.write(f"{_now_ms():010d} TX {_hexstr(dec_cmd)}\n"); utime.sleep_ms(gap_ms)

            elapsed = utime.ticks_diff(_now_ms(), t_cycle)
            rest = cycle_ms - elapsed
            if rest > 0:
                _drain_and_log(f, parser, rest)

        # Stop
        send_frame(CMD_RA["0"]); f.write(f"{_now_ms():010d} TX {_hexstr(CMD_RA['0'])}\n")
        send_frame(CMD_DEC["0"]); f.write(f"{_now_ms():010d} TX {_hexstr(CMD_DEC['0'])}\n")

    print("Log gespeichert als:", fname)
    return fname

# ---------------- Hauptablauf ----------------
if __name__ == "__main__":
    init_mount()
    # Beispiel: 120 s RA-Speed=1, DEC=0
    log_run(duration_s=60, ra_speed="-5", dec_speed="-5")
    print("Fertig – Datei im Pico-Dateisystem.")

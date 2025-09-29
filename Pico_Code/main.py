# main.py
from machine import UART, Pin
import utime
from lookup import CMD_RA, CMD_DEC

# UART1: TX=Pin8, RX=Pin9
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))

COUNTS_PER_ARCSEC = 2.55       # aus Kalibrierung (≈38.3 counts/s bei 15.04"/s)
COUNTS_PER_DEG = COUNTS_PER_ARCSEC * 3600

def send_frame(frame: bytes):
    uart.write(frame)

def read_response(timeout_ms=50):
    start = utime.ticks_ms()
    resp = b''
    while utime.ticks_diff(utime.ticks_ms(), start) < timeout_ms:
        if uart.any():
            resp += uart.read()
    return resp

def parse_position(resp: bytes):
    """ Erwartet Antwort mit mindestens 4 Nutzbytes """
    if len(resp) < 4:
        return None
    # Nimm die letzten 4 Bytes (Positionszähler, Big-Endian)
    val = int.from_bytes(resp[-4:], "big")
    # Umrechnen
    deg = (val / COUNTS_PER_DEG) % 360
    arcsec = val / COUNTS_PER_ARCSEC
    return val, deg, arcsec

def loop(speed_ra="0", speed_dec="0"):
    while True:
        t0 = utime.ticks_ms()

        # 1. Status RA
        send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x04]))
        resp_ra = read_response()
        pos_ra = parse_position(resp_ra)
        if pos_ra:
            val, deg, arcsec = pos_ra
            print(f"RA raw={val}  deg={deg:.6f}°  arcsec={arcsec:.1f}\"")
        else:
            print("RA-Status unvollständig:", resp_ra)

        utime.sleep_ms(25)

        # 2. Status DEC
        send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x24]))
        resp_dec = read_response()
        pos_dec = parse_position(resp_dec)
        if pos_dec:
            val, deg, arcsec = pos_dec
            print(f"DEC raw={val}  deg={deg:.6f}°  arcsec={arcsec:.1f}\"")
        else:
            print("DEC-Status unvollständig:", resp_dec)

        utime.sleep_ms(35)

        # 3. Slew
        send_frame(CMD_RA[speed_ra])
        send_frame(CMD_DEC[speed_dec])
        print("Slew:", speed_ra, speed_dec)

        # Rest bis 300 ms
        elapsed = utime.ticks_diff(utime.ticks_ms(), t0)
        if elapsed < 300:
            utime.sleep_ms(300 - elapsed)
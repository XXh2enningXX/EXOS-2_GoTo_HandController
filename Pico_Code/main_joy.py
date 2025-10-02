from machine import UART, Pin, Timer, ADC
import utime
from lookup import CMD_RA, CMD_DEC

# UART1: TX=Pin8, RX=Pin9
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
ra_ra2 = Pin(5, Pin.OUT)
dec_ra2 = Pin(4, Pin.OUT)

# Joystick
adc_x = ADC(26)   # VRX
adc_y = ADC(27)   # VRY
sw    = Pin(22, Pin.IN, Pin.PULL_UP)  # Switch (active-low)

COUNTS_PER_ARCSEC = 2.55       # aus Kalibrierung (≈38.3 counts/s bei 15.04"/s)
COUNTS_PER_DEG = COUNTS_PER_ARCSEC * 3600

# Globale Variablen
speed_ra = '5'
speed_dec = '0'
run = False   # Loop-Status
_timers = []  # Liste zum Speichern der Timer-Objekte
_last = {"ra": None, "dec": None}

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
    val = int.from_bytes(resp[-4:], "big")
    deg = (val / COUNTS_PER_DEG) % 360
    arcsec = val / COUNTS_PER_ARCSEC
    return val, deg, arcsec

def request_status_ra(timer):
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x04]))
    resp_ra = read_response()
    pos_ra = parse_position(resp_ra)
    if pos_ra:
        val, deg, arcsec = pos_ra
        print(f"RA raw={val}  deg={deg:.6f}°  arcsec={arcsec:.1f}\"")
    else:
        print("RA-Status unvollständig:", resp_ra)
        
def request_status_dec(timer):
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x24]))
    resp_dec = read_response()
    pos_dec = parse_position(resp_dec)
    if pos_dec:
        val, deg, arcsec = pos_dec
        print(f"DEC raw={val}  deg={deg:.6f}°  arcsec={arcsec:.1f}\"")
    else:
        print("DEC-Status unvollständig:", resp_dec)

def send_slew(timer):
    send_frame(CMD_RA[speed_ra])
    send_frame(CMD_DEC[speed_dec])
    print("Slew:", speed_ra, speed_dec)

# ---- Joystick ----
def adc_to_speed(v, dead=4000):
    """ ADC 0..65535 -> Speed -9..+9 (String) """
    mid = 32768
    delta = v - mid
    if abs(delta) <= dead:
        return '0'
    span = 65535/2 - dead
    norm = max(-1.0, min(1.0, delta / span))
    s = int(round(norm * 9))
    if -1 <= s <= 1:
        s = 0
    return str(max(-9, min(9, s)))

def poll_joystick(timer):
    global speed_ra, speed_dec, _last
    sx = adc_to_speed(adc_x.read_u16())
    sy = adc_to_speed(adc_y.read_u16())
    if sw.value() == 0:  # gedrückt -> Stop
        sx, sy = '0', '0'

    if sx != _last["ra"]:
        speed_ra = sx
        _last["ra"] = sx
        print("Joystick RA ->", sx)
    if sy != _last["dec"]:
        speed_dec = sy
        _last["dec"] = sy
        print("Joystick DEC ->", sy)

# ---- Main ----
def main():
    global run, _timers
    run = True
    
    # initialization
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
    
    # Timer initialisieren
    timer_ra_request = Timer()
    timer_ra_request.init(period=370, mode=Timer.PERIODIC, callback=request_status_ra)
    utime.sleep_ms(25)
    timer_dec_request = Timer()
    timer_dec_request.init(period=370, mode=Timer.PERIODIC, callback=request_status_dec)
    utime.sleep_ms(35)
    timer_slew = Timer()
    timer_slew.init(period=370, mode=Timer.PERIODIC, callback=send_slew)
    timer_joy = Timer()
    timer_joy.init(period=50, mode=Timer.PERIODIC, callback=poll_joystick)

    _timers = [timer_ra_request, timer_dec_request, timer_slew, timer_joy]

    i = 0
    while run:
        i += 1
        print("Loop-Zähler:", i)
        utime.sleep_ms(500)

    stop()

def stop():
    """Stoppt die Timer und beendet den Loop"""
    global run, _timers
    run = False
    for t in _timers:
        try:
            t.deinit()
        except:
            pass
    _timers = []
    print("Main loop beendet.")

if __name__ == "__main__":
    main()

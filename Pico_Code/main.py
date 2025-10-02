# main.py
from machine import UART, Pin, Timer, ADC
import utime
from lookup import CMD_RA, CMD_DEC

# ---------- UART & IO ----------
# UART1: TX=Pin8, RX=Pin9
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
ra_ra2 = Pin(5, Pin.OUT)
dec_ra2 = Pin(4, Pin.OUT)

# Joystick
adc_x = ADC(26)   # VRX -> GP26/ADC0
adc_y = ADC(27)   # VRY -> GP27/ADC1
sw    = Pin(22, Pin.IN, Pin.PULL_UP)  # Switch (active-low)

# ---------- Konstanten ----------
COUNTS_PER_ARCSEC = 2.55       # aus Kalibrierung (≈38.3 counts/s bei 15.04"/s)
COUNTS_PER_DEG = COUNTS_PER_ARCSEC * 3600
DEADZONE = 4000                # Deadzone der Joystick-Mitte (ADC ~0..65535)
JOY_PERIOD_MS = 50             # Poll-Rate Joystick
TRACK_SPEED_RA = '1'           # Tracking-Geschwindigkeit RA bei Toggle

# ---------- Globale Zustände ----------
speed_ra = '5'
speed_dec = '0'
run = False                     # Loop-Status / Kill-Switch für Callbacks
tracking_enabled = False        # RA-Tracking an/aus
_last_irq_ms = 0                # Debounce für Switch
_last = {"ra": None, "dec": None}
_timers = {}                    # name -> Timer-Objekt (mit festen IDs)

# ---------- Hilfsfunktionen ----------
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

def frame_from_lookup(table, spd_str):
    """Sichere Tabellenabfrage mit Fallback auf '0'."""
    return table.get(spd_str, table.get('0'))

# ---------- Protokoll-Callbacks ----------
def request_status_ra(timer):
    if not run:
        return
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x04]))
    resp_ra = read_response()
    pos_ra = parse_position(resp_ra)
    if pos_ra:
        val, deg, arcsec = pos_ra
        print(f"RA raw={val}  deg={deg:.6f}°  arcsec={arcsec:.1f}\"")
    else:
        print("RA-Status unvollständig:", resp_ra)
        
def request_status_dec(timer):
    if not run:
        return
    send_frame(bytes([0x55, 0xAA, 0x01, 0x01, 0x24]))
    resp_dec = read_response()
    pos_dec = parse_position(resp_dec)
    if pos_dec:
        val, deg, arcsec = pos_dec
        print(f"DEC raw={val}  deg={deg:.6f}°  arcsec={arcsec:.1f}\"")
    else:
        print("DEC-Status unvollständig:", resp_dec)

def send_slew(timer):
    if not run:
        return
    # Kurze Pause zwischen RA/DEC hält das Protokoll robust
    send_frame(frame_from_lookup(CMD_RA, speed_ra))
    utime.sleep_ms(20)
    send_frame(frame_from_lookup(CMD_DEC, speed_dec))
    print("Slew:", speed_ra, speed_dec)

# ---------- Joystick / Tracking ----------
def adc_to_speed(v, dead=DEADZONE):
    """ADC 0..65535 -> nichtlineare Stufen -9..+9"""
    mid = 32768
    delta = v - mid
    if abs(delta) <= dead:
        return '0'

    span = 32768 - dead
    norm = delta / span   # -1.0 .. +1.0

    def map_zone(x):
        ax = abs(x)
        if ax < 0.2:  return 1
        if ax < 0.4:  return 2
        if ax < 0.6:  return 4
        if ax < 0.8:  return 8
        return 9

    s = map_zone(norm)
    if norm < 0:
        s = -s
    return str(s)
def compute_effective_speeds(js_rx, js_ry):
    """
    Joystick überschreibt Tracking. Wenn Joystick 'losgelassen' (0),
    dann RA = TRACK_SPEED_RA (falls tracking_enabled), sonst 0.
    DEC hat kein Tracking.
    """
    eff_ra = js_rx if js_rx != '0' else (TRACK_SPEED_RA if tracking_enabled else '0')
    eff_dec = js_ry  # DEC kein Tracking
    return eff_ra, eff_dec

def poll_joystick(timer):
    if not run:
        return
    js_rx = adc_to_speed(adc_x.read_u16())
    js_ry = adc_to_speed(adc_y.read_u16())

    eff_ra, eff_dec = compute_effective_speeds(js_rx, js_ry)

    global speed_ra, speed_dec
    if eff_ra != _last["ra"]:
        speed_ra = eff_ra
        _last["ra"] = eff_ra
        print("RA <-", eff_ra, "(tracking {} )".format("AN" if tracking_enabled else "AUS"))
    if eff_dec != _last["dec"]:
        speed_dec = eff_dec
        _last["dec"] = eff_dec
        print("DEC <-", eff_dec)

def _on_sw(pin):
    """IRQ: Toggle Tracking mit Debounce."""
    global _last_irq_ms, tracking_enabled
    now = utime.ticks_ms()
    if utime.ticks_diff(now, _last_irq_ms) < 250:
        return
    _last_irq_ms = now
    tracking_enabled = not tracking_enabled
    print("Tracking:", "AN" if tracking_enabled else "AUS")

# ---------- Start/Stop ----------
def _start_timers():
    # Soft-Timer (-1) für alle Aufgaben
    t0 = Timer(-1); t0.init(period=370, mode=Timer.PERIODIC, callback=request_status_ra)
    utime.sleep_ms(25)
    t1 = Timer(-1); t1.init(period=370, mode=Timer.PERIODIC, callback=request_status_dec)
    utime.sleep_ms(35)
    t2 = Timer(-1); t2.init(period=370, mode=Timer.PERIODIC, callback=send_slew)
    t3 = Timer(-1); t3.init(period=JOY_PERIOD_MS, mode=Timer.PERIODIC, callback=poll_joystick)
    _timers.update({
        "ra_req": t0,
        "dec_req": t1,
        "slew":   t2,
        "joy":    t3,
    })

def _stop_timers():
    for name, t in list(_timers.items()):
        try:
            t.deinit()
        except Exception as e:
            print("Warnung: Timer", name, "deinit fehlgeschlagen:", e)
        _timers.pop(name, None)


def main():
    global run
    run = True

    # Switch-IRQ für Tracking-Toggle
    try:
        sw.irq(trigger=Pin.IRQ_FALLING, handler=_on_sw)
    except Exception as e:
        print("Hinweis: Konnte IRQ nicht setzen:", e)

    # Initialization-Sequenz
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

    _start_timers()

    i = 0
    while run:
        i += 1
        print("Loop-Zähler:", i)
        utime.sleep_ms(500)

    stop()  # beim Beenden Timer sauber deinitialisieren

def stop():
    """Stoppt die Timer und beendet den Loop."""
    global run
    run = False                  # Kill-Switch für Callbacks
    _stop_timers()               # Timer zuverlässig stoppen
    print("Main loop beendet und Timer deinitialisiert.")

if __name__ == "__main__":
    main()

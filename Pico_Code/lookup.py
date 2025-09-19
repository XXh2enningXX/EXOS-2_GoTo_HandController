# lookup.py

def hx(s: str) -> bytes:
    """Hilfsfunktion: Wandelt '55 AA 01 04 ...' in Bytes um"""
    return bytes.fromhex(s)

# -----------------------------------------------------------
# Geschwindigkeitswerte für g_bMountType == 1
# -----------------------------------------------------------
SPEED_MAP = {
    0:  "00 00",  # STOP
    1:  "00 05",  # 1x
    2:  "00 0A",  # 2x
    3:  "00 28",  # 8x
    4:  "00 A0",  # 16x
    5:  "01 40",  # 64x
    6:  "02 80",  # 128x
    7:  "05 00",  # 256x
    8:  "0A 00",  # 512x
    9:  "0A 00",  # MAX (=512x)
}

# -----------------------------------------------------------
# Frame-Generator
# -----------------------------------------------------------
def make_frame(axis: str, speed: int) -> bytes:
    """
    axis: 'ra' oder 'dec'
    speed: positives int = forward, negatives int = backward
    Rückgabe: 8-Byte Frame
    """
    header = "55 AA 01 04"
    if axis == "ra":
        axis_code = "01"
    elif axis == "dec":
        axis_code = "21"
    else:
        raise ValueError("Ungültige Achse (nur 'ra' oder 'dec')")

    if speed >= 0:
        dir_code = "00"  # forward
    else:
        dir_code = "01"  # backward

    speed_val = SPEED_MAP.get(abs(speed))
    if not speed_val:
        raise ValueError(f"Ungültige Geschwindigkeit: {speed}")

    frame_str = f"{header} {axis_code} {dir_code} {speed_val}"
    return hx(frame_str)

# -----------------------------------------------------------
# Lookup-Tabellen (z. B. CMD_RA["+1"], CMD_RA["-1"])
# -----------------------------------------------------------
CMD_RA = {str(s): make_frame("ra", s) for s in range(-9, 10) if s != 0}
CMD_RA["0"] = make_frame("ra", 0)

CMD_DEC = {str(s): make_frame("dec", s) for s in range(-9, 10) if s != 0}
CMD_DEC["0"] = make_frame("dec", 0)

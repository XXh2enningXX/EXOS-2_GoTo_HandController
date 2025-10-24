# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 17:52:16 2025

@author: Henning
"""
"""
parse_ra_only.py — liest eine Logdatei und zeigt nur RA-Statusantworten an.
Format (vom Pico):
t_ms KIND HEX...
"""

import numpy as np

LOGFILE = "ra_dec_log_1761065951.txt"   # <--- Dateinamen anpassen!

def parse_ra_status(path):
    ra_times = []
    ra_frames = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Wir suchen Zeilen, die so beginnen:
            # 1234567890 RX 55 AA 01 01 04 ...
            if "RX 55 AA 01 01 04" in line:
                parts = line.split()
                if len(parts) < 7:
                    continue
                try:
                    t_ms = int(parts[0])
                except ValueError:
                    continue
                # Rest in Bytes umwandeln
                frame_hex = "".join(parts[2:])  # alles nach t_ms + KIND
                try:
                    frame_bytes = bytes.fromhex(frame_hex)
                except ValueError:
                    continue
                ra_times.append(t_ms)
                ra_frames.append(frame_bytes)

    if not ra_times:
        print("Keine RA-Statusantworten gefunden.")
        return None, None

    # In NumPy-Array umwandeln
    maxlen = max(len(b) for b in ra_frames)
    data = np.zeros((len(ra_frames), maxlen), dtype=np.uint8)
    for i, b in enumerate(ra_frames):
        data[i, :len(b)] = np.frombuffer(b, dtype=np.uint8)

    times = np.array(ra_times, dtype=np.uint64)
    return times, data


if __name__ == "__main__":
    times, data = parse_ra_status(LOGFILE)
    if times is not None:
        print(f"{len(times)} RA-Antworten geladen aus {LOGFILE}")
        print("Erste 5 Einträge:")
        for i in range(min(5, len(times))):
            print(f"{times[i]:10d} ms :", " ".join(f"{x:02X}" for x in data[i, :8]))

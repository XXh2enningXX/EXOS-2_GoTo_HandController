# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 17:25:42 2025

@author: Henning
"""
"""
parse_logs.py — liest RA/DEC-Logdateien vom Pico und gibt NumPy-Arrays zurück.

Dateiformat (vom Pico erzeugt):
# t_ms KIND HEX
0000123456 TX 55 AA 01 01 04
0000123478 RX 55 AA 01 04 24 00 7F 02
...
"""

import numpy as np
import glob

def parse_log_file(path):
    """
    Liest eine einzelne Logdatei und gibt ein strukturiertes NumPy-Array zurück.
    dtype:
        [('t_ms','u8'), ('kind','U2'), ('frame','U200'), ('bytes','u1', Nmax)]
    """
    times = []
    kinds = []
    frames = []
    bytes_list = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            t_ms = int(parts[0])
            kind = parts[1]
            frame_hex = " ".join(parts[2:])
            try:
                frame_bytes = bytes.fromhex("".join(parts[2:]))
            except ValueError:
                continue
            times.append(t_ms)
            kinds.append(kind)
            frames.append(frame_hex)
            bytes_list.append(frame_bytes)

    # längstes Paket finden → Array fester Breite anlegen
    maxlen = max(len(b) for b in bytes_list) if bytes_list else 0
    byte_arr = np.zeros((len(bytes_list), maxlen), dtype=np.uint8)
    for i, b in enumerate(bytes_list):
        byte_arr[i, :len(b)] = np.frombuffer(b, dtype=np.uint8)

    dtype = np.dtype([
        ('t_ms', np.uint64),
        ('kind', 'U2'),
        ('frame', 'U200'),
    ])
    meta = np.empty(len(times), dtype=dtype)
    meta['t_ms'] = times
    meta['kind'] = kinds
    meta['frame'] = frames

    return meta, byte_arr


def load_all_logs(pattern="ra_dec_log_*.txt"):
    """
    Liest alle passenden Logs im aktuellen Ordner und gibt eine Liste zurück.
    Jeder Eintrag: (filename, meta_array, byte_array)
    """
    logs = []
    for path in sorted(glob.glob(pattern)):
        meta, data = parse_log_file(path)
        logs.append((path, meta, data))
        print(f"{path}: {len(meta)} Frames geladen.")
    return logs


if __name__ == "__main__":
    # Beispielnutzung
    logs = load_all_logs()
    if logs:
        fname, meta, data = logs[-1]
        print(f"\nBeispiel aus {fname}:")
        print(meta[:5])           # erste 5 Zeilen
        print(data[:5])           # Rohbytes
    else:
        print("Keine Logdateien gefunden.")

# parse_all_spyder.py — Alle Logfiles einlesen, RA/DEC extrahieren, plotten
# Direkt in Spyder ausführbar.

import os
import glob
import numpy as np
import matplotlib.pyplot as plt

# ===== Einstellungen ======================================================
GLOB_PATTERN = "ra_dec_log_*.txt"  # alle passenden Logs
SIGNED = False     # True -> 24-bit signed (2er-Komplement)
UNWRAP = True      # True -> Wraps über 2^24 glätten
SAVE_COMBINED_CSV = None  # z.B. "combined_ra_dec.csv" oder None, um nicht zu speichern
# ==========================================================================

def parse_header_speeds(path):
    """Liest Zeile 2 und extrahiert RA_SPEED und DEC_SPEED, falls vorhanden."""
    ra_spd = dec_spd = None
    try:
        with open(path, "r") as f:
            first = f.readline()
            second = f.readline()
            if second.startswith("#"):
                # Format erwartet: "# RA_SPEED=X  DEC_SPEED=Y  ..."
                text = second.strip("# \n")
                parts = text.replace("  ", " ").split()
                for p in parts:
                    if p.startswith("RA_SPEED="):
                        ra_spd = p.split("=",1)[1]
                    elif p.startswith("DEC_SPEED="):
                        dec_spd = p.split("=",1)[1]
    except Exception:
        pass
    return ra_spd, dec_spd

def parse_ra_dec_from_file(path, signed=False):
    """
    Extrahiert aus einer Datei:
      - RA: payload[0]==0x04
      - DEC: payload[0]==0x24
    Es werden nur RX-Frames berücksichtigt. Die letzten 3 Payload-Bytes bilden den 24-Bit-Wert.
    Rückgabe:
      (times_ra, vals_ra), (times_dec, vals_dec)
    """
    t_ra, v_ra = [], []
    t_dec, v_dec = [], []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 4 or parts[1] != "RX":
                continue

            # Bytes zusammenfügen (alles ab Spalte 2)
            hex_joined = "".join(parts[2:])
            try:
                frame = bytes.fromhex(hex_joined)
            except ValueError:
                continue

            # minimal prüfen: 55 AA 01 <len> ...
            if len(frame) < 5 or frame[0] != 0x55 or frame[1] != 0xAA or frame[2] != 0x01:
                continue
            L = frame[3]
            if 4 + L > len(frame):
                # inkonsistent/unvollständig
                continue
            payload = frame[4:4+L]
            if len(payload) < 4:
                continue

            pid = payload[0]  # 0x04 = RA, 0x24 = DEC
            status_bytes = payload[-3:]  # letzte 3 Bytes
            raw = int.from_bytes(status_bytes, byteorder="little", signed=False)
            if signed and (raw & 0x800000):
                raw -= 0x1000000  # 2^24

            try:
                t_ms = int(parts[0])
            except ValueError:
                continue

            if pid == 0x04:
                t_ra.append(t_ms); v_ra.append(raw)
            elif pid == 0x24:
                t_dec.append(t_ms); v_dec.append(raw)

    T_ra = np.asarray(t_ra, dtype=np.uint64)
    V_ra = np.asarray(v_ra, dtype=np.int64 if signed else np.uint32)
    T_dec = np.asarray(t_dec, dtype=np.uint64)
    V_dec = np.asarray(v_dec, dtype=np.int64 if signed else np.uint32)
    return (T_ra, V_ra), (T_dec, V_dec)

def unwrap_24bit(vals):
    """Entwrappt 24-bit Zähler (0..2^24-1) zu einer stetigen Kurve."""
    if vals.size == 0:
        return vals.astype(np.int64)
    MOD = 1 << 24
    vals = vals.astype(np.int64)
    diffs = np.diff(vals)
    wraps_up   = diffs < -(MOD // 2)
    wraps_down = diffs >  (MOD // 2)
    corr = np.zeros_like(vals, dtype=np.int64)
    k = 0
    for i in range(1, len(vals)):
        if wraps_up[i-1]:
            k += MOD
        elif wraps_down[i-1]:
            k -= MOD
        corr[i] = k
    return vals + corr

# ===== Einlesen aller Dateien ============================================
files = sorted(glob.glob(GLOB_PATTERN))
if not files:
    print("Keine Dateien gefunden für Muster:", GLOB_PATTERN)

all_series_ra = []   # Liste: (fname, ra_speed, dec_speed, times, values)
all_series_dec = []  # Liste: (fname, ra_speed, dec_speed, times, values)

for path in files:
    ra_spd, dec_spd = parse_header_speeds(path)
    (T_ra, V_ra), (T_dec, V_dec) = parse_ra_dec_from_file(path, signed=SIGNED)

    if T_ra.size:
        V_ra_plot = unwrap_24bit(V_ra) if (UNWRAP and not SIGNED) else V_ra.astype(np.int64)
        all_series_ra.append((os.path.basename(path), ra_spd, dec_spd, T_ra, V_ra_plot))
    if T_dec.size:
        V_dec_plot = unwrap_24bit(V_dec) if (UNWRAP and not SIGNED) else V_dec.astype(np.int64)
        all_series_dec.append((os.path.basename(path), ra_spd, dec_spd, T_dec, V_dec_plot))

print(f"Eingelesen: {len(files)} Dateien")
print(f"RA-Serien:  {len(all_series_ra)} | DEC-Serien: {len(all_series_dec)}")

# ===== Optional: kombinierte CSV speichern ===============================
if SAVE_COMBINED_CSV:
    # CSV mit Spalten: file, axis, RA_SPEED, DEC_SPEED, t_ms, value
    import csv
    with open(SAVE_COMBINED_CSV, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "axis", "RA_SPEED", "DEC_SPEED", "t_ms", "value"])
        for fname, ra_spd, dec_spd, T, V in all_series_ra:
            for t, v in zip(T, V):
                w.writerow([fname, "RA", ra_spd, dec_spd, int(t), int(v)])
        for fname, ra_spd, dec_spd, T, V in all_series_dec:
            for t, v in zip(T, V):
                w.writerow([fname, "DEC", ra_spd, dec_spd, int(t), int(v)])
    print("Gespeichert:", SAVE_COMBINED_CSV)

# ===== Plotten: getrennte Plots für RA und DEC ===========================
if all_series_ra:
    plt.figure('RA', figsize=(9,4))
    for fname, ra_spd, dec_spd, T, V in all_series_ra:
        label = f"{fname} (RA={ra_spd}, DEC={dec_spd})"
        plt.plot(V, ".", lw=1, label=label)
    plt.title("RA-Status (24-bit{} )".format(", unwrapped" if (UNWRAP and not SIGNED) else ""))
    plt.xlabel("Zeit [ms]")
    plt.ylabel("RA Wert")
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()

if all_series_dec:
    plt.figure('DEC', figsize=(9,4))
    for fname, ra_spd, dec_spd, T, V in all_series_dec:
        label = f"{fname} (RA={ra_spd}, DEC={dec_spd})"
        plt.plot(V, ".", lw=1, label=label)
    plt.title("DEC-Status (24-bit{} )".format(", unwrapped" if (UNWRAP and not SIGNED) else ""))
    plt.xlabel("Zeit [ms]")
    plt.ylabel("DEC Wert")
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()

if all_series_ra or all_series_dec:
    plt.show()
else:
    print("Keine RA/DEC-Daten zum Plotten gefunden.")

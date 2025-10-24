# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 19:56:36 2025

@author: Henning
"""
# parse_all_angles_spyder.py — Alle Logs laden, RA/DEC in Winkel (Grad) umrechnen & plotten

import os, glob
import numpy as np
import matplotlib.pyplot as plt

# ===== Einstellungen ======================================================
GLOB_PATTERN = "ra_dec_log_*.txt"
SIGNED = False          # True -> 24-bit signed interpretieren
UNWRAP = True           # Unwrap für 24-bit Zähler
COUNTS_PER_ARCSEC = 2.55  # deine Kalibrierung
ZERO_REF = "first"      # "first" = erster Wert je Datei als Null; oder Zahl (Counts)
SAVE_COMBINED_CSV = None  # z.B. "combined_angles.csv" (optional)
# ==========================================================================

def parse_header_speeds(path):
    ra_spd = dec_spd = None
    try:
        with open(path, "r") as f:
            f.readline()
            second = f.readline()
        if second.startswith("#"):
            txt = second.strip("# \n").replace("  ", " ")
            for p in txt.split():
                if p.startswith("RA_SPEED="):  ra_spd  = p.split("=",1)[1]
                if p.startswith("DEC_SPEED="): dec_spd = p.split("=",1)[1]
    except Exception:
        pass
    return ra_spd, dec_spd

def parse_ra_dec_from_file(path, signed=False):
    t_ra, v_ra, t_dec, v_dec = [], [], [], []
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"): continue
            parts = s.split()
            if len(parts) < 4 or parts[1] != "RX": continue
            try:
                frame = bytes.fromhex("".join(parts[2:]))
            except ValueError:
                continue
            if len(frame) < 5 or frame[0]!=0x55 or frame[1]!=0xAA or frame[2]!=0x01: continue
            L = frame[3]
            if 4+L > len(frame): continue
            payload = frame[4:4+L]
            if len(payload) < 4: continue
            pid = payload[0]         # 0x04=RA, 0x24=DEC
            status = payload[-3:]    # letzte 3 Bytes
            raw = int.from_bytes(status, "little", signed=False)
            if signed and (raw & 0x800000):
                raw -= 0x1000000
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
    if vals.size == 0: return vals.astype(np.int64)
    MOD = 1<<24
    vals = vals.astype(np.int64)
    diffs = np.diff(vals)
    wraps_up   = diffs < -(MOD//2)
    wraps_down = diffs >  (MOD//2)
    corr = np.zeros_like(vals, dtype=np.int64)
    k = 0
    for i in range(1, len(vals)):
        if wraps_up[i-1]:   k += MOD
        elif wraps_down[i-1]: k -= MOD
        corr[i] = k
    return vals + corr

def counts_to_deg(vals_counts, zero_mode="first", counts_per_arcsec=2.55):
    vals = vals_counts.astype(np.int64)
    if isinstance(zero_mode, (int, float)):
        ref = zero_mode
    elif zero_mode == "first":
        ref = vals[0] if vals.size else 0
    else:
        ref = 0
    dcounts = vals - ref
    arcsec = dcounts / counts_per_arcsec
    deg = arcsec / 3600.0
    return deg

# ===== Einlesen & Umrechnung =============================================
files = sorted(glob.glob(GLOB_PATTERN))
if not files:
    print("Keine Dateien für", GLOB_PATTERN)

series_ra = []   # (fname, ra_spd, dec_spd, T, deg)
series_dec = []  # (fname, ra_spd, dec_spd, T, deg)

for path in files:
    ra_spd, dec_spd = parse_header_speeds(path)
    (T_ra, V_ra), (T_dec, V_dec) = parse_ra_dec_from_file(path, signed=SIGNED)
    if T_ra.size:
        V_ra2 = unwrap_24bit(V_ra) if (UNWRAP and not SIGNED) else V_ra.astype(np.int64)
        deg_ra = counts_to_deg(V_ra2, ZERO_REF, COUNTS_PER_ARCSEC)
        series_ra.append((os.path.basename(path), ra_spd, dec_spd, T_ra, deg_ra))
    if T_dec.size:
        V_dec2 = unwrap_24bit(V_dec) if (UNWRAP and not SIGNED) else V_dec.astype(np.int64)
        deg_dec = counts_to_deg(V_dec2, ZERO_REF, COUNTS_PER_ARCSEC)
        series_dec.append((os.path.basename(path), ra_spd, dec_spd, T_dec, deg_dec))

print(f"Eingelesen: {len(files)} Dateien")
print(f"Serien: RA={len(series_ra)}  DEC={len(series_dec)}")

# ===== Optional: kombinierte CSV speichern ===============================
if SAVE_COMBINED_CSV:
    import csv
    with open(SAVE_COMBINED_CSV, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file","axis","RA_SPEED","DEC_SPEED","t_ms","deg"])
        for fname, ra_spd, dec_spd, T, D in series_ra:
            for t, d in zip(T, D): w.writerow([fname,"RA",ra_spd,dec_spd,int(t),float(d)])
        for fname, ra_spd, dec_spd, T, D in series_dec:
            for t, d in zip(T, D): w.writerow([fname,"DEC",ra_spd,dec_spd,int(t),float(d)])
    print("Gespeichert:", SAVE_COMBINED_CSV)

# ===== Plotten ============================================================
if series_ra:
    plt.figure('RA', figsize=(9,4))
    for fname, ra_spd, dec_spd, T, D in series_ra:
        label = f"{fname} (RA={ra_spd}, DEC={dec_spd})"
        plt.plot(T, D, ".", lw=1, label=label)
    plt.title("RA-Winkel (Grad, relativ zum ersten Wert)")
    plt.xlabel("Zeit [ms]"); plt.ylabel("RA [deg]")
    plt.grid(True, alpha=0.3); plt.legend(fontsize=8); plt.tight_layout()

if series_dec:
    plt.figure('DEC', figsize=(9,4))
    for fname, ra_spd, dec_spd, T, D in series_dec:
        label = f"{fname} (RA={ra_spd}, DEC={dec_spd})"
        plt.plot(T, D, ".", lw=1, label=label)
    plt.title("DEC-Winkel (Grad, relativ zum ersten Wert)")
    plt.xlabel("Zeit [ms]"); plt.ylabel("DEC [deg]")
    plt.grid(True, alpha=0.3); plt.legend(fontsize=8); plt.tight_layout()

if series_ra and series_dec:
    plt.figure('RA DEC', figsize=(9,4))
    for fname, ra_spd, dec_spd, T, D in series_ra:
        label = f"{fname} (RA={ra_spd}, DEC={dec_spd})"
        plt.plot(T, D, ".", lw=1, label=label)
    for fname, ra_spd, dec_spd, T, D in series_dec:
        label = f"{fname} (RA={ra_spd}, DEC={dec_spd})"
        plt.plot(T, D, ".", lw=1, label=label)
    plt.title("DEC-Winkel (Grad, relativ zum ersten Wert)")
    plt.xlabel("Zeit [ms]"); plt.ylabel("DEC [deg]")
    plt.grid(True, alpha=0.3); plt.legend(fontsize=8); plt.tight_layout()

if series_ra or series_dec:
    plt.show()
else:
    print("Keine Daten zum Plotten.")

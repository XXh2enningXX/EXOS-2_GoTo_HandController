# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 23:16:28 2025

@author: Henning
"""
#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Pfad zur CSV-Datei – passe den Pfad bei Bedarf an
    file_path = "NewFile3.csv"  # Stelle sicher, dass sich die Datei im gleichen Verzeichnis befindet

    # CSV-Datei laden: Annahme, dass sie keine Header enthält.
    # Jede Zeile wird in zwei Werte aufgeteilt: Index und Voltage.
    try:
        df = pd.read_csv(file_path, sep=",", usecols=[0, 1], header=2, names=["Index", "Voltage"])
    except Exception as e:
        print(f"Fehler beim Laden der Datei: {e}")
        return

    # Sicherstellen, dass Voltage numerisch ist
    df["Voltage"] = pd.to_numeric(df["Voltage"], errors="coerce")
    df = df.dropna().reset_index(drop=True)

    # Setze einen Schwellenwert um HIGH und LOW zu unterscheiden
    # Beispiel: Alle Werte > 2.5V sind HIGH, sonst LOW.
    threshold = 2.5
    df["State"] = (df["Voltage"] > threshold).astype(int)

    # Erzeuge eine Spalte, die Flankenwechsel erkennt:
    # diff() berechnet den Unterschied zwischen aufeinanderfolgenden Zuständen
    # Ein Sprung von 1 auf 0 liefert -1 (Falling Edge) und von 0 auf 1 +1 (Rising Edge)
    df["Edge"] = df["State"].diff().fillna(0).astype(int)

    # Zeit pro Sample: hier 5 µs
    sample_time_us = 5
    df["Time_us"] = df["Index"] * sample_time_us

    # Analysiere Low-Pegel-Dauern:
    # Wir gehen Zeile für Zeile: Speichern den Zeitpunkt beim Falling Edge (High to Low)
    # und beim nächsten Rising Edge berechnen wir die Dauer des Low-Pegels.
    low_durations = []
    low_start_time = None
    for i, row in df.iterrows():
        # Wenn es ein Falling Edge ist, starten wir die Low-Periode
        if row["Edge"] == -1:
            low_start_time = row["Time_us"]
        # Wenn es ein Rising Edge ist und wir zuvor einen Low-Start hatten, berechnen wir die Dauer
        elif row["Edge"] == 1 and low_start_time is not None:
            duration = row["Time_us"] - low_start_time
            low_durations.append(duration)
            low_start_time = None

    # Ausgabe einiger Statistiken zur Low-Dauer
    if low_durations:
        print("Erste 10 Low-Pegel-Dauern (in µs):")
        for d in low_durations[:10]:
            print(d)
        print(f"Min Low-Dauer: {min(low_durations)} µs")
        print(f"Max Low-Dauer: {max(low_durations)} µs")
        print(f"Durchschnittliche Low-Dauer: {sum(low_durations) / len(low_durations):.2f} µs")
    else:
        print("Es wurden keine Low-Pegel-Dauern erkannt.")

    # Optional: Diagramm der Spannungsverläufe und erkannten Flanken anzeigen.
    plt.figure('timeline', figsize=(12, 6))
    plt.clf()
    plt.plot(df["Time_us"], df["Voltage"], label="Spannung (V)")
    plt.xlabel("Zeit (µs)")
    plt.ylabel("Spannung (V)")
    plt.title("Oszilloskop-Daten")
    # Markiere die Flankenwechsel:
    rising_edges = df[df["Edge"] == 1]
    falling_edges = df[df["Edge"] == -1]
    plt.scatter(rising_edges["Time_us"], rising_edges["Voltage"], color="green", label="Rising Edge", marker="^")
    plt.scatter(falling_edges["Time_us"], falling_edges["Voltage"], color="red", label="Falling Edge", marker="v")
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.figure('low durations')
    plt.clf()
    plt.plot(low_durations)
    plt.show()
    
    

if __name__ == "__main__":
    df = main()

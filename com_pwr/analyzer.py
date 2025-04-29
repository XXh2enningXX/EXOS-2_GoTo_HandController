# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 21:40:09 2025

@author: Henning
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import groupby

# [file, axis, speed]
speed_1_ra = ["move_ra_sp1.csv", "RA", 1]
speed_2_ra = ["move_ra_sp2.csv", "RA", 2]
speed_1_dec = ["move_dec_sp1.csv", "DEC", 1]
speed_2_dec = ["move_dec_sp2.csv", "DEC", 2]

files = [speed_1_ra, speed_2_ra, speed_1_dec, speed_2_dec]

# fname = "move_ra_sp1.csv"

df_ch0 = pd.DataFrame()
df_ch1 = pd.DataFrame()

# def codiert(time):
#     baud = 9600
#     t_base = 1/baud
#     n_int = int(round(time/t_base, 2))
#     code = n_int
#     # if code > 10:
#     #     code = 10
#     return code

def codiert(time):
    baud = 9600
    t_base = 1/baud
    n_int = int(round(time/t_base, 2))
    code = n_int
    # if code > 10:
    #     code = 10
    return code

# Dateien einlesen
for measure in files:
    fname = measure[0]
    axis = measure[1]
    speed = measure[2]

    name = axis + "_speed_" + str(speed)

    df = pd.read_csv(fname, header=1, names=["time", "ch0", "ch1"])
    df.dropna(inplace=True)
    
    # plot time line
    fig, axs = plt.subplots(2, num = 'time sequence ' + fname, sharex=True)
    fig.suptitle('Digitalsignale')
    axs[0].plot(df["time"], df["ch0"], label="Kanal 0", drawstyle="steps-post")
    axs[0].grid()
    axs[1].plot(df["time"], df["ch1"], label="Kanal 1", drawstyle="steps-post")
    axs[1].grid()

    # ▓▓▓ Fallende Flanken CH0 ▓▓▓
    falling_ch0 = df[(df["ch0"].shift(1) == 1) & (df["ch0"] == 0)].copy()
    falling_ch0["interval_us"] = falling_ch0["time"].diff()
    falling_ch0["interval_us"].iloc[0] = 0.000208#falling_ch0["time"].iloc[0]
    fall_df_ch0 = falling_ch0[["time", "interval_us"]].reset_index()
    fall_df_ch0["code"]=fall_df_ch0["interval_us"].apply(codiert)
    fall_df_ch0["code time"]=fall_df_ch0["code"].cumsum()
    
    df_ch0[name + "_code"] = fall_df_ch0["code"].apply(lambda a: a - 2)
    df_ch0[name + "_code_time"] = fall_df_ch0["code time"]

    # ▓▓▓ Fallende Flanken CH1 ▓▓▓
    falling_ch1 = df[(df["ch1"].shift(1) == 1) & (df["ch1"] == 0)].copy()
    falling_ch1["interval_us"] = falling_ch1["time"].diff().fillna(0)
    falling_ch1["interval_us"].iloc[0] = 0.000208#falling_ch1["time"].iloc[0]
    fall_df_ch1 = falling_ch1[["time", "interval_us"]].reset_index()
    fall_df_ch1["code"]=fall_df_ch1["interval_us"].apply(codiert)
    fall_df_ch1["code time"]=fall_df_ch1["code"].cumsum()
    
    df_ch1[name + "_code"] = fall_df_ch1["code"].apply(lambda a: a - 2)
    df_ch1[name + "_code_time"] = fall_df_ch1["code time"]


    plt.figure(name + 'code', figsize=(12, 4))
    plt.clf()
    plt.plot(df_ch0[name+"_code_time"],df_ch0[name+"_code"], label="Kanal 0", drawstyle="steps-post", alpha=0.6)
    # plt.plot(fall_df_ch1["code time"][26:].to_numpy(),fall_df_ch1["code"][26:].to_numpy(), label="Kanal 1", drawstyle="steps-post", alpha=0.6)
    plt.title("Digitalsignale")
    plt.xlabel("index")
    plt.ylabel("value")
    plt.ylim(-1, 10)
    # plt.xlim(92,281)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()





#!/usr/bin/env python3

import pandas as pd
import os.path as path
from volley_elo import ELO_TEAMS_DIR
import matplotlib.pyplot as plt


def get_elo_df(year):
    fpath = path.join(ELO_TEAMS_DIR, "volley-{}-{}-elo.csv".format(year, year + 1))
    return pd.read_csv(fpath)


def plot_elo(year):
    df = get_elo_df(year)
    plt.style.use("seaborn-darkgrid")

    fig = plt.figure()
    ax = plt.gca()

    df["date"] = pd.to_datetime(df["date"])

    for name, group in df.groupby("name"):
        group.plot(label=name, x="date", y="elo", ax=ax)

    plt.title("Elo rankings for 20{}-{} season".format(year, year + 1))
    plt.axhline(1500, color="k", linestyle="--", label='"Average"')
    plt.legend()
    plt.show()

#!/usr/bin/env python3

import pandas as pd
import os.path as path
from volley_elo import ELO_TEAMS_DIR, ELO_MATCH_DIR
import matplotlib.pyplot as plt


def get_elo_df(year):
    fpath = path.join(ELO_TEAMS_DIR, "volley-{}-{}-elo.csv".format(year, year + 1))
    return pd.read_csv(fpath)


def get_match_df(year):
    fpath = path.join(ELO_MATCH_DIR, "volley-{}-{}-elo.csv".format(year, year + 1))
    df = pd.read_csv(fpath)
    df["home-won"] = df["home-score"] == 3
    return df


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


def brier_score(df, result_col, predict_col):
    """
    Calculate a modified Brier score given a dataframe with results and
    probability predictions.

    Idea stolen from 538's NFL Elo game.

    Gist:

        Brier scores are in [0, 1], with 0 being the best and 1 being the
        worst. That's a terrible idea for a "score."

        Flip it so that 1 is the best and 0 is the worst, then scale everything
        to lie in [0, 100]. Say that you only get points if you're in the top
        25%, otherwise you lose points. In other words, subtract 75 from the
        result.
    """
    return 100 * (1 - (df[result_col] - df[predict_col])**2) - 75

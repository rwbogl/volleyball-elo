#!/usr/bin/env python3

from volley_elo import ELO_TEAMS_DIR, ELO_MATCH_DIR
import os.path as path
import seaborn as sns
import pandas as pd


def get_elo_df(year):
    fpath = path.join(ELO_TEAMS_DIR, "volley-{}-{}-elo.csv".format(year, year + 1))
    return pd.read_csv(fpath)


def get_match_df(year):
    fpath = path.join(ELO_MATCH_DIR, "volley-{}-{}-elo.csv".format(year, year + 1))
    df = pd.read_csv(fpath)
    df["home_won"] = df["home_score"] == 3
    return df


def plot_elo(year, ax):
    df = get_elo_df(year)
    df["date"] = pd.to_datetime(df["date"])

    for name, group in df.groupby("name"):
        plot = sns.lineplot(label=name, x="date", y="elo", ax=ax, legend=False, data=group, err_style="band")

    match_df = get_match_df(year)
    match_df["date"] = pd.to_datetime(match_df["date"])

    postseason_df = match_df[match_df.postseason]
    if not postseason_df.empty:
        print(postseason_df.iloc[0].date)
        ax.axvline(postseason_df.iloc[0].date, color="k", label="Postseason")

    ax.set_title("Elo rankings for 20{}-{} season".format(year, year + 1))
    ax.axhline(1500, color="k", linestyle="--", label='"Average"')
    return plot


def brier_score(df, result_col, predict_col):
    """
    Calculate a modified Brier score given a dataframe with results and
    probability predictions.

    Idea stolen from 538's NFL Elo game.

    Gist:

        Brier scores are in [0, 1], with 0 being the best and 1 being the
        worst. That's a terrible idea for a "score."

        Flip it so that 1 is the best and 0 is the worst, then linearly scale
        everything to lie in [0, 100]. We want to say that a prediction of 1 /
        2 gives you zero points, and we'll achieve this by an additive shift.
        Thus:

                100 (1 - (1 / 2)^2) + c = 0
                                      c = -75.

        We subtract off 75 points. So, bets near 50/50 will get nearly nothing,

    """
    return 100 * (1 - (df[result_col] - df[predict_col])**2) - 75


def plot_brier(df, result_col, predict_col, ax):
    """TODO: Docstring for plot_brier.

    :year: TODO
    :returns: TODO

    """
    df["brier"] = brier_score(df, result_col, predict_col)

    df["brier"].cumsum().plot(label=predict_col, ax=ax)
    df["brier"].cumsum().rolling(7).mean().plot(label="", ax=ax)
    df["bpos"] = df["brier"] > 0
    # df["brier"].plot.bar(color=df["bpos"].map({True: "C2", False: "C1"}), ax=ax)

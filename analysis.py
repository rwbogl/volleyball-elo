#!/usr/bin/env python3

from volley_elo import ELO_TEAMS_DIR, ELO_MATCH_DIR, team_elo_df
import os.path as path
import pandas as pd


def get_elo_df(year):
    fpath = path.join(ELO_TEAMS_DIR, "volley-{}-{}-elo.csv".format(year, year + 1))
    return pd.read_csv(fpath)


def get_match_df(year):
    fpath = path.join(ELO_MATCH_DIR, "volley-{}-{}-elo.csv".format(year, year + 1))
    df = pd.read_csv(fpath)
    df["home_won"] = df["home_score"] == 3
    return df


def plot_elo(match_df, ax, elo_name="elo", teams=None, add_markers=True):
    """Plot an Elo time-series on the given axis for the given teams.

    :match_df: A match dataframe.
    :ax: Matplotlib axis.
    :elo_name: Name that the elo columns in `match_df`.
    :teams: A list of team names to plot, or None if all teams should be plotted.
    :add_markers: Add postseason and average markers.

    `add_markers` is useful if you want to plot multiple versions of Elo in the
    same plot. You wouldn't want duplicate labels of the postseason and average
    markers cluttering up the legend. (There are other solutions, but now you
    can use this one if you like.)
    """
    year = match_df.iloc[0].date.year
    df = team_elo_df(match_df, elo_name=elo_name)

    if teams:
        df = df[teams]

    df.plot(marker="o", lw=3, ax=ax, legend=False)

    ax.set_title("Elo rankings for {}-{} season".format(year, year + 1))

    if add_markers:
        ax.axhline(1500, color="k", linestyle="--", label='"Average"')

        postseason_df = match_df[match_df.postseason]
        if not postseason_df.empty:
            ax.axvline(postseason_df.iloc[0].date, color="k", label="Postseason")


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
    col = brier_score(df, result_col, predict_col)

    col.cumsum().plot(label=predict_col, ax=ax, lw=3, marker="o")
    col.cumsum().rolling(7).mean().plot(label=predict_col + " rolling average", ax=ax, lw=3, alpha=0.8)


if __name__ == "__main__":
    import volley_elo
    import matplotlib.pyplot as plt
    dfs = {year: volley_elo.get_historical_df(year) for year in range(12, 20)}
    volley_elo.record_seasons(list(dfs.values()))
    volley_elo.record_seasons(list(dfs.values()), K=100, elo_name="big-elo")
    plt.figure()
    plot_elo(dfs[19], plt.gca(), "elo", ["Birmingham-Southern"], add_markers=False)
    plot_elo(dfs[19], plt.gca(), "big-elo", ["Birmingham-Southern"], ["Big Elo BSC"])
    plt.legend(["Elo BSC", "Big Elo BSC", "Average", "Postseason"])
    plt.show()

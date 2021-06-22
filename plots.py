#!/usr/bin/env python3

from volley_elo import team_elo_df
from elo import brier_score


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


def plot_brier(df, result_col, predict_col, ax):
    """Plot Brier scores and a moving average for the given dataframe.

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

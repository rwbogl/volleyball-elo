#!/usr/bin/env python3

import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import matplotlib
import volley_elo
import analysis
import math
import pandas as pd
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze the Elo of women's volleyball teams.")
    parser.add_argument('start', metavar='start', type=int,
                        help='Two-digit year to start analysis.')
    parser.add_argument('stop', metavar='stop', type=int,
                        help='Two-digit year to stop analysis.')
    parser.add_argument('-K', type=int, nargs=1, default=40,
                        help='K-factor for Elo updating. Defaults to 40.')

    args = parser.parse_args()

    """
    I want to get rid of the record_seasons function. Or at least make it stop
    using goddamn CSV files.

    Plan:
        1. Read the historical match dataframes directly.
        2. Populate the match-Elo data using the thing in volley_elo.py.
        3. Derive the team_elo from that (just needs an extra row at the end,
           basically).

    This should get everything below working again.

    Okay, we're off to a good start. There's still another problem.

    Let me explain what I'd *like* to do:

        dfs = get_match_dfs(...)

        add_elo_columns(list(dfs.values()), start, stop, "base", elo_params)
        add_elo_columns(list(dfs.values()), start, stop, "new", different_elo_params)

        brier(..., "base_win_prob")
        brier(..., "new_win_prob")

    Okay, I think I've done what I wanted to, but I haven't modified the
    plotting below to use the full generality. I'm also not sure if
    record_seasons is exactly how I like it yet. But it's better than it was
    before, and that's something, at least.
    """
    dfs = {year: volley_elo.get_historical_df(year) for year in range(args.start, args.stop)}

    # Dictionary order is guaranteed to be in insertion order in 3.7+.
    volley_elo.record_seasons(list(dfs.values()))
    volley_elo.record_seasons(list(dfs.values()), K=100, elo_name="big-elo")
    volley_elo.record_seasons(list(dfs.values()), K=600, elo_name="massive-elo")
    volley_elo.record_seasons(list(dfs.values()), K=20, elo_name="small-elo")

    n_cols = 3
    n_rows = math.ceil((args.stop - args.start - 2) / float(n_cols))

    matplotlib.rc('xtick', labelsize=5)
    matplotlib.rc('ytick', labelsize=5)

    sns.set()
    fig, axes = plt.subplots(n_rows, n_cols)

    fig.tight_layout()

    for year in range(args.start + 2, args.stop):
        df = dfs[year]

        brier = analysis.brier_score(df, "home_won", "elo_win_prob")
        brier2 = analysis.brier_score(df, "home_won", "big-elo_win_prob")
        print("20{}-{} Brier score:".format(year, year + 1), brier.sum())
        print("20{}-{} Big Brier score:".format(year, year + 1), brier2.sum())
        # print("20{}-{} Brier description:".format(year, year + 1))
        # print(brier.describe())

        k = year - args.start - 2
        x, y = k // n_cols, k % n_cols
        analysis.plot_elo(df, ax=axes[x, y], elo_name="elo")
        # Too much going on at once.
        # analysis.plot_elo(df, ax=axes[x, y], elo_name="big-elo")
        axes[x, y].set_xlabel("")
        plt.sca(axes[x, y])
        plt.xticks(rotation=45)

    # Idea from: https://stackoverflow.com/a/46921590/6670539
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower right")

    # Brier score plots.
    for year in range(args.start + 2, args.stop):
        fig = plt.figure()
        df = dfs[year]
        df["random_choice"] = pd.DataFrame(np.random.randint(2, size=(len(df), 1)))
        df["record_predict"] = (df["home_wins"] >= df["away_wins"]).apply(int)

        analysis.plot_brier(df, "home_won", "elo_win_prob", ax=plt.gca())
        analysis.plot_brier(df, "home_won", "big-elo_win_prob", ax=plt.gca())
        analysis.plot_brier(df, "home_won", "small-elo_win_prob", ax=plt.gca())
        analysis.plot_brier(df, "home_won", "massive-elo_win_prob", ax=plt.gca())
        analysis.plot_brier(df, "home_won", "record_predict", ax=plt.gca())
        fig.legend(loc="center right")
        plt.title("Brier scores for 20{}-{} season".format(year, year + 1))

    plt.show()

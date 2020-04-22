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
    """
    dfs = volley_elo.record_seasons(args.start, args.stop, args.K, elo_suffix="base_elo")

    # This works right now, but only because we pregenerated the csv files in
    # an earlier commit. The plan is to get this all in dataframes in a later
    # commit.
    teams_df = analysis.get_elo_df(args.stop - 1)

    n_cols = 3
    n_rows = math.ceil((args.stop - args.start - 2) / float(n_cols))

    matplotlib.rc('xtick', labelsize=5)
    matplotlib.rc('ytick', labelsize=5)

    sns.set()
    fig, axes = plt.subplots(n_rows, n_cols)

    fig.tight_layout()

    for year in range(args.start + 2, args.stop):
        df = dfs[year]

        brier = analysis.brier_score(df, "home_won", "win_prob_base_elo")
        print("20{}-{} Brier score:".format(year, year + 1), brier.sum())
        print("20{}-{} Brier description:".format(year, year + 1))
        print(brier.describe())

        k = year - args.start - 2
        x, y = k // n_cols, k % n_cols
        analysis.plot_elo(year, ax=axes[x, y])
        axes[x, y].set_xlabel("")
        plt.sca(axes[x, y])
        plt.xticks(rotation=45)

    # Idea from: https://stackoverflow.com/a/46921590/6670539
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower right")

    # Brier score plots.
    for year in range(args.start + 2, args.stop):
        fig = plt.figure()
        df = analysis.get_match_df(args.stop - 2)
        df["random_choice"] = pd.DataFrame(np.random.randint(2, size=(len(df), 1)))
        df["record_predict"] = (df["home_wins"] >= df["away_wins"]).apply(int)

        analysis.plot_brier(df, "home_won", "elo_win_prob", ax=plt.gca())
        analysis.plot_brier(df, "home_won", "random_choice", ax=plt.gca())
        analysis.plot_brier(df, "home_won", "record_predict", ax=plt.gca())
        fig.legend()
        plt.title("Brier scores for 20{}-{} season".format(year, year + 1))

    plt.show()

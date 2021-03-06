#!/usr/bin/env python3

import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import matplotlib
import volley_elo
import plots
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
    parser.add_argument('-b', '--brier', type=bool, nargs=1, default=False,
                        help='Plot Brier scores.')

    args = parser.parse_args()

    dfs = {year: volley_elo.get_historical_df(year) for year in range(args.start, args.stop)}

    # Add Elo data to the dataframes.
    # (Dictionary order is guaranteed to be insertion order in 3.7+.)
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

    for year in range(args.start + 2, args.stop):
        df = dfs[year]

        brier = plots.brier_score(df, "home_won", "elo_win_prob")
        brier2 = plots.brier_score(df, "home_won", "big-elo_win_prob")
        print("20{}-{} Brier score:".format(year, year + 1), brier.sum())
        print("20{}-{} Big Brier score:".format(year, year + 1), brier2.sum())

        k = year - args.start - 2
        x, y = k // n_cols, k % n_cols
        plots.plot_elo(df, ax=axes[x, y], elo_name="elo")
        axes[x, y].set_xlabel("")
        plt.sca(axes[x, y])
        plt.xticks(rotation=45)

    # Add a single legend for the entire plot.
    # Idea from: https://stackoverflow.com/a/46921590/6670539
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower right")

    plt.subplots_adjust(wspace=0.32, hspace=0.49)

    # Brier score plots.
    if args.brier:
        for year in range(args.start + 2, args.stop):
            fig = plt.figure()
            df = dfs[year]
            df["random_choice"] = pd.DataFrame(np.random.randint(2, size=(len(df), 1)))
            df["record_predict"] = (df["home_wins"] >= df["away_wins"]).apply(int)

            plots.plot_brier(df, "home_won", "elo_win_prob", ax=plt.gca())
            plots.plot_brier(df, "home_won", "big-elo_win_prob", ax=plt.gca())
            plots.plot_brier(df, "home_won", "small-elo_win_prob", ax=plt.gca())
            plots.plot_brier(df, "home_won", "massive-elo_win_prob", ax=plt.gca())
            plots.plot_brier(df, "home_won", "record_predict", ax=plt.gca())
            fig.legend(loc="center right")
            plt.title("Brier scores for 20{}-{} season".format(year, year + 1))

    plt.show()

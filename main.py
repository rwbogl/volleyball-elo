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

    volley_elo.record_seasons(args.start, args.stop, args.K)

    teams_df = analysis.get_elo_df(args.stop - 1)

    n_cols = 3
    n_rows = math.ceil((args.stop - args.start - 2) / float(n_cols))

    matplotlib.rc('xtick', labelsize=5)
    matplotlib.rc('ytick', labelsize=5)

    sns.set()
    fig, axes = plt.subplots(n_rows, n_cols)

    fig.tight_layout()

    for year in range(args.start + 2, args.stop):
        match_df = analysis.get_match_df(year)
        brier = analysis.brier_score(match_df, "home-won", "elo-win-prob")
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
        df["record-predict"] = (df["home-wins"] >= df["away-wins"]).apply(int)

        analysis.plot_brier(df, "home-won", "elo-win-prob", ax=plt.gca())
        analysis.plot_brier(df, "home-won", "random_choice", ax=plt.gca())
        analysis.plot_brier(df, "home-won", "record-predict", ax=plt.gca())
        fig.legend()
        plt.title("Brier scores for 20{}-{} season".format(year, year + 1))

    plt.show()

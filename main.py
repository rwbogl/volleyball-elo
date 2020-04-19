#!/usr/bin/env python3

import argparse
import volley_elo
import analysis

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

    df = analysis.get_elo_df(args.stop - 1)

    analysis.plot_elo(args.stop - 1)

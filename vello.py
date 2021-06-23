#!/usr/bin/env python3

"""
Track Elo of a volleyball team.
"""

import os.path as path
import pandas as pd
import elo


def team_elo_df(match_df, elo_name="elo"):
    teams = dict()

    for k, row in match_df.iterrows():
        if row.home not in teams:
            teams[row.home] = dict()

        if row.away not in teams:
            teams[row.away] = dict()

        teams[row.home][row.date] = row["home_{}".format(elo_name)]
        teams[row.away][row.date] = row["away_{}".format(elo_name)]

    # Not every team plays on every day, so interpolate the gaps linearly.
    df = pd.DataFrame(teams).sort_index().interpolate(method="linear")

    # Sort the columns alphabetically so that legends are always consistent.
    return df.sort_index(axis=1)


def load_games(csv):
    df = pd.read_csv(csv)
    df["date"] = pd.to_datetime(df["date"])
    df["home_won"] = df["home_score"] == 3

    team_names = set(df.home) | set(df.away)
    teams = [elo.Team(name, 1500) for name in team_names]

    return teams, df


def record_games(match_df, teams, K=40, R=3, elo_name="elo", reset=False):
    """
    :dfs: A list of match dataframes, taken to be consecutive seasons.
    :K: K-factor for Elo updating.
    :R: Regression proportion; teams lose an Rth of their distance to 1500 Elo.
    :returns: Dataframe with Elo columns added. Also modifies `teams`.

    """
    if reset:
        for team in teams:
            team.elo = 1500

    last_seen = dict()
    teams = {team.name: team for team in teams}

    home_elo = []
    away_elo = []
    win_prob = []

    for match in match_df.itertuples():
        home = teams[match.home]
        away = teams[match.away]

        # Regress towards to mean for every 3 months you didn't play a
        # game.
        if match.home in last_seen:
            delta = match.date - last_seen[match.home]
            intervals = delta.days // (30 * 3)
            home.elo -= intervals * (home.elo - 1500) / R

        if match.away in last_seen:
            delta = match.date - last_seen[match.away]
            intervals = delta.days // (30 * 3)
            away.elo -= intervals * (away.elo - 1500) / R

        last_seen[match.home] = match.date
        last_seen[match.away] = match.date

        home_elo.append(home.elo)
        away_elo.append(away.elo)

        match = elo.Match(home, away, match.home_score, match.away_score, K=K)
        win_prob.append(match.win_prob)
        match.update_teams()

    update = pd.DataFrame({"home_{}".format(elo_name): home_elo,
                           "away_{}".format(elo_name): away_elo,
                           "{}_win_prob".format(elo_name): win_prob})

    return pd.concat([match_df, update], axis=1)

if __name__ == "__main__":
    teams, df = load_games("./data/results/games.csv")
    elo_df = record_games(df, teams)

#!/usr/bin/env python3

"""
Track Elo of a volleyball team through seasons.

Principles:
    - Given zero information, a team should start at 1500 Elo. In-season
      matches are handled by the logic in elo.py.

    - Given the Elo from a previous season, teams should be regressed towards
      the mean by some amount. (Perhaps cut a third of their distance away, or
      something like that.)

What's the desired output? Really, I want a dataframe. I want to do stuff like

    df["Oglethorpe"]["elo"]

Kind of a weak dataframe though. Just a fancy dictionary (that it totally worth
it to build, of course).

This is effectively a time-series. But...it isn't clear what the time units
are. Total games played? Too big. Games played by team? Not sure if every team
plays the same number of games. Weeks in the season? I don't know if that makes
sense for volleyball.

We could artifically break things into weeks. That would work.

After a quick perusal, it seems like everyone plays 14 games in the SAA, so we
can just record the results of every match for every team. Thus, say,

    df["Oglethorpe", "elo"]

would return the elo of OU for games 1 - 15.

This is a little misleading, though. A time series should represent actual
*time*. If I see a change occur in a graph before some other point, it should
have actually happened *before* that other point.

Okay, so just record the dates of the games along with the results. That way
you can graph things with respect to time later, if you want.
"""

import os.path as path
import pandas as pd
import elo

ELO_DIRECTORY = "data/elo/"
RECORD_DIRECTORY = "data/results"
ELO_TEAMS_DIR = path.join(ELO_DIRECTORY, "teams/")
ELO_MATCH_DIR = path.join(ELO_DIRECTORY, "matches/")
TEAMS_FIELDNAMES = ["name", "wins", "losses", "elo", "date"]
CONF_NAMES = ['Berry', 'Birmingham-Southern', 'Hendrix', 'Millsaps', 'Oglethorpe',
              'Centre', 'Sewanee', 'Rhodes']

TEAMS = {name: elo.Team(name, 1500) for name in CONF_NAMES}


def add_match_elo_columns(teams, df, name="elo", **kwargs):
    """Add Elo-related columns (home/away Elo, win-probability).

    :teams: TODO
    :df: TODO
    :**kwargs: TODO
    :returns: TODO

    Modifies `teams` unless `copy=True` is passed. Overwrites columns of `df`.

    """
    home_elo = []
    away_elo = []
    win_prob = []

    copy = kwargs.get("copy", False)

    if copy:
        teams = {name: elo.Team(name, team.elo) for name, team in teams.items()}

    for row in df.itertuples():
        home = teams[row.home]
        away = teams[row.away]

        home_elo.append(home.elo)
        away_elo.append(away.elo)

        match = elo.Match(home, away, row.home_score, row.away_score, **kwargs)
        win_prob.append(match.win_prob)
        match.update_teams()

    update = pd.DataFrame({"home_{}".format(name): home_elo,
                           "away_{}".format(name): away_elo,
                           "{}_win_prob".format(name): win_prob})

    for column in update.columns:
        df[column] = update[column]


def team_elo_df(match_df, elo_name="elo"):
    """TODO: Docstring for .

    :arg1: TODO
    :returns: TODO

    """
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


def get_historical_df(year):
    """TODO: Docstring for get_historical_df.

    :year: TODO
    :returns: TODO

    """
    record_fname = "volley-{}-{}.csv".format(year, year + 1)
    csv_path = path.join(RECORD_DIRECTORY, record_fname)
    df = pd.read_csv(csv_path)

    # Add some useful miscellaneous columns.
    df["date"] = pd.to_datetime(df["date"])
    df["home_won"] = df["home_score"] == 3

    return df


def record_seasons(dfs, K=40, R=3, elo_name="elo", reset=False):
    """
    Record conseuctive Elo years.

    :dfs: A list of match dataframes, taken to be consecutive seasons.
    :K: K-factor for Elo updating.
    :R: Regression proportion; teams lose an Rth of their distance to 1500 Elo.
    :returns: Nothing, but modifies dataframes in-place.

    """
    if reset:
        for team in TEAMS.values():
            team.elo = 1500

    for df in dfs:
        for name, team in TEAMS.items():
            team.wins = 0
            team.losses = 0

        # Regress teams back towards the mean slightly.
        for team in TEAMS.values():
            team.elo -= (team.elo - 1500) / R

        add_match_elo_columns(TEAMS, df, elo_name, K=K)


if __name__ == "__main__":
    # Use this to populate elo columns.
    dfs = {year: get_historical_df(year) for year in range(12, 21)}
    record_seasons(list(dfs.values()), reset=True)
    team_dfs = {year: team_elo_df(d) for year, d in dfs.items()}

    for year, df in dfs.items():
        df.to_csv("./data/elo/volley-elo-{}-{}.csv".format(year, year + 1))

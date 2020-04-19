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

from volley_scrape import RECORD_DIRECTORY, CSV_FIELDNAMES
from datetime import datetime, timedelta
import os.path as path
import elo
import csv

ELO_DIRECTORY = "data/elo/"
ELO_TEAMS_DIR = path.join(ELO_DIRECTORY, "teams/")
ELO_MATCH_DIR = path.join(ELO_DIRECTORY, "matches/")
TEAMS_FIELDNAMES = ["name", "wins", "losses", "elo", "date"]

NAMES = ['Berry', 'Birmingham-Southern', 'Hendrix', 'Millsaps', 'Oglethorpe',
        'Centre', 'Sewanee', 'Rhodes']
TEAMS = {name: elo.Team(name, 1500) for name in NAMES}


def record_season(teams, year, K, R):
    """Record a single volleyball season with Elo tracking.

    :teams: Dictionary of (name, elo.Team) pairs.
    :year: Two-digit string year.
    :K: K-factor for Elo updating.
    :R: Regression proportion; teams lose an Rth of their distance to 1500 Elo.
    :returns: List of paths to csv files with results.

    """
    # Regress teams back towards the mean slightly.
    for team in teams.values():
        team.elo -= (team.elo - 1500) / R

    record_fname = "volley-{}-{}.csv".format(year, year + 1)
    elo_fname = "volley-{}-{}-elo.csv".format(year, year + 1)
    path_in = path.join(RECORD_DIRECTORY, record_fname)

    path_teams_out = path.join(ELO_TEAMS_DIR, elo_fname)
    path_match_out = path.join(ELO_MATCH_DIR, elo_fname)

    csv_in = open(path_in)
    csv_match_out = open(path_match_out, "w")
    csv_teams_out = open(path_teams_out, "w")

    reader = csv.DictReader(csv_in)
    match_writer = csv.DictWriter(csv_match_out, fieldnames=CSV_FIELDNAMES)
    teams_writer = csv.DictWriter(csv_teams_out, fieldnames=TEAMS_FIELDNAMES)

    match_writer.writeheader()
    teams_writer.writeheader()

    # Get initial date and write "pre-season Elo" rows in the teams file.
    first_row = next(reader)
    start_date = datetime.strptime(first_row["date"], "%Y-%M-%d")
    initial_date = start_date - timedelta(days=4)
    initial_date = initial_date.strftime("%Y-%M-%d")

    for name, team in teams.items():
        teams_writer.writerow({"name": name, "wins": team.wins,
                               "losses": team.losses, "elo": team.elo,
                               "date": initial_date})

    def handle_row(row):
        home = teams[row["home"]]
        away = teams[row["away"]]

        match = elo.Match(home, away, row["home-score"], row["away-score"])

        row["home-elo"] = home.elo
        row["away-elo"] = away.elo
        row["elo-win-prob"] = match.win_prob
        row["home-wins"] = home.wins
        row["home-losses"] = home.losses
        row["away-wins"] = away.wins
        row["away-losses"] = away.losses

        match.update_teams(K)

        match_writer.writerow(row)

        teams_writer.writerow({"name": home.name, "wins": home.wins, "losses": home.losses, "elo": home.elo, "date": row["date"]})
        teams_writer.writerow({"name": away.name, "wins": away.wins, "losses": away.losses, "elo": away.elo, "date": row["date"]})

    handle_row(first_row)

    for row in reader:
        handle_row(row)

    csv_in.close()
    csv_match_out.close()
    csv_teams_out.close()


def record_seasons(start, stop, K=40, R=3):
    for year in range(start, stop):
        record_season(TEAMS, year, K, R)

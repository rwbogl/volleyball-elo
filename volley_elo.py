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

from volley_scrape import RECORD_DIRECTORY
from datetime import timedelta
from datetime import datetime
import os.path as path
import elo
import csv

ELO_DIRECTORY = "data/elo"

NAMES = ['Berry', 'Birmingham-Southern', 'Hendrix', 'Millsaps', 'Oglethorpe',
        'Centre', 'Sewanee', 'Rhodes']
TEAMS = {name: elo.Team(name, 1500) for name in NAMES}


def record_season(teams, year, K):
    # Regress teams back towards the mean slightly.
    for team in teams.values():
        team.elo -= (team.elo - 1500) / 4

    record_fname = "volley-{}-{}.csv".format(year, year + 1)
    elo_fname = "volley-{}-{}-elo.csv".format(year, year + 1)
    path_in = path.join(RECORD_DIRECTORY, record_fname)
    path_out = path.join(ELO_DIRECTORY, elo_fname)

    csv_in = open(path_in)
    csv_out = open(path_out, "w")

    out_names = ["name", "elo", "date"]

    reader = csv.DictReader(csv_in)
    writer = csv.DictWriter(csv_out, fieldnames=out_names)

    writer.writeheader()

    first_row = next(reader)
    start_date = datetime.strptime(first_row["date"], "%Y-%M-%d")
    initial_date = start_date - timedelta(days=4)
    initial_date = initial_date.strftime("%Y-%M-%d")

    for team in teams.values():
        # Conference play starts in mid September or something.
        writer.writerow({"name": team.name, "elo": team.elo, "date": initial_date})

    def handle_row(row):
        home = teams[row["home"]]
        away = teams[row["away"]]

        match = elo.Match(home, away, row["home-score"], row["away-score"])

        match.update_elo(K)

        writer.writerow({"name": home.name, "elo": home.elo, "date": row["date"]})
        writer.writerow({"name": away.name, "elo": away.elo, "date": row["date"]})

    # handle_row(first_row)

    for row in reader:
        handle_row(row)

    csv_in.close()
    csv_out.close()


def record_seasons(start, stop, K=40):
    for year in range(start, stop):
        record_season(TEAMS, year, K)

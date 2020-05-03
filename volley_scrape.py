#!/usr/bin/env python3

"""
Scrape and parse SAA volleyball match records from the past few years.

The goal of this is to simply record who played and the results in a csv file.
We aren't doing any fancy Elo stuff here. That's for another module.
"""

from bs4 import BeautifulSoup
from utils import CONF_NAMES
import os.path as path
import requests
import calendar
import csv
import re

MONTH_DICT = {v: k for k, v in enumerate(calendar.month_name)}
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

# I'm not sure if we'll use all these fieldnames, but I'll add them for now.
CSV_FIELDNAMES = ["home", "away", "home_score", "away_score", "home_wins", "home_losses", "away_wins", "away_losses", "home_elo", "away_elo", "elo_win_prob", "postseason", "date"]

HTML_DIRECTORY = "data/html"
RECORD_DIRECTORY = "data/historical"

DATE_RE = re.compile("Women's Volleyball event: (\w*) (\d*) .*")


def get_soup(year):
    """
    Soupify the html page of a year (given that it's downloaded).
    """
    fname = "volley-{}-{}.html".format(year, year + 1)
    with open(path.join(HTML_DIRECTORY, fname)) as f:
        return BeautifulSoup(f.read())


if __name__ == "__main__":
    for year in range(12, 21):
        fname = "volley-{}-{}".format(year, year + 1)

        html_path = path.join(HTML_DIRECTORY, fname + ".html")
        record_path = path.join(RECORD_DIRECTORY, fname + ".csv")

        try:
            f = open(html_path)

            print("Read file", html_path)
        except FileNotFoundError:
            url = "https://www.saa-sports.com/sports/wvball/20{}-{}/schedule".format(year, year + 1)
            print("GET", url)

            r = requests.get(url, headers={"User-Agent": USER_AGENT})
            print(r.status_code)

            if r.status_code != 200:
                print("error with", url)
                continue

            with open(html_path, "w") as f:
                f.write(r.text)

            print("Wrote", html_path)
            f = open(html_path)

        print("Souping")
        text = f.read()
        f.close()
        soup = BeautifulSoup(text)

        conf_markers = soup.find_all(title="Conference")
        rows = [("reg", t.parent.parent) for t in conf_markers]

        postseason_markers = soup.find_all(title="Post Season")
        postseason_rows = [("post", t.parent.parent) for t in postseason_markers]

        # BOLD ASSUMPTION: The postseason happens after the regular season.
        rows += postseason_rows

        print("Parsing rows")
        with open(record_path, "w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()

            for post, row in rows:
                try:
                    date_match = DATE_RE.match(row.ul.li.a["aria-label"])
                    month, day = date_match.group(1), date_match.group(2)
                    month = MONTH_DICT[month]
                except AttributeError:
                    month, day = None, None

                names = row.find_all(class_="team-name")
                home = names[0].text
                away = names[1].text

                # We don't track out-of-conference games.
                if home not in CONF_NAMES or away not in CONF_NAMES:
                    continue

                # Fix some data issues.
                if home == "Birmingham Southern":
                    home = "Birmingham-Southern"

                if away == "Birmingham Southern":
                    away = "Birmingham-Southern"

                if month and day:
                    date = "20{}-{}-{}".format(year, month, day)
                else:
                    date = None

                try:
                    results = row.find_all(class_="e_result")
                    home_score = int(results[0].text.strip())
                    away_score = int(results[1].text.strip())
                except ValueError:
                    home_score = None
                    away_score = None

                postseason = True if post == "post" else False

                writer.writerow({"home": home, "away": away, "home_score": home_score, "away_score": away_score, "postseason": postseason, "date": date})

        print("Wrote", record_path)
        print("Done")

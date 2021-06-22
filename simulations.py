#!/usr/bin/env python3

import pandas as pd
import random
import copy
import elo


def predict_season(match_df, teams, iterations=1, regress=True, **kwargs):
    """TODO: Docstring for predict_season.

    :match_df: TODO
    :teams: Dictionary of (name, Team) pairs.
    :returns: TODO

    """
    data = {name:
                {"elo": [], "wins": [],
                 "losses": []} for name in teams.keys()}

    R = kwargs.get("R", 3)

    for _ in range(iterations):
        df = match_df.copy()
        new_teams = copy.deepcopy(teams)

        for team in new_teams.values():
            team.wins = 0
            team.losses = 0
            if regress:
                team.elo -= (team.elo - 1500) / R

        for row in df.itertuples():
            home = new_teams[row.home]
            away = new_teams[row.away]

            """
            Okay, I'm about to do something super hack-y here.

            Matches give an extra 20% weight to total beatdowns, and I'm not
            sure what's the best way to predict the "spread" based on Elo yet.
            (538 does something for the NFL, go check it out.) For now, I'm
            just going to say that every victory is a nice 3-1 win, which *as
            of right now* (2020-04-26 00:14) leaves its value unmodified.

            My point is that the score here is totally arbitrary, and I really
            want to say "just don't look at the score."
            """
            win_prob = elo.win_prob(home, away)
            if random.random() < win_prob:
                # Home team won.
                match = elo.Match(home, away, 3, 1, **kwargs)
            else:
                # Away team won.
                match = elo.Match(home, away, 1, 3, **kwargs)

            match.update_teams()

        for name, team in new_teams.items():
            data[name]["elo"].append(team.elo)
            data[name]["wins"].append(team.wins)
            data[name]["losses"].append(team.losses)

    # Turn the results into a MultiIndex dataframe.

    # Borrowed from: https://stackoverflow.com/a/24988227/6670539
    reform = {(outer_key, inner_key): values for outer_key, inner_dict in data.items() for inner_key, values in inner_dict.items()}

    return pd.DataFrame(reform)


if __name__ == "__main__":
    import volley_elo
    import matplotlib.pyplot as plt
    dfs = {year: volley_elo.get_historical_df(year) for year in range(12, 20)}

    # Only record seasons up to 2019. (This actually modifies volley_elo.TEAMS,
    # don't forget that.)
    volley_elo.record_seasons(list(dfs.values())[:-1])

    test_df = dfs[19]
    res = predict_season(test_df, volley_elo.TEAMS, 10000)

    print(res.describe())

    plt.style.use("seaborn")
    res["Oglethorpe"]["elo"].hist(alpha=0.8, label="OU")
    res["Birmingham-Southern"]["elo"].hist(alpha=0.8, label="BSC")
    res["Berry"]["elo"].hist(alpha=0.8, label="BE")
    plt.legend()
    plt.title("Histogram of forecasted wins for the 2019-2020 SAA Women's Volleyball Season")
    plt.ylabel("Frequency")
    plt.xlabel("Wins")
    plt.show()

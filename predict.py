import matplotlib.pyplot as plt
import pandas as pd
import random
import vello
import copy
import elo

TRAIN_INPUT = "./data/games.csv"
TEST_INPUT = "./data/test.csv"

def predict_season(match_df, teams, iterations=1, regress=True, **kwargs):
    """
    Simulate the matches described by `match_df` using the teams from a given
    dictionary.

    """
    R = kwargs.get("R", 3)

    # Only look at teams which actually appear in the season.
    teams = {team.name: team for team in teams if
                team.name in match_df.home.values or
                team.name in match_df.away.values}

    data = {name:
            {"elo": [], "wins": [], "seed": [], "first_round": [],
                "second_round": [], "champs": [], "pct": [],
                 "losses": []} for name in teams.keys()}


    for _ in range(iterations):
        matches_df = match_df.copy()
        new_teams = copy.deepcopy(teams)

        for team in new_teams.values():
            team.wins = 0
            team.losses = 0
            if regress:
                team.elo -= (team.elo - 1500) / R

        for match in matches_df.itertuples():
            if match.postseason:
                # Don't handle scheduled postseason matches.
                # (If you pass in a historical year where postseason matches
                # are included, we want to skip those.)
                continue

            home = new_teams[match.home]
            away = new_teams[match.away]

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
            data[name]["pct"].append(team.wins / (team.wins + team.losses))

        # Handle the postseason.
        # For now (2021-06-22 23:18) we're going to use the 2020 playoff rules:
        # Top 4 seeds play each other in a tournament.

        # It LOOKS LIKE this is the ranking.
        rank = lambda name: data[name]["wins"][-1] - data[name]["losses"][-1]
        rankings = sorted(list(new_teams.keys()), key=rank, reverse=True)
        top_4 = rankings[:4]
        for k, name in enumerate(rankings):
            data[name]["first_round"].append(False)
            data[name]["second_round"].append(False)
            data[name]["champs"].append(False)
            data[name]["seed"].append(k + 1)

        for name in top_4:
            data[name]["first_round"][-1] = True

        one = new_teams[top_4[0]]
        two = new_teams[top_4[1]]
        three = new_teams[top_4[-2]]
        four = new_teams[top_4[-1]]

        # Simulate 1-4.
        if random.random() < elo.win_prob(one, four):
            data[top_4[0]]["second_round"][-1] = True
            one_winner = top_4[0]
            elo.Match(one, four, 3, 1, **kwargs).update_teams()
        else:
            data[top_4[-1]]["second_round"][-1] = True
            one_winner = top_4[-1]
            elo.Match(one, four, 1, 3, **kwargs).update_teams()

        # Simulate 2-3.
        if random.random() < elo.win_prob(two, three):
            data[top_4[1]]["second_round"][-1] = True
            two_winner = top_4[1]
            elo.Match(two, three, 3, 1, **kwargs).update_teams()
        else:
            data[top_4[-2]]["second_round"][-1] = True
            two_winner = top_4[-2]
            elo.Match(two, three, 1, 3, **kwargs).update_teams()

        new_one = new_teams[one_winner]
        new_two = new_teams[two_winner]

        # Simulate the championship.
        if random.random() < elo.win_prob(new_one, new_two):
            data[one_winner]["champs"][-1] = True
            elo.Match(new_one, new_two, 3, 1, **kwargs).update_teams()
        else:
            data[two_winner]["champs"][-1] = True
            elo.Match(new_one, new_two, 1, 3, **kwargs).update_teams()

    # Turn the results into a MultiIndex dataframe.

    # Borrowed from: https://stackoverflow.com/a/24988227/6670539
    reform = {(outer_key, inner_key): values for outer_key, inner_dict in data.items() for inner_key, values in inner_dict.items()}

    return list(teams.keys()), pd.DataFrame(reform)


if __name__ == "__main__":
    teams, df = vello.load_games(TRAIN_INPUT)
    vello.record_games(df, teams)

    used_teams, test_df = vello.load_games(TEST_INPUT)

    teams, res = predict_season(test_df, teams, 1000)

    print(res.describe())

    plt.style.use("seaborn")
    fig, axes = plt.subplots(3, 3)

    for k, team in enumerate(sorted(teams)):
        print(team)
        col = k % 3
        row = k // 3
        res[team]["pct"].hist(ax=axes[row][col], color="C{}".format(k))
        axes[row][col].set_title(team)
        axes[row][col].set_xlim(0, 1)

    # plt.title("Histogram of forecasted wins for the 2020-2021 SAA Women's Volleyball Season")
    # plt.ylabel("Frequency")
    # plt.xlabel("Wins")
    plt.show()

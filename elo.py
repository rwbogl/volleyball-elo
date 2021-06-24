from itertools import combinations
from numpy.random import normal, randint


class Team:
    def __init__(self, name, elo):
        self.name = name
        self.elo = elo
        self.wins = 0
        self.losses = 0

    def __str__(self):
        return "{} ({})".format(self.name, round(self.elo))

    def __repr__(self):
        return "{} ({})".format(self.name, round(self.elo))


class Match:
    def __init__(self, home, away, home_score, away_score, **kwargs):
        """
            Supported kwargs:

                :home_advantage: Additive Elo constant for home advantage.

                :postseason: Boolean postseason flag.

                :postseason_multiplier: Constant factor for postseason Elo.

                :K: Elo K-factor, the "base" Elo change from a win (defaults to 40).

                :set_map: Dictionary mapping number of sets (3, 4, 5) to
                          constant Elo mutliplier.

        """
        self.home = home
        self.away = away
        self.home_score = int(home_score)
        self.away_score = int(away_score)
        self.sets = self.home_score + self.away_score
        self.winner = home if self.home_score == 3 else away
        self.home_win_val = 1 if self.home_score == 3 else 0

        self.home_advantage = kwargs.get("home_advantage", 0)
        self.postseason = kwargs.get("postseason", False)
        self.postseason_multiplier = kwargs.get("postseason_multiplier", 1.2)
        self.K = kwargs.get("K", 40)
        self.set_map = kwargs.get("set_map", {3: 1.2, 4: 1, 5: 0.9})

        self.set_factor = self.set_map[self.sets]

    @property
    def win_prob(self):
        """Return the probability that the home team wins."""
        d = self.home.elo + self.home_advantage - self.away.elo
        return 1 / (1 + 10**(-d / 400))

    def home_elo_change(self):
        """Return the change in Elo for the home team from this match."""
        if self.home_score == 3:
            d = self.home.elo + self.home_advantage - self.away.elo
        else:
            d = self.away.elo - (self.home.elo + self.home_advantage)

        # Stolen from Nate Silver.
        # (Not the exact numbers.)
        # (https://fivethirtyeight.com/features/introducing-nfl-elo-ratings/)
        underdog_factor = 1

        factor = self.K * self.set_factor * underdog_factor

        if self.postseason:
            factor *= 1.3

        return factor * (self.home_win_val - self.win_prob)

    def update_teams(self):
        """
        Update the records and Elo ratings of the involved teams based on the
        match.

        Note that this could be called repeatedly with different effects each
        time.
        """
        self.home.elo += self.home_elo_change()
        self.away.elo -= self.home_elo_change()

        if self.home_score == 3:
            self.home.wins += 1
            self.away.losses += 1
        else:
            self.away.wins += 1
            self.home.losses += 1

    def __str__(self):
        return "{} @ {}: {}-{}".format(self.home, self.away, self.home_score, self.away_score)

    def __repr__(self):
        return "{} @ {}: {}-{}".format(self.home, self.away, self.home_score, self.away_score)


def win_prob(home, away, home_advantage=0):
    """TODO: Docstring for win_prob.

    :home_elo: TODO
    :away_elo: TODO
    :returns: TODO

    """
    d = home.elo + home_advantage - away.elo
    return 1 / (1 + 10**(-d / 400))


def brier_score(df, result_col, predict_col):
    """
    Calculate a modified Brier score given a dataframe with results and
    probability predictions.

    Idea stolen from 538's NFL Elo game.

    Gist:

        Brier scores are in [0, 1], with 0 being the best and 1 being the
        worst. That's a terrible idea for a "score."

        Flip it so that 1 is the best and 0 is the worst, then linearly scale
        everything to lie in [0, 100]. We want to say that a prediction of 1 /
        2 gives you zero points, and we'll achieve this by an additive shift.
        Thus:

                100 (1 - (1 / 2)^2) + c = 0
                                      c = -75.

        We subtract off 75 points. So, bets near 50/50 will get nearly nothing,

    """
    return 100 * (1 - (df[result_col] - df[predict_col])**2) - 75


def brier(result, prediction):
    return 100 * (1 - (result - prediction)**2) - 75


if __name__ == "__main__":
    ou = Team("OU", 1500)
    ct = Team("CT", 1500)

    m = Match(ou, ct, 3, 2)

    # Now let's try a real test.
    # Generate n random teams with preset strengths.

    means = [1200, 1500, 1700]
    stds = [100, 50, 100]

    teams = [(m, stds[k], Team("t" + str(k), m)) for k, m in enumerate(means)]

    # Make every team play the others, ten times each.
    for k in range(1000):
        for home, away in combinations(teams, 2):
            home_mean, home_std, home_team = home
            away_mean, away_std, away_team = away

            if normal(home_mean, away_std) >= normal(away_mean, away_std):
                m = Match(home_team, away_team, 3, randint(1, 3))
            else:
                m = Match(home_team, away_team, randint(1, 3), 3)

            home_team.elo += m.elo_change
            away_team.elo -= m.elo_change

    # Wow! Works pretty well!

    # One complaint: Though it happens slowly, the very worst and best teams
    # may drift off to unbounded Elo. We need harsher penalties for heavy
    # favorites winning. (I've added a quick "underdog factor" to try and fix
    # this.)

    # (I'm a little worried that my underdog factor is too aggressive. Maybe I
    # should tone it down.)

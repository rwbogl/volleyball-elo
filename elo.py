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
    def __init__(self, home, away, home_score, away_score, home_advantage=0):
        self.home = home
        self.away = away
        self.home_score = int(home_score)
        self.away_score = int(away_score)
        self.sets = home_score + away_score
        self.winner = home if self.home_score == 3 else away
        self.home_win_val = 1 if self.home_score == 3 else 0
        self.home_advantage = home_advantage

        if self.sets == 3:
            self.set_factor = 1.2
        elif self.sets == 4:
            self.set_factor = 1
        else:
            self.set_factor = 0.9

    @property
    def win_prob(self):
        """Return the probability that the home team wins."""
        d = self.home.elo + self.home_advantage - self.away.elo
        return 1 / (1 + 10**(-d / 400))

    def home_elo_change(self, K):
        """Return the change in Elo for the home team from this match."""
        if self.home_score == 3:
            d = self.home.elo + self.home_advantage - self.away.elo
        else:
            d = self.away.elo - (self.home.elo + self.home_advantage)
        # Stolen from Nate Silver.
        # (Not the exact numbers.)
        # (https://fivethirtyeight.com/features/introducing-nfl-elo-ratings/)
        underdog_factor = 1

        factor = K * self.set_factor * underdog_factor
        return factor * (self.home_win_val - self.win_prob)

    def update_teams(self, K):
        """
        Update the records and Elo ratings of the involved teams based on the
        match.

        Note that this could be called repeatedly with different effects each
        time.
        """
        self.home.elo += self.home_elo_change(K)
        self.away.elo -= self.home_elo_change(K)

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

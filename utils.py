CONF_NAMES = ['Berry', 'Birmingham-Southern', 'Hendrix', 'Millsaps', 'Oglethorpe',
              'Centre', 'Sewanee', 'Rhodes']


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

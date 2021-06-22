# Volleyball Elo Ratings

This is a small project to compute and analyze [Elo
ratings](https://en.wikipedia.org/wiki/Elo_rating_system) for Women's
Volleyball teams in the [Southern Athletic
Association](https://saa-sports.com/index.aspx?path=wvball).

The project contains:

1. CSV files summarizing match results of SAA play from 2012 ([data/](data/)).
   (This was originally scraped with a script, but the SAA changes its website
   so much that it's easier to just provide CSV files.)

2. Code to compute Elo scores ([volley_elo.py](volley_elo.py)).

3. Code for example Elo and [Brier
   score](https://en.wikipedia.org/wiki/Brier_score) analysis ([historical_plots.py](historical_plots.py)).

4. Code to predict future games based on current Elo ([simulations.py](simulations.py)).

## Examples

The following code will load some dataframes and populate them with Elo and
Brier score data:

```python
import volley_elo
from utils import brier_score

df = volley_elo.get_historical_df(19)

# (Dictionary order is guaranteed to be insertion order in 3.7+.)
volley_elo.record_seasons([df])
volley_elo.record_seasons([df], K=100, elo_name="big-elo")
volley_elo.record_seasons([df], K=20, elo_name="small-elo")

print(df["elo_win_prob"])
print(df["big-elo_win_prob"])
print(df["small-elo_win_prob"])

brier = brier_score(df, "home_won", "elo_win_prob")
brier2 = brier_score(df, "home_won", "big-elo_win_prob")

brier_total = brier.cumsum()
brier2_total = brier.cumsum()
```

The file `historical_plots.py` contains a much more complicated example,
including plots.

The file `simulations.py` contains examples for running simulations of future
games based on Elo.

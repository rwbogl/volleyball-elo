# Volleyball Elo Ratings

This is a small project to compute and analyze [Elo
ratings](https://en.wikipedia.org/wiki/Elo_rating_system) for Women's
Volleyball teams in the [Southern Athletic
Association](https://www.saa-sports.com/sports/wvball).

The project contains scripts to:

1. Scrape and parse historical match data from the SAA's website ([volley_scrape.py](volley_scrape.py))

2. Compute Elo scores from historical data ([volley_elo.py](volley_elo.py))

3. Plot examples of Elo and [Brier
   score](https://en.wikipedia.org/wiki/Brier_score) analysis ([historical_plots.py](historical_plots.py))

3. Predict future games based on current Elo ([simulations.py](simulations.py))

## Getting started

First, run `./volley_scrape.py` to ensure that the relevant historical data has
been scraped from the SAA's website.

Then, the following code will load some dataframes and populate them with Elo
and Brier score data:

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

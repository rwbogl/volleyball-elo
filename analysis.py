import pandas as pd
import matplotlib.pyplot as plt


def get_elo_df(year):
    return pd.read_csv("./data/elo/volley-{}-{}-elo.csv".format(year, year + 1))


def plot_elo(year):
    df = get_elo_df(year)
    plt.style.use("seaborn-darkgrid")

    fig = plt.figure()
    ax = plt.gca()

    df["date"] = pd.to_datetime(df["date"])

    for name, group in df.groupby("name"):
        group.plot(label=name, x="date", y="elo", ax=ax)

    plt.title("Elo rankings for 20{}-{} season".format(year, year + 1))
    plt.axhline(1500, color="k", linestyle="--", label='"Average"')
    plt.legend()
    plt.show()

import pandas as pd
import Levenshtein as lev


def calc_leven(row):
	col2 = str(row["description"])
	return lev.distance(col2,st)

gramdf = pd.read_csv("data/foodandgrams.csv")
grams = gramdf.loc[gramdf.apply(calc_leven,axis=1).idxmin()]["gram_weight"]



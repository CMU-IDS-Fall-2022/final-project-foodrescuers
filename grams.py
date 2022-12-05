import pandas as pd

def get_grams(row):
	col2 = str(row["Serving"])
	start = col2.find("(")
	end = col2.find(")")
	return float(col2[start+1:end-2])

st = "Apples"

gramdf = pd.read_csv("data/foodcalories.csv")
gramdf["grams"] = gramdf.apply(get_grams,axis=1)
gramdf["Food"] = gramdf["Food"].str.lower()



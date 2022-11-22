import pandas as pd

def impact_calculate(name, grams):
  df = pd.read_csv("data/Food_Impact.csv")

  x = df.loc[(df['Entity'] == name), ['Emissions per kilogram', 'Eutrophication per kilogram', 'Land use per kilogram', 'Water scarcity per kilogram',	'Water withdrawals per kilogram']]
  total = x * (grams / 1000)
  return total


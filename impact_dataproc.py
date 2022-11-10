
import pandas as pd
import numpy as np
from pandas_profiling import ProfileReport

files = ['data/raw/food-footprints_comm_carbon.csv',
 'data/raw/food-footprints_comm_eutro.csv',
 'data/raw/food-footprints_comm_land.csv',
 'data/raw/food-footprints_comm_scarcity.csv',
 'data/raw/food-footprints_comm_water.csv',
 'data/raw/food-footprints_specific.csv']

dfs = {}
for i,file in enumerate(files):
    dfs[i] = pd.read_csv(file)


specfoodprod = dfs[5].iloc[:,:-4:4].copy()
specfoodprod["Year"] = dfs[5]["Year"]

for i in range(5):
    dfs[i]=dfs[i].drop("Code",axis=1)

for i in range(1,5):
    dfs[0] = pd.merge(dfs[0],dfs[i])

commodity = dfs[0].copy()

ccolumns = list(commodity.columns)

mapping = {"Entity":"Entity",
          'GHG emissions per kilogram (Poore & Nemecek, 2018)':'Emissions per kilogram',
          "Year":"Year",
          "Eutrophying emissions per kilogram (Poore & Nemecek, 2018)":'Eutrophication per kilogram',
          'Land use per kilogram (Poore & Nemecek, 2018)':'Land use per kilogram',
          'Scarcity-weighted water use per kilogram (Poore & Nemecek, 2018)':'Water scarcity per kilogram',
          'Freshwater withdrawals per kilogram (Poore & Nemecek, 2018)':'Water withdrawals per kilogram'}

for i,c in enumerate(ccolumns):
    ccolumns[i] = mapping[c]

commodity.columns = ccolumns

commodity["Label"] = "Commodity"

specfoodprod["Label"] = "Specific Food Products"

final = pd.concat([commodity,specfoodprod],ignore_index=True)

final.to_csv("data/Food_Impact.csv")

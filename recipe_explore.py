import pickle as pk
import pandas 

with open('data/raw/ingr_map.pkl', 'rb') as f:
    data = pk.load(f)

print(type(data))
data.head().to_csv("data/recipe_head.csv") 



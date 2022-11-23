import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from stqdm import stqdm
import streamlit as st

def parsein(ings):
    return ings[1:-1].replace("'","").replace(",","")

st.title("Hello")
df = pd.read_csv("RAW_recipes.csv")
df["ingredients_fmt"] = df["ingredients"].apply(parsein)
df.ingredients_fmt.values.astype('U')
tfidf = TfidfVectorizer()
tfidfing = tfidf.fit_transform(df["ingredients_fmt"])
inputing = "prepared pizza crust sausage patty eggs milk salt and pepper cheese"
inputtfidf = tfidf.transform([inputing])
cos_sim = map(lambda x: cosine_similarity(inputtfidf, x), tfidfing)
scores = list(stqdm(cos_sim,total=len(df["ingredients_fmt"])))
top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]


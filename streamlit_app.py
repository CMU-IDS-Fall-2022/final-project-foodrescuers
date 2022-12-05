import streamlit as st
import pandas as pd
import altair as alt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from stqdm import stqdm
import Levenshtein as lev
from stack_chart import * # implementation file of stack chart
from impact import impact_calculate

@st.cache()  # add caching so we load the data only once
def load_data():
    df = pd.read_csv("data/Food_Impact.csv")
    # normalized per categories then divide by 4 and mult by 100 (--> mult 25)
    df['impact_idx'] = (df['Emissions per kilogram'] / df['Emissions per kilogram'].max() + \
        df['Land use per kilogram'] / df['Land use per kilogram'].max() + \
        df['Water withdrawals per kilogram'] / df['Water withdrawals per kilogram'].max() + \
        df['Eutrophication per kilogram'] / df['Eutrophication per kilogram'].max()) * 25
    df["Normalized land use"] = df['Land use per kilogram'] / df['Land use per kilogram'].max() * 25
    df["Normalized water withdrawals"] = df['Water withdrawals per kilogram'] / df['Water withdrawals per kilogram'].max() * 25
    df["Normalized eutrophication"] = df['Eutrophication per kilogram'] / df['Eutrophication per kilogram'].max() * 25
    df["Normalized greenhouse emissions"] = df['Emissions per kilogram'] / df['Emissions per kilogram'].max() * 25

    return df
@st.cache()
def load_recipes():
    return pd.read_csv("reciperec/RAW_recipes.csv")
@st.cache
def get_slice_membership(df, flabels):
    """
    Implement a function that computes which rows of the given dataframe should
    be part of the slice, and returns a boolean pandas Series that indicates 0
    if the row is not part of the slice, and 1 if it is part of the slice.
    
    In the example provided, we assume genders is a list of selected strings
    (e.g. ['Male', 'Transgender']). We then filter the labels based on which
    rows have a value for gender that is contained in this list. You can extend
    this approach to the other variables based on how they are returned from
    their respective Streamlit components.
    """
    labels = pd.Series([1] * len(df), index=df.index)
    if flabels:
        labels &= df['Label'].isin(flabels)
    # if entities:
    #     labels &= df['Entity'].isin(entities)
    # ... complete this function for the other demographic variables
    return labels
#############
# MAIN CODE #
#############

st.set_page_config(layout="wide") # wide page format
st.title("Food Rescuers")

with st.spinner(text="Loading data..."):
    df = load_data()
    dfr = load_recipes()
###############
# STACK CHART #
###############
stack_chart_frame(df)


def parsein(ings):
    return ings[1:-1].replace("'","").replace(",","")

def parsein2(ings):
    return ings[1:-1].replace("'","").split(",")


def calc_leven(row,ing):
	col2 = str(row["description"])
	return lev.distance(col2,ing)

def calc_leven2(row,ing):
	col2 = str(row["Entity"]).lower()
	return lev.distance(col2,ing)



if st.button('Load recipes'):
    st.title("Loading Recipes. This may take a while......")
    dfr["ingredients_fmt"] = dfr["ingredients"].apply(parsein)
    dfr.ingredients_fmt.values.astype('U')
    st.write("Encoding your data 🤖")
    tfidf = TfidfVectorizer()
    tfidfing = tfidf.fit_transform(dfr["ingredients_fmt"])
    inputing = "prepared pizza crust sausage patty eggs milk salt and pepper cheese"
    inputtfidf = tfidf.transform([inputing])
    out = "Example input: "+inputing
    st.write(out)
    st.write("Finding the best recipe given your ingredients:")
    cos_sim = map(lambda x: cosine_similarity(inputtfidf, x), tfidfing)
    scores = list(stqdm(cos_sim,total=len(dfr["ingredients_fmt"])))
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]

    st.write("Suggested recipes: ")
    for i,t in enumerate(top):
        totalemissions = 0
        totaleutrophication = 0
        totallanduse = 0
        totalwaterscarcity = 0
        totalwaterwithdrawals = 0
        ingrs = dfr.iloc[t]["ingredients"]
        for ingredient in parsein2(ingrs):
            gramdf = pd.read_csv("data/foodandgrams.csv")
            grams = gramdf.loc[gramdf.apply(calc_leven,axis=1,ing=ingredient).idxmin()]["gram_weight"]
            closeingredient = df.loc[df.apply(calc_leven2,axis=1,ing=ingredient).idxmin()]["Entity"]
            totalemissions += impact_calculate(closeingredient,grams).iloc[0]["Emissions per kilogram"]
            totaleutrophication += impact_calculate(closeingredient,grams).iloc[0]["Eutrophication per kilogram"]
            totallanduse += impact_calculate(closeingredient,grams).iloc[0]["Land use per kilogram"]
            totalwaterscarcity = impact_calculate(closeingredient,grams).iloc[0]["Water scarcity per kilogram"]
            totalwaterwithdrawals = impact_calculate(closeingredient,grams).iloc[0]["Water withdrawals per kilogram"]
        st.write(dfr.iloc[t]["name"] +"emissions: "+str(totalemissions)+ "eutrophication: "+str(totaleutrophication) + "landuse: "+str(totallanduse) + "waterscarcity: "+str(totalwaterscarcity)+ "waterwithdrawals: "+str(totalwaterwithdrawals))
        steps = dfr.iloc[t]["steps"][2:-2].split("', '")
        all_steps = ""
        for i,step in enumerate(steps):
            all_steps += str(i+1)+". "+step + " "
        st.write(all_steps)

           




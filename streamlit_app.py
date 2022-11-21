import streamlit as st
import pandas as pd
import altair as alt
import pandas as pd

from stack_chart import * # implementation file of stack chart

@st.cache()  # add caching so we load the data only once
def load_data():
    df = pd.read_csv("data/Food_Impact.csv")
    # normalized per categories then divide by 4 and mult by 100 (--> mult 25)
    df['impact_idx'] = (df['Emissions per kilogram'] / df['Emissions per kilogram'].max() + \
        df['Land use per kilogram'] / df['Land use per kilogram'].max() + \
        df['Water withdrawals per kilogram'] / df['Water withdrawals per kilogram'].max() + \
        df['Eutrophication per kilogram'] / df['Eutrophication per kilogram'].max()) * 25
    df["Normalized land use"] = df['Land use per kilogram'] / df['Land use per kilogram'].max() #* 25
    df["Normalized water withdrawals"] = df['Water withdrawals per kilogram'] / df['Water withdrawals per kilogram'].max() #* 25
    df["Normalized eutro"] = df['Eutrophication per kilogram'] / df['Eutrophication per kilogram'].max() #* 25
    df["Normalized greenhouse emissions"] = df['Emissions per kilogram'] / df['Emissions per kilogram'].max() #* 25

    return df
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
df
###############
# STACK CHART #
###############
stack_chart(df)


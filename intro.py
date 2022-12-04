import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st
import plotly.express as px
import altair 


# source: https://www.fao.org/platform-food-loss-waste/flw-data/en/
## import data and make cleaner table to work 
fao_df_raw = pd.read_csv("data/FAO_data.csv")
fao_df = fao_df_raw[['year','country','loss_percentage','activity','food_supply_stage','commodity']]
fao_df = fao_df.sort_values(by = ['year','country'], ascending=True)


# country options and selection
country_options = fao_df['country'].unique().tolist()
country_options.append('All')
country_options.sort()
country_choice = st.sidebar.multiselect('Which countries are you interested in?', country_options, ['United States of America'])

# year options and selection
date_options = fao_df['year'].unique().tolist()
date_selected = st.sidebar.selectbox('What year were you born?', date_options, index=23)
df_year_selected = fao_df[fao_df['year'] == date_selected]


df_filtered = fao_df[fao_df['year'] >= date_selected]
df_filtered = df_filtered[fao_df['country'].isin(country_choice)]


# filtering based on user input code
st.title('Food loss based on your selections')

st.dataframe(df_filtered.sort_values('year',
            ascending=False).reset_index(drop=True))


## graphing filtered data
fig = plt.figure(figsize=(10,4))
plt.xticks(rotation=60)

## not working - should change ylabel name
plt.ylabel("Food loss (kg)") 

sns.countplot(data=df_filtered, x="year")
st.write(fig)

#####
st.write('scatterplot')
## scatterplot
fig, ax = plt.subplots()
## need to fix to only show integers
plt.xticks(rotation=60)
plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.scatter(x='year',
           y='loss_percentage', 
           data=df_filtered)
st.pyplot(fig)


####
# st.write('sns')

# plot = sns.catplot(data=df_filtered, x='year', y='loss_percentage', aspect=5/2)
# plot.set(xlabel="year",
#             ylabel="loss percentage",
#             title="loss percentage")
# plot



## KNOWN BUGS
# selecting any years > 2018
# not selecting a country
# selecting 'All' countries

## GAPS
# no tool tip on scatterplot
# no coloring based on commodity
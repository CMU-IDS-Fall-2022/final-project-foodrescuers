# import json
# import requests
import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.ticker as mticker
# import seaborn as sns
import streamlit as st
# import plotly.express as px
import altair as alt
import pycountry
from vega_datasets import data
import numpy as np

# source: https://www.fao.org/platform-food-loss-waste/flw-data/en/
## import data and make cleaner table to work 

@st.cache()
def get_data():
    # main data #

    fao_df_raw = pd.read_csv("data/FAO_data.csv", low_memory=False)
    fao_df = fao_df_raw[['year','country','loss_percentage','food_supply_stage','commodity']]
    fao_df = fao_df.sort_values(by = ['year','country'], ascending=True)
    dtypes = {
    'year': 'int64',
    'country': 'string',
    'loss_percentage': 'float64',
    'food_supply_stage': 'string',
    'commodity': 'string'
    }
    fao_df = fao_df.astype(dtypes)
    #there are duplicates for some reason ... keep max
    fao_df['loss_percentage'] = fao_df.groupby(['year', 'country', 'commodity'])['loss_percentage'].transform(max)
    fao_df.drop_duplicates(inplace=True)

    # gets count info
    count = pd.Series.to_frame(fao_df.groupby(['year','country'])['commodity'].agg('count'))
    count.rename(columns={'commodity': 'count'}, inplace=True)

    # gets worst commodity info (for tooltip)
    fao_df['worst_loss'] = fao_df.groupby(['year','country'])['loss_percentage'].transform(max)
    worst_commodity = (fao_df[fao_df['loss_percentage']==fao_df['worst_loss']])[['year', 'country', 'commodity']]
    worst_commodity.rename(columns={'commodity': 'worst_commodity'}, inplace=True)

    # merges #
    merged = count.merge(worst_commodity, on=['year', 'country'])
    merged = fao_df.merge(merged, on=['year', 'country'], how='left')

    # get country information #

    country_df = pd.Series.to_frame(fao_df.groupby(['country', 'year'])['loss_percentage'].agg('mean'))
    
    #rename index
    multiindex = pd.MultiIndex.to_numpy(country_df.index)
    get_country = np.vectorize(lambda x: x[0])
    get_year = np.vectorize(lambda x: x[1])
    country_df['country'] = get_country(multiindex)
    country_df['year'] = get_year(multiindex)
    country_df = country_df.reset_index(drop=True)

    # clean country names 
    country_df['country'] = country_df['country'].apply(lambda x: "United States" if x=="United States of America" else x) # rename USA
    country_df.rename(columns={'loss_percentage': 'loss_average'}, inplace=True)

    return (fao_df, merged, country_df)

def intro_frame():

    (fao_df, merged, country_df) = get_data()

    st.write("According to the United States Department of Agriculture (USDA), " +\
        "between **30 - 40** percent of the food supply in the US is wasted. This " +\
        "corresponds to about **133 billion** pounds and **\$161 billion** worth of food" +\
        " in 2010. This is not just a problem in the United States; one-third of" +\
        " food produced for human consumption is lost or wasted globally. This "+\
        "amounts to 1.3 billion tons annually, worth approximately $1 trillion. If"+\
        " wasted food were a country, it would be the world's third-largest producer of carbon dioxide, after the USA and China ")
    st.write("Not convinced? Checkout...")
    st.title('Food loss percentage based on your selections')
    st.write('Select a country and year below to see the impacts of food waste around the world for a given country and time.')

    st.markdown('Adjust the year to get a different window of time. Hover over each bar to get information'+\
        ' about the commodity with the most loss for that country and year. Select one or more bars to'+\
        ' filter by year and interact with the scatterplot below')


    col1, col2 = st.columns(2)

    st.write("---")

    with col1:

        # country options and selection
        country_options = list(fao_df['country'].unique())
        country_options.sort()
        country_choice = st.multiselect('Which countries are you interested in?', country_options, ['United States of America'])

        all_countries = st.checkbox("Select all countries")

        if all_countries:
            country_choice = fao_df['country']

    with col2:

        # year options and selection
        date_options = fao_df['year'].unique().tolist()
        # cut options down to be values between 1970 and 2015
        date_options = [x for x in date_options if x <= 2015 and x >= 1970]
        date_selected = st.slider('What year are you interested in?', min_value=1970, max_value=2015, value=1990)


    col1b, col2b = st.columns(2)

    with col1b:
        # filtering based on user input code
        #made a date range for visbility purposes
        date_range = []
        k= 5
        for year in range(date_selected-k, date_selected+k+1):
            date_range.append(year)
        merged_filtered = merged[merged['year'].isin(date_range)]
        merged_filtered = merged_filtered[merged_filtered['country'].isin(country_choice)]


        num_shown_years = len(merged_filtered['year'].unique().tolist())

        year_select = alt.selection_multi(encodings=['x'])
        years_chart = alt.Chart(merged_filtered).mark_bar(size=20).encode(
            x=alt.X('year:Q', axis=alt.Axis(tickCount=num_shown_years)),
            y='count:Q',
            tooltip = ['worst_commodity:N', 'worst_loss:Q', 'country:N'],
            color=alt.condition(year_select, alt.value('darkgreen'), alt.value('darkseagreen'))
        ).add_selection(
            year_select
        ).properties(
            height=400
        )

        #####
        ## scatterplot

        scatter_chart = alt.Chart(merged_filtered).mark_circle(size=100).encode(
            x='commodity:N',
            y='loss_percentage:Q',
            tooltip=['year:Q', 'country:N','loss_percentage:Q'],
            color='year:N',
        ).transform_filter(
            year_select
        )

        st.altair_chart((years_chart & scatter_chart).resolve_scale(color='independent'), use_container_width=True)

        # worst loss for a given year selected
        #st.write(max(merged_filtered.worst_loss))


    with col2b:
                
        ## choropleth
        countries = alt.topo_feature(data.world_110m.url, 'countries')

        name2id = {}
        for country in pycountry.countries:
            name2id[country.name] = int(country.numeric)
        
    
        # standardize country names
        # labels = country_df['country'].apply(lambda x: x not in name2id)#isin(name2id.keys())
        # st.dataframe((country_df[labels])['country'].apply(lambda x: "."+x+"."))
        # st.write(len(country_df[labels]))

        
        # drop non-countries (e.g: "Africa")
        country_df_filtered = country_df[country_df['country'].isin(name2id.keys())]
        # add id column for choropleth map
        country_df_filtered['id'] = country_df_filtered['country'].apply(lambda x: name2id[x])

        # filter for year
        country_df_filtered = country_df_filtered[country_df_filtered['year']==date_selected]

        background = alt.Chart(countries).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).properties(
            width=650
        ).project('equirectangular')
        
        
        countries_chart = alt.Chart(countries).mark_geoshape().encode(
            color='loss_average:Q',
            tooltip=['country:N', 'loss_average:Q']
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(country_df_filtered, 'id', ['country', 'loss_average'])
        ).project(
            type='equirectangular'
        ).properties(
            width=650
        )

        st.write("Want to see how food loss is affected globally? Check out the average loss percentage across the globe for the selected year.")
        st.altair_chart(background + countries_chart)



## KNOWN BUGS
# selecting any years > 2018
# not selecting a country
# selecting 'All' countries

## GAPS
# no tool tip on scatterplot
# no coloring based on commodity

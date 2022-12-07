# import json
# import requests
import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.ticker as mticker
# import seaborn as sns
import streamlit as st
# import plotly.express as px
import altair as alt
import plotly.graph_objects as go


# source: https://www.fao.org/platform-food-loss-waste/flw-data/en/
## import data and make cleaner table to work 

@st.cache()
def get_data():
    fao_df_raw = pd.read_csv("data/FAO_data.csv", low_memory=False)
    fao_df = fao_df_raw[['year','country','loss_percentage','food_supply_stage','commodity']]
    fao_df = fao_df.sort_values(by = ['year','country'], ascending=True)
    dtypes = {
    'year': 'int64',
    'country': 'string',
    'loss_percentage': 'float64',
    'food_supply_stage': 'string',
    'commodity': 'string',
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

    #merges
    merged = count.merge(worst_commodity, on=['year', 'country'])
    merged = fao_df.merge(merged, on=['year', 'country'], how='left')

    return (fao_df, merged)

def intro_frame():

    (fao_df, merged) = get_data()
    # add a category in the dataframe for bucket
    #map between subregion and region name
    print(fao_df['commodity'].unique())
    
    st.write("According to the United States Department of Agriculture (USDA), " +\
        "between **30 - 40** percent of the food supply in the US is wasted. This " +\
        "corresponds to about **133 billion** pounds and **\$161 billion** worth of food" +\
        " in 2010. This is not just a problem in the United States; one-third of" +\
        " food produced for human consumption is lost or wasted globally. This "+\
        "amounts to 1.3 billion tons annually, worth approximately $1 trillion. If"+\
        " wasted food were a country, it would be the world's third-largest producer of carbon dioxide, after the USA and China ")

    col1, col2 = st.columns(2)

    with col1:
        # year options and selection
        country_born = "United States of America"
        date_options = fao_df[(fao_df['country'] == country_born)]['year'].unique().tolist()

        # cut options down to be values between 1970 and 2015
        date_selected = st.slider('What year are were you born in?', min_value=min(date_options) , max_value=max(date_options), value=1990)

    # filter fao_df based on user input
    fao_df_filtered = fao_df[(fao_df['country'] == country_born) & (fao_df['year'] == date_selected)]
    # top 10 loss percentage
    fao_df_filtered = fao_df_filtered.sort_values(by = ['loss_percentage'], ascending=False).drop_duplicates(subset=['commodity']).head(10)
    # row 0 of fao_df_filtered
    top_loss = fao_df_filtered.iloc[0]
    with col1:
        st.markdown(""" <style> .font {
        font-size:22px;font-weight: bold;} 
        </style> """, unsafe_allow_html=True)
        st.write(f"""In the year that you were born **({date_selected})**, the highest percentage loss of food commodity in the U.S. was:""""")
        st.markdown(f"""<span class="font">{top_loss['commodity']}</span> at <span class="font">{top_loss['loss_percentage']}%</span>""", unsafe_allow_html=True)
    with col2:
        # altair bar graph for fao_df_filtered
        bar = alt.Chart(fao_df_filtered).mark_bar().encode(
            x=alt.X('commodity', sort='-y', title='Commodity'),
            y=alt.Y('loss_percentage', title='Loss Percentage (%)'),
            color=alt.Color('commodity:N', legend=None),
            tooltip=['commodity', 'loss_percentage'],
        ).properties(
            title='Top 10 Loss Percentage in the U.S. in '+str(date_selected),
        )
        st.altair_chart(bar, use_container_width=True)

    st.write("Not convinced? Checkout...")
    st.write("---")

    st.title('Food loss percentage based on your selections')
    st.write('Select a country and year below to see the impacts of food waste around the world for a given country and time.')

    st.markdown('Adjust the year to get a different window of time. Hover over each bar to get information'+\
        ' about the commodity with the most loss for that country and year. Select one or more bars to'+\
        ' filter by year and interact with the scatterplot below')

    col1, col2 = st.columns(2)
    with col1:
        # country options and selection
        country_options = fao_df['country'].unique().tolist()
        country_options.sort()
        country_choice = st.multiselect('Which countries are you interested in?', country_options, ['United States of America'])
        #country_choice = st.sidebar.selectbox('Which countries are you interested in?', country_options, ['United States of America'])

        all_countries = st.checkbox("Select all countries")

        if all_countries:
            country_choice = fao_df['country']

    with col2:
        # year options and selection
        date_options = fao_df['year'].unique().tolist()
        # cut options down to be values between 1970 and 2015
        date_options = [x for x in date_options if x <= 2015 and x >= 1970]
        date_selected = st.slider('What year are you interested in?', min_value=1970, max_value=2015, value=1990)

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
    )

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
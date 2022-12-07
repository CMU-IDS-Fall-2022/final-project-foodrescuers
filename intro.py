# import json
# import requests
import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.ticker as mticker
# import seaborn as sns
import streamlit as st
# import plotly.express as px
import altair as alt


# source: https://www.fao.org/platform-food-loss-waste/flw-data/en/
## import data and make cleaner table to work 

@st.cache()
def get_data():
    fao_df_raw = pd.read_csv("data/FAO_data.csv")
    fao_df = fao_df_raw[['year','country','loss_percentage','food_supply_stage','commodity']]
    fao_df = fao_df.sort_values(by = ['year','country'], ascending=True)

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

    st.title('Food loss based on your selections')
    st.write('Food loss has impacted the world in many ways. Select a country and year below to see the impacts of food waste around the world for a given country and time.')

    st.markdown('Adjust the year to get a different window of time')
    st.markdown('Hover over each bar to get information about the commodity with the most loss for that country and year.')
    st.markdown('Select one or more bars to filter by year and interact with the scatterplot below')

    col1, col2 = st.columns(2)

    st.write("---")

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
        date_selected = st.selectbox('What year are you interested in?', date_options, index=0)

        
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


    # ## graphing filtered data
    # fig = plt.figure(figsize=(10,4))
    # plt.xticks(rotation=60)

    # ## not working - should change ylabel name
    # plt.ylabel("Food loss (kg)") 

    # sns.countplot(data=df_filtered, x="year")
    # st.write(fig)

    #####
    ## scatterplot
    # fig, ax = plt.subplots()
    # ## need to fix to only show integers
    # plt.xticks(rotation=60)
    # plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
    # ax.scatter(x='year',
    #            y='loss_percentage', 
    #            data=df_filtered)
    # st.pyplot(fig)

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

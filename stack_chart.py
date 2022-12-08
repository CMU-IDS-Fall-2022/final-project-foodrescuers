import streamlit as st
import pandas as pd
import altair as alt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_vega_lite import altair_component
import numpy as np
import math
@st.cache()
def get_slice_membership(df, label):
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
    if label:
        labels &= df['Label'] == label
    return labels
@st.cache()
def get_top_slice(df, entities, maxBarCount):
    # sort top MAX_BAR item df, but leave spots for selected food items
    topMax = df.sort_values(by=['impact_idx'], ascending=False).head(maxBarCount)
    # count overlap between topMax and entities
    overlap = topMax['Entity'].isin(entities)
    topBars = df.sort_values(by=['impact_idx'], ascending=False).head(maxBarCount -len(entities)+overlap.sum())
    # add food select to top10 using concat
    topBars = pd.concat([topBars, df[df['Entity'].isin(entities)]])
    # sort by impact index
    topBars = topBars.sort_values(by=['impact_idx'], ascending=False)
    return topBars
#############
# MAIN CODE #
#############

def stack_chart_frame(df):
    st.title("Explore the Environmental Impact of each Food Product")
    st.write("Now that we saw how much food is wasted, let's look at the environmental impact of food products"+\
        " to see how the food waste negatively impacts the environment in each category of land use, water withdrawals, "+\
        "greenhouse emissions, and eutrophication.")
    MAX_BAR = 10
    # compute food impact index by normalizing each column
    col1, col2 = st.columns(2)
    
    with col2:
        label = st.radio(
        "COMMODITY OR SPECIFIC FOOD PRODUCT",
        ('Commodity', 'Specific Food Products'))

    slice_labels = get_slice_membership(df, label)

    with col1:
        food_select = df[slice_labels]['Entity'].unique()
        entities = st.multiselect(
            "Add food (up to {}): ".format(MAX_BAR),
            food_select,
            max_selections=MAX_BAR
        )

    topBars = get_top_slice(df[slice_labels], entities, MAX_BAR).drop_duplicates()

    #### Selection brushes ####
    # change topBars from wide to long df
    names = ["Normalized water withdrawals","Normalized greenhouse emissions", "Normalized land use", "Normalized eutrophication"]
    longTopBars = topBars.melt(id_vars=['Entity', 'impact_idx'], value_vars=names, var_name='type', value_name='value')
    
    st.markdown('Double click on the legend to select the type of impact or select bar(s).')
    ######################
    #### Stack Charts ####
    ######################
    @st.cache
    def stack_chart():
        # selection brush for type
        selection = alt.selection_single(fields=['type'], bind='legend', name="type")
        #selection brush for entity
        entities_selection = alt.selection_multi(encodings=['y'], name="entities_selection")
        
        return alt.Chart(longTopBars
            ).transform_calculate(
                order=f"-indexof({names}, datum.Origin)"
            ).mark_bar().encode(
                x=alt.X('value:Q'),
                y=alt.Y('Entity:N', sort='-x'),
                color=alt.Color('type:N', scale=alt.Scale(domain=names, range=["#1f77b4", "#2ca02c", "#bd9e39",  "#7f7f7f"])),
                opacity=alt.condition(entities_selection | selection, alt.value(1), alt.value(0.2)),
                order="order:Q"
            ).add_selection(
                selection,
                entities_selection
            ).properties(width=500, title='Impact Index by Food Type')

    chart = stack_chart()
    event_dict = altair_component(altair_chart=chart)

    # subtitle for instruction
   
    ##################
    #### Pie chart ####
    ##################
    # update based on selected
    selected_columns = event_dict.get("Entity")
    if selected_columns:
        #filter topBars by selected columns
        topBars = topBars[topBars['Entity'].isin(selected_columns)]

    # plotly go figure treemap for land
    land_fig = go.Figure(go.Treemap(
        labels=topBars['Entity'],
        parents=[''] * (len(topBars)+1),
        values = topBars['Land use per kilogram'],
        marker_colorscale='ylorbr',
        ))
    land_fig.update_layout(title_text="Land use per kg of food product \
        <br><sup>Land use measured in in meters squared (m²).</sup>")
    land_fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} m²/kg<extra></extra>')
    # add template to textinfo
    land_fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} m²/kg')
    land_fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))

    # plotly go figure treemap for water
    water_fig = go.Figure(go.Treemap(
        labels=topBars['Entity'],
        parents=[''] * (len(topBars) + 1),
        values = topBars['Water withdrawals per kilogram'],
        marker_colorscale='blues',
        ))
    water_fig.update_layout(title_text="Freshwater withdrawals per kg of food product\
        <br><sup>Water withdrawals measured in liters (L).</sup>")
    water_fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} L<extra></extra>')
    # add template to textinfo 
    water_fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} L')
    water_fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))

    # plotly go figure treemap for eutro
    eutro_fig = go.Figure(go.Treemap(
        labels=topBars['Entity'],
        parents=[''] * (len(topBars) + 1),
        values = topBars['Eutrophication per kilogram'],
        marker_colorscale='Greys',
        ))
    eutro_fig.update_layout(title_text="Eutrophication emissions per kg of food product\
        <br><sup>Emissions measured in grams of phosphate equivalents (PO₄eq).</sup>")
    eutro_fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} g<extra></extra>')
    # add template to textinfo 
    eutro_fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} g')
    eutro_fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))

    # plotly go figure treemap for emis
    emis_fig = go.Figure(go.Treemap(
        labels=topBars['Entity'],
        parents=[''] * (len(topBars) + 1),
        values = topBars['Emissions per kilogram'],
        marker_colorscale='algae',
        ))
    emis_fig.update_layout(title_text="Greenhouse gas emissions per kg of food product\
        <br><sup>Emissions measured carbon dioxide equivalents (CO2eq).</sup>")
    emis_fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} kg<extra></extra>')
    # add template to textinfo 
    emis_fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} kg')
    emis_fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.plotly_chart(water_fig, use_container_width=True)
    with col2:
        st.plotly_chart(emis_fig, use_container_width=True)
    with col3:
        st.plotly_chart(land_fig, use_container_width=True)
    with col4:
        st.plotly_chart(eutro_fig, use_container_width=True)

    st.markdown("""
        <style>
        .big-font {
            font-size:22px !important;
        }
        </style>
""", unsafe_allow_html=True)
    # compute percentage reduce when swap recipe 0 to 4
    st.markdown(f"""Swapping from ***{topBars.iloc[0]["Entity"]}*** to ***{topBars.iloc[-1]["Entity"]}*** would reduce """ + \
            f"""the environmental impact index by <span class="big-font">{round((topBars.iloc[0]["impact_idx"] - topBars.iloc[-1]["impact_idx"])/topBars.iloc[0]["impact_idx"]*100, 2)}%<span class="big-font">.""", unsafe_allow_html=True)
    
    landsave = (topBars.iloc[0]["Land use per kilogram"] - topBars.iloc[-1]["Land use per kilogram"])
    watersave= (topBars.iloc[0]["Water withdrawals per kilogram"] - topBars.iloc[-1]["Water withdrawals per kilogram"])
    eutrosave = (topBars.iloc[0]["Eutrophication per kilogram"] - topBars.iloc[-1]["Eutrophication per kilogram"])
    emissave = (topBars.iloc[0]["Emissions per kilogram"] - topBars.iloc[-1]["Emissions per kilogram"])

    # basketball court dimensions https://en.wikipedia.org/wiki/Basketball_court#:~:text=In%20the%20National%20Basketball%20Association,(91.9%20by%2049.2%20ft).
    basketball_court = 28 * 15
    bbal_save = math.ceil(landsave*365/basketball_court)
    
    bball_str = f"""🏀 ⛹ This swap {"helped you protect" if bbal_save > 0 else "costs"} a land surface equal to **{abs(bbal_save)}** basketball courts!"""
    st.markdown("##### " + bball_str, unsafe_allow_html=True)
    # shower use https://home-water-works.org/indoor-use/showers#:~:text=The%20average%20American%20shower%20uses,per%20minute%20(7.9%20lpm).
    # The average American shower uses approximately 15.8 gallons (59.8 liters) and lasts for 7.8 minutes at an average flow rate of 2.1 gallons per minute (7.9 lpm)
    shower = 60
    shower_save = math.ceil(watersave*365/shower)
    shower_str = f"""🚿 🛁 This swap {"helped you save" if shower_save > 0 else "costs"} **{abs(shower_save)}** showers!"""
    st.markdown("##### " + shower_str, unsafe_allow_html=True)

    # car emissions https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle#:~:text=typical%20passenger%20vehicle%3F-,A%20typical%20passenger%20vehicle%20emits%20about%204.6%20metric%20tons%20of,8%2C887%20grams%20of%20CO2.
    # 0.404 kg of CO2 per mile
    # 371 miles between pit and nyc
    car = 0.404 * 371
    car_save = math.ceil(emissave*365/car)
    car_str = f"""🚗 🚙 This swap {"helped you save" if car_save > 0 else "costs"} **{abs(car_save)}** car trips between Pittsburgh and NYC!"""

    st.markdown("##### " + car_str, unsafe_allow_html=True)
    land_percent_save = -1*round(landsave/topBars.iloc[0]["Land use per kilogram"]*100, 2)
    water_percent_save = -1*round(watersave/topBars.iloc[0]["Water withdrawals per kilogram"]*100, 2)
    eutro_percent_save = -1*round(eutrosave/topBars.iloc[0]["Eutrophication per kilogram"]*100, 2)
    emis_percent_save = -1*round(emissave/topBars.iloc[0]["Emissions per kilogram"]*100, 2)
    prefix_land = "+" if land_percent_save > 0 else ""
    prefix_water = "+" if water_percent_save > 0 else ""
    prefix_eutro = "+" if eutro_percent_save > 0 else ""
    prefix_emis = "+" if emis_percent_save > 0 else ""
    cols = st.columns(4)
    with cols[0]:
        st.write(f"""**Water withdrawals:**""")
        st.subheader(f"""**{prefix_water}{water_percent_save}** %""")
    with cols[1]:
        st.write(f"""**Land use:**""")
        st.subheader(f"""**{prefix_land}{land_percent_save}** %""")
    with cols[2]:
        st.write(f"""**Greenhouse gas emissions:**""")
        st.subheader(f"""**{prefix_emis}{emis_percent_save}** %""")
    with cols[3]:
        st.write(f"""**Eutrophication:**""")
        st.subheader(f"""**{prefix_eutro}{eutro_percent_save}** %""")

    st.write(""" *Given that a basketball court is [28m x 15m](https://en.wikipedia.org/wiki/Basketball_court#:~:text=In%20the%20National%20Basketball%20Association,(91.9%20by%2049.2%20ft)),"""+\
    """ an average American shower is [60L lasts for 7.8 minutes](https://home-water-works.org/indoor-use/showers#:~:text=The%20average%20American%20shower%20uses,per%20minute%20(7.9%20lpm)),"""+\
     """ and average average passenger vehicle emission is [0.404kg](https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle#:~:text=typical%20passenger%20vehicle%3F-,A%20typical%20passenger%20vehicle%20emits%20about%204.6%20metric%20tons%20of,8%2C887%20grams%20of%20CO2.) of CO2 per mile,"""+\
     """ distance between PIT and NYC is [371 miles](https://www.google.com/search?q=distance+between+pittsburgh+and+nyc&rlz=1C5CHFA_enUS960US960&oq=distance+between+pittsburgh+and+nyc&aqs=chrome..69i57j0i390l4.13342j0j7&sourceid=chrome&ie=UTF-8), """ +\
        "and that you make this swap everyday for a year.")

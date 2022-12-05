import streamlit as st
import pandas as pd
import altair as alt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_vega_lite import altair_component
import numpy as np
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

    topBars = get_top_slice(df[slice_labels], entities, MAX_BAR)

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
    eutro_fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} kgPO₄eq')
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
    emis_fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} kgCO2eq')
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
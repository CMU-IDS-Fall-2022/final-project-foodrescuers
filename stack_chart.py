import streamlit as st
import pandas as pd
import altair as alt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_vega_lite import altair_component
import numpy as np
@st.cache
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
@st.cache
def get_top_slice(df, entities, maxBarCount):
    # sort top MAX_BAR item df, but leave spots for selected food items
    topBars = df.sort_values(by=['impact_idx'], ascending=False).head(maxBarCount -len(entities))
    # add food select to top10 using concat
    topBars = pd.concat([topBars, df[df['Entity'].isin(entities)]])
    # sort by impact index
    topBars = topBars.sort_values(by=['impact_idx'], ascending=False)
    return topBars
#############
# MAIN CODE #
#############

def stack_chart(df):
    MAX_BAR = 10
    # compute food impact index by normalizing each column
    col1, col2 = st.columns(2)
    
    with col2:
        label = st.radio(
        "COMMODITY OR SPECIFIC FOOD PRODUCT",
        ('Commodity', 'Specific Food Products'))

    slice_labels = get_slice_membership(df, label)
    st.write("The sliced dataset contains {} elements".format(slice_labels.sum()))

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
    longTopBars = topBars.melt(id_vars=['Entity', 'impact_idx'], value_vars=['norm_land', 'norm_water', 'norm_eutro', 'norm_emis'], var_name='type', value_name='value')
    

    ######################
    #### Stack Charts ####
    ######################
    # plotly stack chart with longTopBars horizontal
    # fig = go.Figure()
    # fig.add_trace(go.Bar(
    #     y=longTopBars[longTopBars['type'] == 'norm_land']['Entity'],
    #     x=longTopBars[longTopBars['type'] == 'norm_land']['value'],
    #     name='Land',
    #     orientation='h',
    #     marker_color='rgb(55, 83, 109)'
    # ))
    # fig.add_trace(go.Bar(
    #     y=longTopBars[longTopBars['type'] == 'norm_water']['Entity'],
    #     x=longTopBars[longTopBars['type'] == 'norm_water']['value'],
    #     name='Water',
    #     orientation='h',
    #     marker_color='rgb(26, 118, 255)'
    # ))
    # fig.add_trace(go.Bar(
    #     y=longTopBars[longTopBars['type'] == 'norm_eutro']['Entity'],
    #     x=longTopBars[longTopBars['type'] == 'norm_eutro']['value'],
    #     name='Eutrophication',
    #     orientation='h',
    #     marker_color='rgb(255, 65, 54)'
    # ))
    # fig.add_trace(go.Bar(
    #     y=longTopBars[longTopBars['type'] == 'norm_emis']['Entity'],
    #     x=longTopBars[longTopBars['type'] == 'norm_emis']['value'],
    #     name='Climate Change',
    #     orientation='h',
    #     marker_color='rgb(255, 128, 14)'
    # ))
    # fig.update_layout(barmode='stack', title='Impact Index by Food Type', xaxis_title='Impact Index', yaxis_title='Food Type')
    
    fig = px.bar(longTopBars, x="value", y="Entity", color="type", orientation='h', title='Impact Index by Food Type', labels={'value':'Impact Index', 'Entity':'Food Type'})
    
    fig.update_layout(clickmode="event+select")
    st.write(fig.data)
    for figure in fig.data:
        figure.update(
            selected=dict(marker=dict(opacity=1.0)),
            unselected=dict(marker=dict(opacity=0.25)),
        )
    # selected_points = plotly_events(fig)

    #update opacity of fig
    for figure in fig.data:
        figure.update(
            selected=dict(marker=dict(opacity=1.0)),
            unselected=dict(marker=dict(opacity=0.25)),
        )
    st.write(fig)
    # # update clickmode
    # st.write(selected_points)

    @st.cache
    def stack_chart():
        # selection brush for type
        selection = alt.selection_single(fields=['type'], bind='legend', name="type")
        #selection brush for entity
        entities_selection = alt.selection_multi(encodings=['y'], name="entities_selection")
        
        return alt.Chart(longTopBars
            ).mark_bar().encode(
                x=alt.X('value:Q'),
                y=alt.Y('Entity:N', sort='-x'),
                color='type:N',
                opacity=alt.condition(entities_selection | selection, alt.value(1), alt.value(0.2))
            ).add_selection(
                selection,
                entities_selection
            ).properties(width=500, title='Impact Index by Food Type')

    chart = stack_chart()
    
    event_dict = altair_component(altair_chart=chart)
    
    #TODO: rename legend to be name instead of variable name
    #TODO: Change color of legend to match color of treemap

    # subtitle for instruction
    st.markdown('Double click on the legend to select the type of impact or select bar(s).')

    
    ##################
    #### Tree Map ####
    ##################
    selected_columns = event_dict.get("Entity")
    if selected_columns:
        #filter topBars by selected columns
        topBars = topBars[topBars['Entity'].isin(selected_columns)]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # plotly go figure treemap for land
        fig = go.Figure(go.Treemap(
            labels=topBars['Entity'],
            parents=[''] * (len(topBars)+1),
            values = topBars['Land use per kilogram'],
            marker_colorscale='ylorbr',
            ))
        fig.update_layout(title_text="Land use per kg of food product \
            <br><sup>Land use measured in in meters squared (m²).</sup>")
        fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} m²/kg<extra></extra>')
        # add template to textinfo
        fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} m²/kg')
        fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # plotly go figure treemap for water
        fig = go.Figure(go.Treemap(
            labels=topBars['Entity'],
            parents=[''] * (len(topBars) + 1),
            values = topBars['Water withdrawals per kilogram'],
            marker_colorscale='blues',
            ))
        fig.update_layout(title_text="Freshwater withdrawals per kg of food product\
            <br><sup>Water withdrawals measured in liters (L).</sup>")
        fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} L<extra></extra>')
        # add template to textinfo 
        fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} L')
        fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        # plotly go figure treemap for eutro
        fig = go.Figure(go.Treemap(
            labels=topBars['Entity'],
            parents=[''] * (len(topBars) + 1),
            values = topBars['Eutrophication per kilogram'],
            marker_colorscale='algae',
            ))
        fig.update_layout(title_text="Eutrophication emissions per kg of food product\
            <br><sup>Emissions measured in grams of phosphate equivalents (PO₄eq).</sup>")
        fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} g<extra></extra>')
        # add template to textinfo 
        fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} g')
        fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        # plotly go figure treemap for emis
        fig = go.Figure(go.Treemap(
            labels=topBars['Entity'],
            parents=[''] * (len(topBars) + 1),
            values = topBars['Emissions per kilogram'],
            marker_colorscale='reds',
            ))
        fig.update_layout(title_text="Greenhouse gas emissions per kg of food product\
            <br><sup>Emissions measured carbon dioxide equivalents (CO2eq).</sup>")
        fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} kg<extra></extra>')
        # add template to textinfo 
        fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} kg')
        fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)

    # TODO: change between single select view and multi select view to update the treemap
    # Basically linking multi view between the two charts. Selection are already created.
    # Just need to display the values

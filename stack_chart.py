import streamlit as st
import pandas as pd
import altair as alt
import pandas as pd
import plotly.graph_objects as go
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
    value_vars = ['Normalized land use', 'Normalized water withdrawals', 'Normalized eutro', 'Normalized greenhouse emissions']
    longTopBars = topBars.melt(id_vars=['Entity', 'impact_idx'], value_vars=value_vars, var_name='type', value_name='value')
    # selection brush for type
    selection = alt.selection_single(fields=['type'], bind='legend')
    #selection brush for entity
    entities_selection = alt.selection_multi(encodings=['y'])

    ######################
    #### Stack Charts ####
    ######################
    
    stack_chart = alt.Chart(longTopBars
    ).mark_bar().encode(
        x=alt.X('value:Q'),
        y=alt.Y('Entity:N', sort='-x'),
        # color=alt.Color('type:N',
        #            scale=alt.Scale(
        #     domain=['Normalized eutro', 'Normalized greenhouse emissions', 'Normalized land use', 'Normalized water withdrawals'],
        #     range=['pink', 'green', 'orange', 'blue'])),
        color=alt.Color('type:N', scale=alt.Scale(domain=value_vars, range=["orange", "blue", "pink", "green"])),
        opacity=alt.condition(entities_selection & selection, alt.value(1), alt.value(0.2)),
        tooltip='type:N'
    ).add_selection(
        selection,
        entities_selection
    )

    # subtitle for instruction
    st.markdown("The type of carbon footprint is normalized against the max for that type")
    st.markdown('Double click on the legend to select the type of impact or select bar(s).')
    # st.altair_chart(stack_chart, use_container_width=True)

    
    ##################
    #### Pie chart ####
    ##################

    domain = list(topBars["Entity"].unique()) #+ list(topBars["Entity"].unique())
    # scheme = 'category10'

    size = 200
    land_pie = alt.Chart(topBars, title="Land use (m²) per kilogram").mark_arc().encode(
        theta='Land use per kilogram:Q',
        color=alt.Color('Entity:N', scale=alt.Scale(domain=domain, scheme='oranges')),
        tooltip=['Entity', 'Land use per kilogram:Q']
    ).transform_filter(
        entities_selection
    ).properties(
        width=size,
        height=size
    )

    water_pie = alt.Chart(topBars, title="Water withdrawals (L) per kilogram").mark_arc().encode(
        theta='Water withdrawals per kilogram:Q',
        color=alt.Color('Entity:N', scale=alt.Scale(domain=domain, scheme='blues')),
        tooltip=['Entity', 'Water withdrawals per kilogram:Q']
    ).transform_filter(
        entities_selection
    ).properties(
        width=size,
        height=size
    )

    eutro_pie = alt.Chart(topBars, title="Eutrophication (PO₄eq) per kilogram").mark_arc().encode(
        theta='Eutrophication per kilogram:Q',
        color=alt.Color('Entity:N', scale=alt.Scale(domain=domain, scheme='redpurple')),
        tooltip=['Entity', 'Land use per kilogram:Q']
    ).transform_filter(
        entities_selection
    ).properties(
        width=size,
        height=size
    )

    emis_pie = alt.Chart(topBars, title="Greenhouse gas emissions use (kg) per kilogram").mark_arc().encode(
        theta='Emissions per kilogram:Q',
        color=alt.Color('Entity:N', scale=alt.Scale(domain=domain, scheme='greens')),
        tooltip=['Entity', 'Emissions per kilogram:Q']
    ).transform_filter(
        entities_selection
    ).properties(
        width=size,
        height=size
    )
    
    st.write((stack_chart & (eutro_pie | emis_pie | land_pie | water_pie).resolve_scale(color='independent')).resolve_scale(color='independent'))
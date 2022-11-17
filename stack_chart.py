import streamlit as st
import pandas as pd
import altair as alt
import pandas as pd
import plotly.express as px
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
    # if entities:
    #     labels &= df['Entity'].isin(entities)
    # ... complete this function for the other demographic variables
    return labels

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

    # sort top MAX_BAR item df, but leave spots for selected food items
    topBars = df[slice_labels].sort_values(by=['impact_idx'], ascending=False).head(11-len(entities))
    # add food select to top10
    topBars = topBars.append(df[slice_labels][df[slice_labels]['Entity'].isin(entities)])
    # sort by impact index
    topBars = topBars.sort_values(by=['impact_idx'], ascending=False)
    stack_chart = alt.Chart(topBars).transform_fold(
        ["norm_land",
        "norm_water",
        "norm_eutro",
        "norm_emis"
        ],
        as_=['column', 'value']
    ).mark_bar().encode(
        x=alt.X('sum(value):Q'),
        y=alt.Y('Entity:N', sort='-x'),
        color='column:N'
    )
    st.altair_chart(stack_chart, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # plotly tree map of land using topBars
        fig = px.treemap(
            topBars, path=['Entity'],
            values='Land use per kilogram',
            hover_data=['Entity', 'Land use per kilogram'])

        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)
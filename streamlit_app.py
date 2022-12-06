import streamlit as st
import pandas as pd
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from stqdm import stqdm
import Levenshtein as lev
import math
from stack_chart import * # implementation file of stack chart
from impact import impact_calculate

@st.cache()  # add caching so we load the data only once
def load_data():
    df = pd.read_csv("data/Food_Impact.csv")
    # normalized per categories then divide by 4 and mult by 100 (--> mult 25)
    df['impact_idx'] = (df['Emissions per kilogram'] / df['Emissions per kilogram'].max() + \
        df['Land use per kilogram'] / df['Land use per kilogram'].max() + \
        df['Water withdrawals per kilogram'] / df['Water withdrawals per kilogram'].max() + \
        df['Eutrophication per kilogram'] / df['Eutrophication per kilogram'].max()) * 25
    df["Normalized land use"] = df['Land use per kilogram'] / df['Land use per kilogram'].max() * 25
    df["Normalized water withdrawals"] = df['Water withdrawals per kilogram'] / df['Water withdrawals per kilogram'].max() * 25
    df["Normalized eutrophication"] = df['Eutrophication per kilogram'] / df['Eutrophication per kilogram'].max() * 25
    df["Normalized greenhouse emissions"] = df['Emissions per kilogram'] / df['Emissions per kilogram'].max() * 25

    return df
@st.cache()
def load_recipes():
    dfr = pd.read_csv("reciperec/RAW_recipes.csv")
    dfr["ingredients_fmt"] = dfr["ingredients"].apply(parsein)
    dfr.ingredients_fmt.values.astype('U')
    return dfr
@st.cache()
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

# data source: https://www.fao.org/platform-food-loss-waste/flw-data/en/
fao_df_raw = pd.read_csv("data/FAO_data.csv")
fao_df = fao_df_raw[['year','country','loss_percentage','activity','food_supply_stage','commodity']]
fao_df = fao_df.sort_values(by = ['year','country'], ascending=True)

#############
# MAIN CODE #
#############

st.set_page_config(layout="wide") # wide page format
st.title("Food Rescuers")

with st.spinner(text="Loading data..."):
    df = load_data()

###############
# INTRO SECTION #
###############

st.title('Food loss around the world')
st.write('Food loss has impacted the world in many ways. Select a country and year below to see the impacts of food waste around the world for a given country and time.')
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
    date_selected = st.selectbox('What year were you born?', date_options, index=23)
    df_year_selected = fao_df[fao_df['year'] == date_selected]
    
    # filter to year and country selected
    df_filtered = fao_df[fao_df['year'] >= date_selected]
    df_filtered = df_filtered[fao_df['country'].isin(country_choice)]

st.write('Based on the Country and Years you were interested:')
st.dataframe(df_filtered.sort_values('year',
            ascending=False).reset_index(drop=True))

## HISTOGRAM 
fig = plt.figure(figsize=(10,4))
plt.xticks(rotation=60)
sns.countplot(data=df_filtered, x="year")
st.write(fig)

# SCATTERPLOT FUNCTIONALITY
st.write('Scatterplot of food loss per year')
## scatterplot
fig, ax = plt.subplots()
## need to fix to only show integers
plt.xticks(rotation=60)
plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.scatter(x='year',
           y='loss_percentage', 
           data=df_filtered)
st.pyplot(fig)


###############
# STACK CHART #
###############
stack_chart_frame(df)


###############
# RECIPE PAGE #
###############

def parsein(ings):
    return ings[1:-1].replace("'","").replace(",","")

def parsein2(ings):
    return ings[1:-1].replace("'","").split(",")


def calc_leven(row,ing):
	col2 = str(row["description"])
	return lev.distance(col2,ing)

def calc_leven2(row,ing):
	col2 = str(row["Entity"]).lower()
	return lev.distance(col2,ing)

@st.cache
def get_gramdf():
    return pd.read_csv("data/foodandgrams.csv")

@st.cache
def get_recipes(gramdf, top, dfr):
    suggested_recipes = []
    for i,t in enumerate(top):
        recipe_impact = {}
        title = dfr.iloc[t]["name"]
        totalemissions = 0
        totaleutrophication = 0
        totallanduse = 0
        totalwaterscarcity = 0
        totalwaterwithdrawals = 0
        ingrs = dfr.iloc[t]["ingredients"]
        for ingredient in parsein2(ingrs):
            grams = gramdf.loc[gramdf.apply(calc_leven,axis=1,ing=ingredient).idxmin()]["gram_weight"]
            closeingredient = df.loc[df.apply(calc_leven2,axis=1,ing=ingredient).idxmin()]["Entity"]
            totalemissions += impact_calculate(closeingredient,grams).iloc[0]["Emissions per kilogram"]
            totaleutrophication += impact_calculate(closeingredient,grams).iloc[0]["Eutrophication per kilogram"]
            totallanduse += impact_calculate(closeingredient,grams).iloc[0]["Land use per kilogram"]
            totalwaterscarcity = impact_calculate(closeingredient,grams).iloc[0]["Water scarcity per kilogram"]
            totalwaterwithdrawals = impact_calculate(closeingredient,grams).iloc[0]["Water withdrawals per kilogram"]
        recipe_impact["title"] = title
        recipe_impact["totalemissions"] = totalemissions
        recipe_impact["totaleutrophication"] = totaleutrophication
        recipe_impact["totallanduse"] = totallanduse
        recipe_impact["totalwaterscarcity"] = totalwaterscarcity
        recipe_impact["totalwaterwithdrawals"] = totalwaterwithdrawals
        
        all_ingredients = ""
        ingredients = parsein2(ingrs)
        for i, ingredient in enumerate(ingredients):
            if i == 0:
                all_ingredients += ingredient
            else:
                all_ingredients += ", " +ingredient
        recipe_impact["ingredients"] = all_ingredients
        steps = dfr.iloc[t]["steps"][2:-2].split("', '")
        all_steps = ""
        for i,step in enumerate(steps):
            all_steps += str(i+1)+". "+step + "\n"
        recipe_impact["steps"] = all_steps
        
        suggested_recipes.append(recipe_impact)
    return suggested_recipes

def compute(dfr, inputing):
    tfidf = TfidfVectorizer()
    tfidfing = tfidf.fit_transform(dfr["ingredients_fmt"])
    inputtfidf = tfidf.transform([inputing])
    cos_sim = map(lambda x: cosine_similarity(inputtfidf, x), tfidfing)
    scores = list(stqdm(cos_sim,total=len(dfr["ingredients_fmt"])))
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
    return top

st.title("How can you make a difference?")
st.subheader("Find recipes with your existing food ingredients and reduce food waste!")

inputing = st.text_input("Enter your ingredients below:",
    value="pizza beef eggs milk salt and pepper cheese")

if st.button('Find recipes'):
    dfr = load_recipes()

    # expensive compute
    with st.spinner(text="Finding the best recipe given your ingredients. This may take a while...  🤖"):
        top = compute(dfr, inputing)

    st.write("Suggested recipes: ")

    gramdf = get_gramdf()
    
    suggested_recipes = get_recipes(gramdf, top, dfr)
    
    # #cache for testing
    # suggested_recipes = [{'title': 'calzones', 'totalemissions': 1.6031170937774613, 'totaleutrophication': 6.052143668111411, 'totallanduse': 1.9244491661825236, 'totalwaterscarcity': 2562.8521406654063, 'totalwaterwithdrawals': 124.23803330225903, 'ingredients': 'frozen bread dough,  beef,  mushroom,  pizza sauce,  pizza cheese', 'steps': '1. thaw bread dough\n2. when it is able to be sliced , cut each loaf into 6 sections\n3. place on greased cookie sheet and allow to rise to its capacity\n4. while dough is rising , brown meat and mushrooms\n5. when dough is raised , roll out each section on floured board\n6. place 1 tablespoon meat mixture on half the dough\n7. add pizza sauce and pizza cheese , as much as you like\n8. fold in half and pinch the edges of the dough pieces together\n9. lay on cookie sheet\n10. bake at 300 degrees fahrenheit until done\', "may be baked at a higher temperature , if oven isn\'t too hot", \'bake until bread dough is not doughy on inside\n11. can make vegetable calzones , too\n'}, {'title': 'cheesy pizza macaroni', 'totalemissions': 3.6974012477870457, 'totaleutrophication': 12.717593176671729, 'totallanduse': 5.0933151576428095, 'totalwaterscarcity': 1068.8783898694896, 'totalwaterwithdrawals': 51.4006915607653, 'ingredients': 'lean ground beef,  macaroni and cheese mix,  milk,  pizza sauce,  cheddar cheese,  mozzarella cheese', 'steps': '1. in a large skillet , cook the beef until no longer pink\n2. drain\n3. prepare macaroni and cheese according to package directions , using 1 / 3 cup milk and omitting margarine\n4. spread 1 / 2 the pizza sauce into a 11x7 inch baking dish\n5. layer with half the beef , half the macaroni and cheese and half the cheddar and mozzarella cheeses\n6. repeat layers\n7. bake , uncovered , at 350 degrees for 25-30 minutes or until bubbly\n'}, {'title': 'carmen jackson s swedish eggs rara', 'totalemissions': 0.45456513228531925, 'totaleutrophication': 1.747614754168688, 'totallanduse': 1.0661947793971038, 'totalwaterscarcity': 2373.050568538462, 'totalwaterwithdrawals': 40.394188321846165, 'ingredients': 'eggs,  milk,  butter,  salt and pepper', 'steps': '1. beat the eggs and the milk or cream\n2. over low heat melt the butter in a heavy frying pan\n3. add the eggs\n4. slowly keep scraping the bottom of the pan with a large spoon\', "don\'t walk away", \'when the eggs are creamy just set serve\n'}, {'title': 'cheeseburger pizza', 'totalemissions': 2.165037118536642, 'totaleutrophication': 9.680219216781012, 'totallanduse': 4.000360724297197, 'totalwaterscarcity': 3544.2251299812497, 'totalwaterwithdrawals': 49.5912480724375, 'ingredients': 'ground beef,  onion,  garlic cloves,  salt,  pepper,  pizza crust,  pizza sauce,  cooked bacon,  dill pickle,  mozzarella cheese,  cheddar cheese,  parmesan cheese,  italian seasoning', 'steps': '1. in a skillet , cook beef , onion , garlic , salt , and pepper until meat is browned\n2. drain and set aside\n3. place crust on an ungreased 12-inch pizza pan\n4. spread with pizza sauce\n5. top with beef mixture , bacon , pickles , and cheeses\n6. sprinkle with italian seasoning\n7. bake at 450 degrees for 9-15 minutes or until cheese is melted\n'}, {'title': 'cheese omelette', 'totalemissions': 0.6588981322853192, 'totaleutrophication': 2.8016917541686883, 'totallanduse': 2.057533779397104, 'totalwaterscarcity': 126.53581418635294, 'totalwaterwithdrawals': 5.594092500218692, 'ingredients': 'eggs,  cheese,  salt and pepper,  butter', 'steps': '1. whisk the eggs till light and fluffy\n2. add cheese , salt and pepper\n3. mix well\n4. heat a 7 inch non-stick skillet and add butter\n5. as the butter begins to smoke , lower heat and pour the beaten egg mixture\n6. cook covered for a minute\n7. fold over and serve immediately\n'}]
 
    # create df from suggested_recipes
    details = {}
    for recipe in suggested_recipes:
        details["Recipe"] = details.get('Recipe', []) + [recipe["title"]]
        details["totalemissions"] = details.get('totalemissions', []) + [recipe["totalemissions"]]
        details["totaleutrophication"] = details.get('totaleutrophication', []) + [recipe["totaleutrophication"]]
        details["totallanduse"] = details.get('totallanduse', []) + [recipe["totallanduse"]]
        details["totalwaterscarcity"] = details.get('totalwaterscarcity', []) + [recipe["totalwaterscarcity"]]
        details["totalwaterwithdrawals"] = details.get('totalwaterwithdrawals', []) + [recipe["totalwaterwithdrawals"]]
        details["steps"] = details.get('steps', []) + [recipe["steps"]]
        details["ingredients"] = details.get('ingredients', []) + [recipe["ingredients"]]
    df = pd.DataFrame(details, columns = ['Recipe', 'totalemissions', 'totaleutrophication', 'totallanduse', 'totalwaterscarcity', 'totalwaterwithdrawals', 'steps', 'ingredients'])
    # normalized per categories then divide by 4 and mult by 100 (--> mult 25)
    df['impact_idx'] = (df['totalemissions'] / df['totalemissions'].max() + \
        df['totallanduse'] / df['totallanduse'].max() + \
        df['totalwaterwithdrawals'] / df['totalwaterwithdrawals'].max() + \
        df['totaleutrophication'] / df['totaleutrophication'].max()) * 25
    df["Normalized land use"] = df['totallanduse'] / df['totallanduse'].max() * 25
    df["Normalized water withdrawals"] = df['totalwaterwithdrawals'] / df['totalwaterwithdrawals'].max() * 25
    df["Normalized eutrophication"] = df['totaleutrophication'] / df['totaleutrophication'].max() * 25
    df["Normalized greenhouse emissions"] = df['totalemissions'] / df['totalemissions'].max() * 25

    # selection brush for type
    topBars = df.sort_values(by=['impact_idx'], ascending=False)
    names = ["Normalized water withdrawals","Normalized greenhouse emissions", "Normalized land use", "Normalized eutrophication"]
    longTopBars = topBars.melt(id_vars=['Recipe', 'impact_idx'], value_vars=names, var_name='type', value_name='value')
    

    #selection brush for entity
    selection = alt.selection_single(fields=['type'], bind='legend')
    recipe_chart = alt.Chart(longTopBars
            ).transform_calculate(
                order=f"-indexof({names}, datum.Origin)"
            ).mark_bar().encode(
                x=alt.X('value:Q'),
                y=alt.Y('Recipe:N', sort='-x'),
                color=alt.Color('type:N', scale=alt.Scale(domain=names, range=["#1f77b4", "#2ca02c", "#bd9e39",  "#7f7f7f"])),
                opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
                order="order:Q",
            ).add_selection(
                selection,
            ).properties(width=500, title='Impact Index by Food Type')
    st.altair_chart(recipe_chart, use_container_width=True)

    # plotly go figure treemap for land
    land_fig = go.Figure(go.Treemap(
        labels=topBars['Recipe'],
        parents=[''] * (len(topBars)+1),
        values = topBars['totallanduse'],
        marker_colorscale='ylorbr',
        ))
    land_fig.update_layout(title_text="Land use per recipe\
        <br><sup>Land use measured in in meters squared (m²).</sup>")
    land_fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} m²/kg<extra></extra>')
    # add template to textinfo
    land_fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} m²/kg')
    land_fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))

    # plotly go figure treemap for water
    water_fig = go.Figure(go.Treemap(
        labels=topBars['Recipe'],
        parents=[''] * (len(topBars) + 1),
        values = topBars['totalwaterwithdrawals'],
        marker_colorscale='blues',
        ))
    water_fig.update_layout(title_text="Freshwater withdrawals per recipe\
        <br><sup>Water withdrawals measured in liters (L).</sup>")
    water_fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} L<extra></extra>')
    # add template to textinfo 
    water_fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} L')
    water_fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))

    # plotly go figure treemap for eutro
    eutro_fig = go.Figure(go.Treemap(
        labels=topBars['Recipe'],
        parents=[''] * (len(topBars) + 1),
        values = topBars['totaleutrophication'],
        marker_colorscale='Greys',
        ))
    eutro_fig.update_layout(title_text="Eutrophication emissions per recipe\
        <br><sup>Emissions measured in grams of phosphate equivalents (PO₄eq).</sup>")
    eutro_fig.update_traces(hovertemplate='<b>%{label}</b><br>%{value} g<extra></extra>')
    # add template to textinfo 
    eutro_fig.update_traces(texttemplate='<b>%{label}</b><br>%{value} g')
    eutro_fig.update_layout(margin =dict(t=50, l=25, r=25, b=25))

    # plotly go figure treemap for emis
    emis_fig = go.Figure(go.Treemap(
        labels=topBars['Recipe'],
        parents=[''] * (len(topBars) + 1),
        values = topBars['totalemissions'],
        marker_colorscale='algae',
        ))
    emis_fig.update_layout(title_text="Greenhouse gas emissions per recipe\
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

    # recipe steps
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.subheader(topBars.iloc[i]["Recipe"])
            st.markdown('**Ingredients:** ' + topBars.iloc[i]["ingredients"])
            # st.write(topBars.iloc[i]["ingredients"])
            st.write(topBars.iloc[i]["steps"])

    # Reflection
    st.header('Check this out!')
    st.markdown("""
        <style>
        .big-font {
            font-size:22px !important;
        }
        </style>
""", unsafe_allow_html=True)
    # compute percentage reduce when swap recipe 0 to 4
    st.markdown(f"""Swapping from recipe ***{topBars.iloc[0]["Recipe"]}*** to recipe ***{topBars.iloc[4]["Recipe"]}*** would reduce """ + \
            f"""the environmental impact index by <span class="big-font">{round((topBars.iloc[0]["impact_idx"] - topBars.iloc[4]["impact_idx"])/topBars.iloc[0]["impact_idx"]*100, 2)}%<span class="big-font">.""", unsafe_allow_html=True)
    
    landsave = (topBars.iloc[0]["totallanduse"] - topBars.iloc[4]["totallanduse"])
    watersave= (topBars.iloc[0]["totalwaterwithdrawals"] - topBars.iloc[4]["totalwaterwithdrawals"])
    eutrosave = (topBars.iloc[0]["totaleutrophication"] - topBars.iloc[4]["totaleutrophication"])
    emissave = (topBars.iloc[0]["totalemissions"] - topBars.iloc[4]["totalemissions"])

    # basketball court dimensions https://en.wikipedia.org/wiki/Basketball_court#:~:text=In%20the%20National%20Basketball%20Association,(91.9%20by%2049.2%20ft).
    basketball_court = 28 * 15
    bball_str = f"""🏀 ⛹ This swap helped you protect a land surface equal to **{math.ceil(landsave*365/basketball_court)}** basketball courts!"""
    st.markdown("##### " + bball_str, unsafe_allow_html=True)
    # shower use https://home-water-works.org/indoor-use/showers#:~:text=The%20average%20American%20shower%20uses,per%20minute%20(7.9%20lpm).
    # The average American shower uses approximately 15.8 gallons (59.8 liters) and lasts for 7.8 minutes at an average flow rate of 2.1 gallons per minute (7.9 lpm)
    shower = 60
    shower_str = f"""🚿 🛁 This swap helped you save **{math.ceil(watersave*365/shower)}** showers!"""
    st.markdown("##### " + shower_str, unsafe_allow_html=True)

    # car emissions https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle#:~:text=typical%20passenger%20vehicle%3F-,A%20typical%20passenger%20vehicle%20emits%20about%204.6%20metric%20tons%20of,8%2C887%20grams%20of%20CO2.
    # 0.404 kg of CO2 per mile
    # 371 miles between pit and nyc
    car = 0.404 * 371
    car_str = f"""🚗 🚙 This swap helped you save **{math.ceil(emissave*365/car)}** car trips between Pittsburgh and NYC!"""
    st.markdown("##### " + car_str, unsafe_allow_html=True)

    cols = st.columns(4)
    with cols[0]:
        st.write(f"""**Water withdrawals:**""")
        st.subheader(f"""**-{round(watersave/topBars.iloc[0]["totalwaterwithdrawals"]*100, 2)}** %""")
    with cols[1]:
        st.write(f"""**Land use:**""")
        st.subheader(f"""**-{round(landsave/topBars.iloc[0]["totallanduse"]*100, 2)}** %""")
    with cols[2]:
        st.write(f"""**Greenhouse gas emissions:**""")
        st.subheader(f"""**-{round(emissave/topBars.iloc[0]["totalemissions"]*100, 2)}** %""")       
    with cols[3]:
        st.write(f"""**Eutrophication:**""")
        st.subheader(f"""**-{round(eutrosave/topBars.iloc[0]["totaleutrophication"]*100, 2)}** %""")

    st.write(""" *Given that a basketball court is [28m x 15m](https://en.wikipedia.org/wiki/Basketball_court#:~:text=In%20the%20National%20Basketball%20Association,(91.9%20by%2049.2%20ft)),"""+\
    """ an average American shower is [60L lasts for 7.8 minutes](https://home-water-works.org/indoor-use/showers#:~:text=The%20average%20American%20shower%20uses,per%20minute%20(7.9%20lpm)),"""+\
     """ and average average passenger vehicle emission is [0.404kg](https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle#:~:text=typical%20passenger%20vehicle%3F-,A%20typical%20passenger%20vehicle%20emits%20about%204.6%20metric%20tons%20of,8%2C887%20grams%20of%20CO2.) of CO2 per mile,"""+\
     """ distance between PIT and NYC is [371 miles](https://www.google.com/search?q=distance+between+pittsburgh+and+nyc&rlz=1C5CHFA_enUS960US960&oq=distance+between+pittsburgh+and+nyc&aqs=chrome..69i57j0i390l4.13342j0j7&sourceid=chrome&ie=UTF-8), """ +\
        "and that you make this swap everyday for a year.")

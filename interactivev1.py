import altair as alt
import pandas as pd
import streamlit as st
import json
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from PIL import Image
from folium.plugins import MarkerCluster
from folium import IFrame
import base64
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


#Title
st.title("Poutine: A Delicious Mess \nby Mike VerHulst")

poutine_pic = Image.open('poutine_pic.jpg')
st.image(poutine_pic, caption='Poutine', width=700)

#Import data
recipes = pd.read_csv('https://raw.githubusercontent.com/mcverhulst/poutine/main/recipenlg.csv')
derp = recipes.iloc[0]['ingredients']

def clean_ingred(x):
    for i in range(len(x)):
        x[i] = x[i].replace('"','')
    return x

recipes['ingredients'] = recipes['ingredients'].apply(lambda x: x.strip('][').split(', '))
recipes['NER_list'] = recipes['NER'].apply(lambda x: x.strip('][').split(', '))

recipes['ingredients'] = recipes['ingredients'].apply(clean_ingred)
recipes['NER_list'] = recipes['NER_list'].apply(clean_ingred)

curds = ['baking powder']
curd_recipes = recipes[recipes['NER'].str.contains('curds')]
beef = recipes[recipes['NER'].str.contains('beef')]
pork = recipes[recipes['NER'].str.contains('pork')]
bacon = recipes[recipes['NER'].str.contains('bacon')]
chicken = recipes[recipes['NER'].str.contains('chicken')]

def remove_beef_broth(x):
    if ('beef broth'  or 'beef gravy') in x:
        return 1
    else:
        return 0

def remove_chicken_broth(x):
    if 'chicken broth' in x:
        return 1
    else:
        return 0

beef2 = beef.copy()
chicken2 = chicken.copy()

beef2['beef_broth'] = beef2['NER'].apply(remove_beef_broth)
beef_no_broth = beef2[beef2['beef_broth'] == 0]

chicken2['chicken_broth'] = chicken2['NER'].apply(remove_chicken_broth)
chicken_no_broth = chicken2[chicken2['chicken_broth'] == 0]


st.write('''Poutine is made up of 3 simple ingredients: **french fries, gravy, and cheese curds**. This dish was
invented in the Centre-du-Québec region of Quebec in the 1950s and has come to be known as an
iconic Canadian food. According to the Merriam-Webster Dictionary, poutine comes from a
Québécois slang word meaning “mess.”''')


### map
#Referenced: https://stackoverflow.com/questions/39401729/plot-latitude-longitude-points-from-dataframe-on-folium-map-ipython

originals = pd.read_csv('https://raw.githubusercontent.com/mcverhulst/poutine/main/originals.csv')
locations = [(45.9434,-71.9890), (45.8865, -72.5056), (46.1692, -71.8696)]

m = folium.Map(location=[46, -72], zoom_start=7, tiles='CartoDB positron', width=700)

for point in range(0, len(locations)):
    folium.CircleMarker(locations[point], color='red', fill_color='black', radius=5, tooltip=originals['name'][point], popup=originals['name'][point]).add_to(m)
    
st.write('\n')
st.write('\n')
st.write('\n')
st.write('### Who invented poutine?') 
st.write('''The origins of poutine are unknown. However, a few restaurants in the area claim to be the originators of the dish, but no consensus exists. The map below shows where these three restaurants are located.''')
folium_static(m)

rest_ops = list(originals.name.unique())
blurbs = list(originals.blurb.unique())

st.write('\n')
st.write('### Select a restaurant below to learn more about it')
rest_select = st.selectbox('Select a restaurant below to learn more about it', rest_ops, label_visibility='hidden')
if rest_select == rest_ops[0]:
    cafe_ideal = Image.open('cafeideal.jpg')
    st.image(cafe_ideal, caption=blurbs[0], width=700)
if rest_select == rest_ops[1]:
    cafe_ideal = Image.open('le_roy_jucep.jpg')
    st.image(cafe_ideal, caption=blurbs[1], width=700)
if rest_select == rest_ops[2]:
    cafe_ideal = Image.open('petite.jpg')
    st.image(cafe_ideal, caption=blurbs[2], width=700)


### curds
curds = {'Uses cheese curds': len(curd_recipes), 'Uses other cheese': 68}

curds_df = pd.DataFrame.from_dict(curds, orient='index')
curds_df.reset_index(inplace=True)
curds_df.rename(columns={0:'num', 'index': 'has_curds'}, inplace=True)

base = alt.Chart(curds_df).encode(
    theta=alt.Theta("num:Q", stack=True), 
    color=alt.Color("has_curds:N", legend=None),
    tooltip=alt.Tooltip('num', title='num')
)

pie = base.mark_arc(outerRadius=100, color='red')
text = base.mark_text(radius=160, size=15).encode(text="has_curds:N")

curd_viz = (pie + text).properties(title='Percentage of poutine recipes that use cheese curds', width=700)

st.write('\n')
st.write('\n')
st.write('\n')
st.write('''#### Cheese with a squeak''')

st.write('''The key ingredient in poutine is fresh cheese curds. Fresh cheese curds
can last 24 hours before needing to be refrigerated and have a springiness
and squeak as you eat them. After being refrigerated, curds will lose thse
unique properties, leading to subsitutions for more common forms of
cheese such as shredded or block cheese.''')


curd_pic = Image.open('curds.jpg')
st.image(curd_pic, caption='Cheese curds', width=700)

# curd_viz
curd_pic = Image.open('curds_int-01.jpg')
st.image(curd_pic, width=700)


### proteins
proteins = {
    'Chicken': [len(chicken_no_broth)],
    'Beef': [len(beef_no_broth)],
    'Other Pork': [len(pork)],
    'Bacon': [len(bacon)]
}
protein_df = pd.DataFrame.from_dict(proteins, orient='index')
protein_df.reset_index(inplace=True)
protein_df.rename(columns={0:'Recipe Count', 'index': 'protein'}, inplace=True)

s1 = alt.selection_single(on='mouseover')
opacityCondition = alt.condition(s1, alt.value('red'), alt.value('gray'))


protein_viz = alt.Chart(protein_df).mark_bar(color='red').encode(
    alt.Y('protein',
          sort=alt.EncodingSortField(field='Recipe Count', order='descending'),
          axis=alt.Axis(title='Protein')),
    alt.X('Recipe Count'),
    tooltip = ['Recipe Count']
).add_selection(
    s1,
).encode(
    color = opacityCondition
).properties(width=700, height=150, title='Most common proteins found in poutine recipes')

st.write('\n')
st.write('\n')
st.write('\n')
st.write('''#### How about some toppings?''')

st.write('''With only 3 core ingredients, it’s very
common to add additional toppings.
Proteins such as beef and chicken tend to
be the most commonly found additions
to the traditional recipe.''')

protein_viz

protein_ops = ['Beef', 'Chicken', 'Bacon', 'Other Pork']
# blurbs = list(originals.blurb.unique())

st.write('##### Select a protein to get recipe options')
protein_select = st.selectbox('Select a restaurant below to learn more about it', protein_ops, label_visibility='hidden')
if protein_select == protein_ops[0]:
    x = beef_no_broth.sample(5)
    st.write(x[['title', 'link']])
if protein_select == protein_ops[1]:
    x = chicken_no_broth.sample(5)
    st.write(x[['title', 'link']])
if protein_select == protein_ops[2]:
    x = bacon.sample(5)
    st.write(x[['title', 'link']])
if protein_select == protein_ops[3]:
    x = pork.sample(5)
    st.write(x[['title', 'link']])




### iconic
iconic = {'Poutine': 21, 'Maple syrup': 14, 'Lobster': 10}

iconic_df = pd.DataFrame.from_dict(iconic, orient='index')
iconic_df.reset_index(inplace=True)
iconic_df.rename(columns={0:'percent', 'index': 'food'}, inplace=True)

iconic_viz = alt.Chart(iconic_df).mark_bar(color='red').encode(
    alt.Y('food:N',
          sort=alt.EncodingSortField(field='percent', order='descending'),
          axis=alt.Axis(title='Food')),
    alt.X('percent:Q',
         axis=alt.Axis(title='Percentage of surveyed Canadians (2017)')),
    tooltip = ['percent:Q']
).add_selection(
    s1,
).encode(
    color = opacityCondition
).properties(width=700, height=150, title="What is your favorite 'iconic' Canadian Food?")

st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')

st.write('''#### A New Canadian Icon?''')
st.write('''In a 2017 survey, more Canadians
chose poutine as their favorite “iconic”
Canadian food, even beating out maple
syrup.''')

iconic_viz

### map
can = gpd.read_file('https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/canada.geojson')
states = gpd.read_file('https://raw.githubusercontent.com/mcverhulst/poutine/main/us_map2.json')
can = can[['name', 'geometry']]

states = states[['NAME', 'geometry']]
states.rename(columns={'NAME': 'name'},inplace=True)

# states2 = states[(states['name'] != 'Alaska') & (states['name'] != 'Hawaii') & (states['name'] != 'Puerto Rico')]
states2 = states[(states['name'] != 'Hawaii') & (states['name'] != 'Puerto Rico')]

# can2 = can[(can['name'] != 'Nunavut') & (can['name'] != 'Northwest Territories') & (can['name'] != 'Yukon Territory')]

combined = pd.concat([can, states2])

p_list = ['Quebec', 'Newfoundland and Labrador', 'British Columbia', 'New Brunswick', 
          'Nova Scotia', 'Saskatchewan', 'Alberta', 'Prince Edward Island', 'Manitoba', 
          'Ontario', 'Nunavut', 'Northwest Territories', 'Yukon Territory','Washington', 'Oregon','Idaho','Montana','North Dakota', 
          'Minnesota', 'Wisconsin', 'Michigan', 'Illinois', 'Tennessee',
          'Pennsylvania', 'New York', 'Vermont', 'New Hampshire', 'Maine', 
          'Massachusetts', 'Rhode Island', 'Connecticut', 'Alaska']

poutine = combined.loc[combined['name'].isin(p_list)]
combined['poutine'] = np.where(combined["name"].isin(p_list), 1, 0)

new_cities = pd.read_csv('https://raw.githubusercontent.com/mcverhulst/poutine/main/poutine_cities.csv')

m = folium.Map(location=[49.8954, -97.1385], zoom_start=3, tiles='CartoDB positron')

marker_cluster = MarkerCluster().add_to(m)

for point in range(0, len(locations)):
    folium.Marker(locations[point], color='black', fill_color='black', radius=5, tooltip=originals['name'][point], popup=originals['name'][point]).add_to(marker_cluster)

# folium.Choropleth(
#     geo_data = combined,
#     fill_color='gray',
#     opacity=1,
#     highlight=True
# ).add_to(m)

folium.Choropleth(
    geo_data = poutine,
    fill_color='red',
    tooltip=folium.features.GeoJsonTooltip(fields=['name']),
    opacity=1,
    highlight=True
).add_to(m)

style_function = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}
NIL = folium.features.GeoJson(
    combined,
    style_function=style_function, 
    control=False,
    highlight_function=highlight_function, 
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name'],
        aliases=['State/Province Name'],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
    )
).add_to(m)

st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')
st.write('''##### Gaining in Popularity''')
st.write('''In present day, poutine has spread far outside Quebec. Poutine
is commonly found throughout Canada and the northern portions
of the United States.''')
    
st.write("###### Locations in *red* are where poutine can be commonly found or where poutine festivals have been held")
folium_static(m)

st.write('''Gaining popularity
outside Canada,
major poutine festivals
have been hosted in
places like Chicago,
Knoxville, Manchester,
NH, and Rhode Island.''')

### restaurants
rests = pd.read_csv('https://raw.githubusercontent.com/mcverhulst/poutine/main/laPoutine%20rest.csv')
missing = {'year': [2015, 2018, 2020], 'count': [120, 240, 400]}
missing= pd.DataFrame(data=missing)

missing_plot = alt.Chart(missing).mark_line(
    color='red',
    point=alt.OverlayMarkDef(color="black"),
    strokeDash = [4,6]
).encode(
    alt.X('year:N', axis=alt.Axis(title='Year')),
    alt.Y('count:Q',
          axis=alt.Axis(title='Restaurants Participating'))
)

rest_viz = alt.Chart(rests).mark_line(
    color='red',
    point=alt.OverlayMarkDef(color="black")
).encode(
    alt.X('year:N', axis=alt.Axis(title='Year')),
    alt.Y('number:Q',
          axis=alt.Axis(title='Restaurants Participating')),
    tooltip = ['number:Q']
).properties(width=700, height=450,title={
             'text': 'Number of restaurants participating in La Poutine Week by year',
             'subtitle': 'Dotted line indicates estimated values'}
)

st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')
st.write('''#### La Poutine Week''')
st.write('''La Poutine Week is the largest poutine
festival in the world. Beginning in
Montreal in 2013 with only 30
restaurants, it has since exploded to the
United States and even as far as
Australia. The 2022 festival had over
800 restaurants participate.''')


rest_viz+missing_plot

### mapping la poutine week

st.write('##### Use the slider to show cities that have participated in La Poutine Week each year')
slider = st.slider('Select a year', min_value=2013, max_value=2019, value=2013, step=1, label_visibility="visible")
to_plot = new_cities[new_cities[str(slider)] == 1]

fig = px.scatter_mapbox(to_plot, lat="lat", lon="lon", hover_name="city",
                        color_discrete_sequence=["red"], zoom=3, height=300)
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=0.5,
    mapbox_center={"lat": 49.8954, "lon": -97.1385},
    width=700,
    height=500,
)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})




st.plotly_chart(fig)

if slider == 2013:
    st.write('The number of restaurants participating in *La Poutine Week* this year is: **30**')
if slider == 2014:
    st.write('The number of restaurants participating in *La Poutine Week* this year is: **100**')
if slider == 2015:
    st.write('The number of restaurants participating in *La Poutine Week* this year is: **120**')
if slider == 2016:
    st.write('The number of restaurants participating in *La Poutine Week* this year is: unknown')
if slider == 2017:
    st.write('The number of restaurants participating in *La Poutine Week* this year is: unknown')
if slider == 2018:
    st.write('The number of restaurants participating in *La Poutine Week* this year is: **240**')
if slider == 2019:
    st.write('The number of restaurants participating in *La Poutine Week* this year is: unknown')

    
st.write('\n')
st.write('\n')
st.write('\n')
st.write('\n')
st.write('''Source: https://en.wikipedia.org/wiki/Poutine''')

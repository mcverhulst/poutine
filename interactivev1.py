# Mike VerHulst (uniqname: verhulst)
# si649f22 altair transforms 2

# imports we will use
import altair as alt
import pandas as pd
import streamlit as st
import json
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from PIL import Image


#Title
st.title("Poutine: A Delicious Mess \nby Mike VerHulst")

poutine_pic = Image.open('poutine_pic.jpg')
st.image(poutine_pic, caption='Poutine', width=500)

#Import data
recipes = pd.read_csv('recipenlg.csv')
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
iconic Canadian dish. According to the Merriam-Webster Dictionary, poutine comes from a
Québécois slang word meaning “mess.”''')

st.write('**Insert map of Quebec here**')


### map
m = folium.Map(location=[46, -72], zoom_start=7, tiles='CartoDB positron')


# folium.Choropleth(
#     geo_data = combined,
#     fill_color='red',
#     opacity=1
# ).add_to(m)

folium_static(m)



### curds
curds = {'Uses cheese curds': len(curd_recipes), 'Uses other cheese': 68}

curds_df = pd.DataFrame.from_dict(curds, orient='index')
curds_df.reset_index(inplace=True)
curds_df.rename(columns={0:'num', 'index': 'has_curds'}, inplace=True)

base = alt.Chart(curds_df).encode(
    theta=alt.Theta("num:Q", stack=True), color=alt.Color("has_curds:N", legend=None)
)

pie = base.mark_arc(outerRadius=100)
text = base.mark_text(radius=160, size=15).encode(text="has_curds:N")

curd_viz = (pie + text).properties(title='Percentage of poutine recipes that use chees curds')

st.write('''#### Cheese with a squeek''')

st.write('''The key ingredient in poutine is fresh cheese curds. Fresh cheese curds
can last 24 hours before needing to be refrigerated and have a springiness
and squeak as you eat them. After being refrigerated, curds will lose thse
unique properties, leading to subsitutions for more common forms of
cheese such as shredded or block cheese.''')


curd_pic = Image.open('curds.jpg')
st.image(curd_pic, caption='Cheese curds', width=500)

curd_viz


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

protein_viz = alt.Chart(protein_df).mark_bar(color='red').encode(
    alt.Y('protein',
          sort=alt.EncodingSortField(field='Recipe Count', order='descending'),
          axis=alt.Axis(title='Protein')),
    alt.X('Recipe Count')
)


st.write('''#### How about some toppings?''')
st.write('''With only 3 core ingredients, it’s very
common to add additional toppings.
Proteins such as beef and bacon tend to
be the most commonly found additions
to the traditional recipe.''')

protein_viz


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
         axis=alt.Axis(title='Percentage of surveyed Canadians'))
)


st.write('''#### A New Canadian Icon?''')
st.write('''In a 2017 survey, more Canadians
chose poutine as their favorite “iconic”
Canadian food, even beating out maple
syrup.''')

iconic_viz

### map
can = gpd.read_file('https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/canada.geojson')
states = gpd.read_file('us_map2.json')
can = can[['name', 'geometry']]

states = states[['NAME', 'geometry']]
states.rename(columns={'NAME': 'name'},inplace=True)

# states2 = states[(states['name'] != 'Alaska') & (states['name'] != 'Hawaii') & (states['name'] != 'Puerto Rico')]
states2 = states[(states['name'] != 'Hawaii') & (states['name'] != 'Puerto Rico')]

# can2 = can[(can['name'] != 'Nunavut') & (can['name'] != 'Northwest Territories') & (can['name'] != 'Yukon Territory')]

combined = pd.concat([can, states2])

p_list = ['Quebec', 'Newfoundland and Labrador', 'British Columbia', 'New Brunswick', 
          'Nova Scotia', 'Saskatchewan', 'Alberta', 'Prince Edward Island', 'Manitoba', 
          'Ontario','Washington', 'Oregon','Idaho','Montana','North Dakota', 
          'Minnesota', 'Wisconsin', 'Michigan', 'Illinois', 'Tennessee',
          'Pennsylvania', 'New York', 'Vermont', 'New Hampshire', 'Maine', 
          'Massachusetts', 'Rhode Island', 'Connecticut', 'Alaska']
poutine = combined.loc[combined['name'].isin(p_list)]

# can_us = alt.Chart(combined).mark_geoshape(
#     fill='lightgray',stroke='white'
# ).project('albers').properties(
#     width=500,
#     height=300
# )

# p_map = alt.Chart(poutine).mark_geoshape(
#     fill='red',stroke='white'
# ).project('albers').properties(
#     width=500,
#     height=300
# )

# (can_us + p_map).properties(title='Places where poutine is commonly found')
# can_us


# https://www.youtube.com/watch?v=AHiWIOohYa8

m = folium.Map(location=[49.8954, -97.1385], zoom_start=3, tiles='CartoDB positron')

folium.Choropleth(
    geo_data = combined,
    fill_color='red',
    opacity=1
).add_to(m)


st.write('''#### Gaining in Popularity''')
st.write('''In present day, poutine has spread far outside Quebec. Poutine
is commonly found throughout Canada and the northern portions
of the United States.''')

folium_static(m)

st.write('''Gaining popularity
outside Canada,
major poutine festivals
have been hosted in
places like Chicago,
Knoxville, Manchester,
NH, and Rhode Island.''')

### restaurants
rests = pd.read_csv('laPoutine rest.csv')

rest_viz = alt.Chart(rests).mark_line(
    color='red',
    point=alt.OverlayMarkDef(color="black")
).encode(
    alt.X('year:N', axis=alt.Axis(title='Year')),
    alt.Y('number:Q',
          axis=alt.Axis(title='Restaurants Participating')),
          # impute=alt.ImputeParams(
          #     value = None,
          #     method='min',
          #     keyvals = [2015,2022]))
).properties(width=500, title='Number of restaurants participating in La Poutine Week by year')


st.write('''#### La Poutine Week''')
st.write('''La Poutine Week is the largest poutine
festival in the world. Beginning in
Montreal in 2013 with only 30
restaurants, it has since exploded to the
United States and even as far as
Australia. The 2022 festival had over
800 restaurants participate.''')


rest_viz


st.write('''Source: https://en.wikipedia.org/wiki/Poutine''')

#Sidebar


###### Making of all the charts


########Vis 1
#Interaction requirement 2, change opacity when hover over 
# s1 = alt.selection_single(on='mouseover', empty='none')

# #Interaction requirement 3 and 4, create brushing filter  
# s2 = alt.selection_interval(empty='none')
# opacityCondition = alt.condition(s1|s2, alt.value(1), alt.value(.6))


# ##Static Component - Bars
# bars = alt.Chart(df1).mark_bar(opacity=.6,color='orange', height=15).transform_filter(
#     alt.datum.rank < 11
# ).encode(
#     x = alt.X('PERCENT:Q',axis=None),
#     y = alt.Y('EMOJI:N', sort=alt.EncodingSortField(field='rank', order='ascending'),axis=None),
#     tooltip = alt.Tooltip('EMOJI:N', title='none'),
#     # opacity = opacityCondition
# ).add_selection(
#     s1,
# ).encode(
#     opacity = opacityCondition
# )

# ##Static Component - Emojis
# emojis = alt.Chart(df1).mark_text(align='right', width=20,opacity=.6).transform_filter(
#     alt.datum.rank < 11
# ).encode(
#     y = alt.Y('EMOJI:N', sort=alt.EncodingSortField(field='rank', order='ascending'), axis=None),
#     text = alt.Text('EMOJI:N'),
#     # opacity = opacityCondition
# ).add_selection(
#     s1,
#     s2
# ).encode(opacity = opacityCondition)


# ##Static Component - Text
# text = alt.Chart(df1).mark_text(align='right', width=20,opacity=.6).transform_filter(
#     alt.datum.rank < 11
# ).transform_calculate(
#     per = alt.datum.PERCENT / 100
# ).encode(
#     y = alt.Y('EMOJI:N', sort=alt.EncodingSortField(field='rank', order='ascending'), axis=None),
#     text = alt.Text('PERCENT_TEXT'),
#     # opacity = opacityCondition
# ).add_selection(
#     s1,
#     s2
# ).encode(
#     opacity = opacityCondition
# )
# ##Put all together
# viz1 = (emojis|text|bars).configure_view(strokeWidth=0)#.resolve_scale(y='shared')


# ########Vis 2
# #Static component line chart
# line = alt.Chart(df2).mark_line(size=2.5).encode(
#     x = alt.X('datetime:T'),
#     y = alt.Y('tweet_count', title='Four-minute rolling average'),
#     color = 'team:N'
# )

# #Zooming and Panning
# line = line.interactive(bind_y = False)

# #vertical line
# selection1 = alt.selection_single(on='mouseover', empty='none', encodings=['x'])
# colorCondition = alt.condition(selection1, alt.value('lightgray'),alt.value('none'))
# opacityCondition = alt.condition(selection1, alt.value(1), alt.value(0))

# vline = alt.Chart(df2).mark_rule(size=4).encode(
#     x = alt.X('datetime:T'),
#     # tooltip = alt.Tooltip(['tweet_count', 'datetime','team'])
#     # y = alt.Y('tweet_count', title='Four-minute rolling average'),
# ).add_selection(selection1).encode(color=colorCondition, opacity = opacityCondition)

# #interaction dots
# selection2 = alt.selection_single(on='mouseover', nearest=True, empty='none')

# colorCondition2 = alt.condition(selection1, alt.value('black'),alt.value('none'))

# dots = alt.Chart(df2).mark_circle(
#     filled=True,
#     color='none',
#     size=70
# ).encode(
#     x = alt.X('datetime:T'),
#     y = alt.Y('tweet_count', title='Four-minute rolling average'),
#     tooltip = alt.Tooltip(['tweet_count', 'datetime','team'])
# ).add_selection(selection2).encode(
#     color=colorCondition2, 
#     opacity = opacityCondition
# )

# # viz2 final
# viz2 = (line + vline + dots)


# ########Vis3
# emojis = list(df3['emoji'].unique())

# select_emoji = alt.selection_single(
#     fields = ['emoji'],
#     init = {'emoji': '🔥'},
#     bind = alt.binding_radio(
#         options = emojis,
#         name = 'emojis'
#     )
# )

# op_condition = alt.condition(select_emoji, alt.value(1), alt.value(0))

# line = alt.Chart(df3).mark_line().transform_filter(select_emoji).encode(
#     x = alt.X('datetime:T', axis=alt.Axis(tickCount=5)),
#     y = alt.Y('tweet_count:Q', axis=alt.Axis(tickCount=5)),
#     color = 'emoji:N'
# ).add_selection(select_emoji).encode(opacity = op_condition)


# # circles
# circle_selector = alt.selection_interval(empty='none')
# color_dot = alt.condition(circle_selector&select_emoji, alt.value('black'), alt.value('none'))
# opacityCondition = alt.condition(circle_selector&select_emoji, alt.value(1), alt.value(0))

# circles = alt.Chart(df3).mark_circle(
#     filled=True,
#     color='none',
#     size=70
# ).encode(
#     x = alt.X('datetime:T', axis=alt.Axis(tickCount=5)),
#     y = alt.Y('tweet_count:Q', axis=alt.Axis(tickCount=5))
# ).add_selection(circle_selector).encode( 
#     opacity = opacityCondition,
#     color = color_dot
# )
# viz3 = line+circles



# ########Vis4 BONUS OPTIONAL

# #Altair version

# #Streamlit widget version


# ##### Display graphs
# CHOICES = {1: "viz1", 2: "viz2", 3: "viz3"}

# def format_func(option):
#     return CHOICES[option]

# viz_options = [viz1, viz2, viz3]

# option = st.sidebar.selectbox("Select option", options=list(CHOICES.keys()), format_func=format_func)

# if option == 3:
#     st.write('### Altair Version')
#     viz_options[option-1]
    
#     st.write('### Streamlit Version')
#     ########Streamlit viz3
#     emojis = list(df3['emoji'].unique())

#     radio = st.radio('button', options=emojis)

#     op_condition = alt.condition(select_emoji, alt.value(1), alt.value(0))

#     line = alt.Chart(df3).mark_line().transform_filter(
#         alt.datum.emoji == radio
#     ).encode(
#         x = alt.X('datetime:T', axis=alt.Axis(tickCount=5)),
#         y = alt.Y('tweet_count:Q', axis=alt.Axis(tickCount=5)),
#         color = 'emoji:N'
#     )

#     # circles
#     circle_selector = alt.selection_interval(empty='none')
#     color_dot = alt.condition(circle_selector, alt.value('black'), alt.value('none'))
#     opacityCondition = alt.condition(circle_selector, alt.value(1), alt.value(0))

#     circles = alt.Chart(df3).mark_circle(
#         filled=True,
#         color='none',
#         size=70
#     ).transform_filter(
#         alt.datum.emoji == radio
#     ).encode(
#         x = alt.X('datetime:T', axis=alt.Axis(tickCount=5)),
#         y = alt.Y('tweet_count:Q', axis=alt.Axis(tickCount=5))
#     ).add_selection(circle_selector).encode( 
#         opacity = opacityCondition,
#         color = color_dot
#     )

#     viz3_streamlit = line+circles
#     viz3_streamlit
# else:
#     viz_options[option-1]
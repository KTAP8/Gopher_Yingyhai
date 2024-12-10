from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import ast
import matplotlib.pyplot as plt
import pydeck as pdk
from streamlit_agraph import agraph, Node, Edge, Config
import plotly.express as px
from streamlit_option_menu import option_menu
from collections import Counter
from wordcloud import WordCloud

#================================================================================================================================================================================================#
#================================================================================================================================================================================================#

# Make Dataframe from mongoDB
# uri = "mongodb+srv://KTAP8:JhpxOn0CFlXE5mty@dsdedata.hv1co.mongodb.net/?retryWrites=true&w=majority&appName=DsdeData"
# client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
# db = client['DsdeData']
# collection_datagiven = db['papers']
# collection_datascraped = db['arxivScraped']
# json_datagiven = collection_datagiven.find({})
# json_datascraped = collection_datascraped.find({})
# l = []
# for i in json_datagiven:
#     l.append(i)
# df = pd.DataFrame(l)

# Make Dataframe from csv
df = pd.read_csv('givenData.csv')

#================================================================================================================================================================================================#
#================================================================================================================================================================================================#

@st.cache_data
def load_data(nrows=None):
    data = df.copy()

    temp_ref_df = df['reference']
    row1 = temp_ref_df[0]
    cols = list(eval(str(row1)).keys())
    l = [list(eval(str(row)).values()) for row in temp_ref_df]
    ref_df = pd.DataFrame(l, columns=cols)
    data['refCount'] = ref_df['ref_count']
    # data['refCount'] = data['reference'].apply(lambda x: ast.literal_eval(x)['ref_count'] if pd.notna(x) and 'ref_count' in ast.literal_eval(x) else 0)

    cols = ['ID']
    ids = [[list(eval(str(row)).keys())] for row in df['subjectArea']]
    id_df = pd.DataFrame(ids, columns=cols)
    data['subjectAreaID'] = id_df['ID']
    # data['subjectAreaID'] = data['subjectArea'].apply(lambda x: list(ast.literal_eval(x).keys()) if pd.notna(x) else [])

    names = []
    for row in df['author']:
        n = [r['name'] for r in list(eval(str(row)).values())]
        names.append([n])
    cols = ['names']
    names_df = pd.DataFrame(names, columns=cols)
    data['authors'] = names_df['names']
    # data['authors'] = data['author'].apply(lambda x: [author['name'] for author in ast.literal_eval(x).values()] if pd.notna(x) else [])

    affiliation = []
    for row in df['affiliation']:
        a = [r['name'] for r in list(eval(str(row)).values())]
        affiliation.append([a])
    cols = ['affiliates']
    affiliates_df = pd.DataFrame(affiliation, columns=cols)
    data['affiliates'] = affiliates_df['affiliates']
    # data['affiliates'] = data['affiliation'].apply(lambda x: [affiliation['name'] for affiliation in ast.literal_eval(x).values()] if pd.notna(x) else [])
    
    # data['subjectAreaFull'] = data['subjectArea'].apply(lambda x: list(ast.literal_eval(x).values()) if pd.notna(x) else [])
    
    country = []
    for row in df['affiliation']:
        c = [r['country'] for r in list(eval(str(row)).values())]
        country.append([c])
    cols = ['country']
    country_df = pd.DataFrame(country, columns=cols)
    data['country'] = country_df['country']
    # data['country'] = data['affiliation'].apply(lambda x: [affiliation['country'] for affiliation in ast.literal_eval(x).values()] if pd.notna(x) else [])
    
    author_list = []
    for idx, row in df.iterrows():
        # print(row['author'])
        value_list = list(eval(str(row['author'])).values())
        l = [value['name'] for value in value_list]
        author_list.append([l])
    cols = ['author_list']
    author_list_df = pd.DataFrame(author_list, columns=cols)
    data['author_list'] = author_list_df['author_list']

    return data

def load_css(file_name):
    with open(file_name, 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


#================================================================================================================================================================================================#
#================================================================================================================================================================================================#

# set page configuration to be 'wide' 
st.set_page_config(layout="wide")

# reduce white space top of page
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)


# (if used), used style.css for decoration
load_css('style.css')

# Loading the data with caching
df_papers = load_data()  # Caching this load for efficiency

# Title
st.title("Research Paper Analysis")
# st.markdown('<p class="title">My Styled Title</p>', unsafe_allow_html=True)

#================================================================================================================================================================================================#
## Sidebar
with st.sidebar:

    st.image('Gopher.png', caption='Gopher and friends', use_container_width=True)

    selected_page = option_menu(
        menu_title = 'Menu',
        options = ['Home', 'Publication', 'Author', 'Affiliation', 'ML'],
        menu_icon = 'cast',
        icons= ['house']
    )

    # Filter title
    st.markdown(f'''
        <div style="font-size: 19px; text-align: center;">
            <b>Filter:</b>
        </div>
        ''', unsafe_allow_html=True)
    
    # Filter Start End Date
    start_date = pd.to_datetime(st.sidebar.date_input("Start Date:", value=pd.to_datetime("2018-01-01")))
    end_date = pd.to_datetime(st.sidebar.date_input("End Date:", value=pd.to_datetime("2023-12-12"),max_value=pd.to_datetime("2023-12-12")))

    # Filter using subject area
    subject_map = {
        'Materials Science': 'MATE', 'Physics': 'PHYS', 'Business': 'BUSI', 'Economics': 'ECON',
        'Health Sciences': 'HEAL', 'Chemistry': 'CHEM', 'Pharmacy': 'PHAR', 'Medicine': 'MEDI',
        'Biochemistry': 'BIOC', 'Agricultural Sciences': 'AGRI', 'Multidisciplinary': 'MULT',
        'Neuroscience': 'NEUR', 'Chemical Engineering': 'CENG', 'Engineering': 'ENGI',
        'Computer Science': 'COMP', 'Sociology': 'SOCI', 'Veterinary Science': 'VETE',
        'Earth Sciences': 'EART', 'Decision Sciences': 'DECI', 'Immunology': 'IMMU', 'Energy': 'ENER',
        'Mathematics': 'MATH', 'Arts and Humanities': 'ARTS', 'Environmental Science': 'ENVI',
        'Psychology': 'PSYC', 'Dentistry': 'DENT', 'Nursing': 'NURS', 'ALL':"ALL"
    }
    topics = list(subject_map.keys())
    topics.sort()
    selected_subject_area = st.sidebar.multiselect("Subject Area:", options=topics, default=["ALL"])
    subject_areas_mapped = [subject_map[area] for area in selected_subject_area]
    ## filtered_df = filter by date range
    ## filtered_df  = filter by date and subject area
    filtered_df = df_papers[(pd.to_datetime(df_papers['publishedDate']) >= start_date) & (pd.to_datetime(df_papers['publishedDate']) <= end_date)]
    if ("ALL" not in subject_areas_mapped) & (len(subject_areas_mapped) > 0):
        filtered_df2 = filtered_df[filtered_df['subjectAreaID'].apply(
            lambda x: any(area in x for area in subject_areas_mapped)
        )]
    else:
        filtered_df2 = filtered_df

# Style for sidebar
# st.markdown("""
#     <style>
#         /* Style for the sidebar */
#         [data-testid="stSidebar"] {
#             background-color: #1c1c1c;
#         }
#         /* Style for text in sidebar */
#         [data-testid="stSidebar"] p {
#             color: #ffffff;
#         }
#         [data-testid="stSidebar"] h2 {
#             color: #ffffff;
#         }
#         /* Style for the sidebar inputs */
#         [data-testid="stSidebar"] input {
#             color: black !important;
#         }
#         [data-testid="stSidebar"] select {
#             color: black !important;
#         }
#     </style>
#     """, unsafe_allow_html=True)

#================================================================================================================================================================================================#
## Key Metric Boxes

reference_count = filtered_df2['refCount'].dropna()
reference_count = reference_count.astype(int)
unique_authors = set(author for authors_list in filtered_df2['authors'] if isinstance(authors_list, list) for author in authors_list)
author_count = len(unique_authors)
unique_affiliations = set(affiliation for affiliations_list in filtered_df2['affiliates'] if isinstance(affiliations_list, list) for affiliation in affiliations_list)
unique_affiliations = len(unique_affiliations)
affiliation_count = filtered_df2['affiliates'].apply(len)
all_affiliates = df_papers['affiliates'].explode()
most_frequent_university = all_affiliates.value_counts().idxmax()
## metrics filtered by date and subject area

st.markdown("""
    <style>
        .metric-box {
            padding: 5px; 
            border-radius: 5px; 
            border: 1px solid #e6e6e6; 
            text-align: center; 
            background-color: #ffffff; 
            height: 75px; 
        }
    </style>
    """, unsafe_allow_html=True)

st.subheader("Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 18px">
            <b>Publications</b><br>{filtered_df2.shape[0]}
        </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 18px">
            <b>Authors</b><br>{author_count}
        </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 18px">
            <b>Reference Count</b><br>{reference_count.sum()}
        </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 18px">
            <b>Affiliations</b><br>{unique_affiliations}
        </div>
    ''', unsafe_allow_html=True)

with col5:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 18px">
            <b>Top Affiliation</b><br>{most_frequent_university}
        </div>
    ''', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

#================================================================================================================================================================================================#

col1,col2,col3 = st.columns([0.5, 0.05, 0.5])
with col1:
    ## publication share by subject area, filtered by date range
    subject_area_data = filtered_df2['subjectAreaID'].explode().value_counts().reset_index()
    subject_area_data.columns = ['Subject Area', 'Count']

    st.markdown("<h2 style='font-size:32px;'>Publication Share by Subject Area</h2>", unsafe_allow_html=True)
    chart_type = st.selectbox(
        "Choose Chart Type",
        options=['Bar Chart', 'Pie Chart', 'Donut Chart'],
    )

    if chart_type == "Bar Chart":
        # Bar chart using Altair
        bar_chart = alt.Chart(subject_area_data).mark_bar().encode(
            x=alt.X('Subject Area', sort='-y', title='Subject Area'),
            y=alt.Y('Count', title='Number of Publications'),
            tooltip=['Subject Area', 'Count']
        ).properties(
            width=500,
            height=400
        )
        st.altair_chart(bar_chart, use_container_width=True)

    elif chart_type == "Pie Chart":
        # Pie chart using Altair
        pie_chart = alt.Chart(subject_area_data).mark_arc().encode(
            theta=alt.Theta(field='Count', type='quantitative'),
            color=alt.Color(field='Subject Area', type='nominal', title='Subject Area'),
            tooltip=['Subject Area', 'Count']
        ).properties(
            width=500,
            height=400
        )
        st.altair_chart(pie_chart, use_container_width=True)

    elif chart_type == "Donut Chart":
        # Donut chart using Altair (similar to Pie Chart but with an inner radius)
        donut_chart = alt.Chart(subject_area_data).mark_arc(innerRadius=100).encode(
            theta=alt.Theta(field='Count', type='quantitative'),
            color=alt.Color(field='Subject Area', type='nominal', title='Subject Area'),
            tooltip=['Subject Area', 'Count']
        ).properties(
            width=500,
            height=400
        )
        st.altair_chart(donut_chart, use_container_width=True)
with col2:
    pass
with col3:
    ## Top affiliations by publication count, filtered by date range
    affiliation_data = filtered_df2['affiliates'].explode().value_counts().reset_index()
    affiliation_data.columns = ['Affiliation', 'Count']
    top_affiliation_data = affiliation_data.head(5)
    # Altair chart for top affiliations by publication count
    affiliation_chart = alt.Chart(top_affiliation_data).mark_bar().encode(
        x=alt.X('Count'),
        y='Affiliation'
    ).properties(
        width=500,
        height=480,
        title='Top Affiliations by Publication Count (Log Scale)'
    )
# Display the chart in Streamlit
    st.markdown("<h2 style='font-size:32px;'>Top Affiliations by Publication Count</h2>", unsafe_allow_html=True)

    st.altair_chart(affiliation_chart, use_container_width=True)

#================================================================================================================================================================================================#
## Affiliation Map

# Streamlit Title
st.markdown("<h1 style='font-size:32px;'>Interactive Affiliation Map Dashboard (Grouped by Country)</h1>", unsafe_allow_html=True)
# Define accurate country coordinates
country_coordinates = {
    "Thailand": [15.8700, 100.9925],
    "China": [35.8617, 104.1954],
    "Taiwan": [23.6978, 120.9605],
    "South Korea": [35.9078, 127.7669],
    "Australia": [-25.2744, 133.7751],
    "Hong Kong": [22.3193, 114.1694],
    "India": [20.5937, 78.9629],
    "Malaysia": [4.2105, 101.9758],
    "Singapore": [1.3521, 103.8198],
    "Philippines": [12.8797, 121.7740],
    "Brazil": [-14.2350, -51.9253],
    "Bulgaria": [42.7339, 25.4858],
    "Canada": [56.1304, -106.3468],
    "United Kingdom": [55.3781, -3.4360],
    "United States": [37.0902, -95.7129],
    "Germany": [51.1657, 10.4515],
    "France": [46.6034, 1.8883],
    "Italy": [41.8719, 12.5674],
    "Croatia": [45.1000, 15.2000],
    "Egypt": [26.8206, 30.8025],
    "Poland": [51.9194, 19.1451],
    "Iran": [32.4279, 53.6880],
    "Turkey": [38.9637, 35.2433],
    "Ukraine": [48.3794, 31.1656],
    "Qatar": [25.3548, 51.1839],
    "Ecuador": [-1.8312, -78.1834],
    "Georgia": [42.3154, 43.3569],
    "Puerto Rico": [18.2208, -66.5901],
    "Cyprus": [35.1264, 33.4299],
    "Sri Lanka": [7.8731, 80.7718],
    "Latvia": [56.8796, 24.6032],
    "Armenia": [40.0691, 45.0382],
    "Estonia": [58.5953, 25.0136],
    "Serbia": [44.0165, 21.0059],
    "Russian Federation": [61.5240, 105.3188],
    "Pakistan": [30.3753, 69.3451],
    "Belarus": [53.7098, 27.9534],
    "Lithuania": [55.1694, 23.8813],
    "Colombia": [4.5709, -74.2973],
    "Belgium": [50.8503, 4.3517],
    "Mexico": [23.6345, -102.5528],
    "Finland": [61.9241, 25.7482],
    "Greece": [39.0742, 21.8243],
    "Spain": [40.4637, -3.7492],
    "Switzerland": [46.8182, 8.2275],
    "Austria": [47.5162, 14.5501],
    "Hungary": [47.1625, 19.5033],
    "Portugal": [39.3999, -8.2245],
    "New Zealand": [-40.9006, 174.8860],
    "Czech Republic": [49.8175, 15.4730],
    "Ireland": [53.4129, -8.2439],
    "Netherlands": [52.1326, 5.2913],
    "Japan": [36.2048, 138.2529],
    "Indonesia": [-0.7893, 113.9213],
    "Chile": [-35.6751, -71.5430],
    "Slovenia": [46.1512, 14.9955],
    "Saudi Arabia": [23.8859, 45.0792],
    "Argentina": [-38.4161, -63.6167],
    "Bangladesh": [23.6850, 90.3563],
    # Add more countries as needed from the provided list
}

# Extract Affiliations with Real Country Data
def get_affiliation_details(filtered_df):
    """Extract affiliation details, including country information."""
    affiliation_data = []
    for idx, row in filtered_df.iterrows():
        for affiliation, country in zip(row['affiliates'], row['country']):
            # Use predefined coordinates if available
            if country in country_coordinates:
                lat, lon = country_coordinates[country]
            else:
                # Skip countries without coordinates to ensure accuracy
                continue

            affiliation_data.append({
                "Affiliation": affiliation,
                "Country": country,
                "Latitude": lat,
                "Longitude": lon,
                "Publications": 1,  # Assuming 1 publication per row
                # "Authors": len(row['authors'])
            })
    
    return pd.DataFrame(affiliation_data)

# Extract affiliation details from loaded data
affiliation_map_data = get_affiliation_details(filtered_df2)

# Aggregate Data by Country
country_map_agg = affiliation_map_data.groupby(
    ["Country", "Latitude", "Longitude"]
).agg({"Publications": "sum"}).reset_index()

country_map_display = country_map_agg[["Country", "Publications"]]

col6, col7 = st.columns([0.7, 0.3])
with col6:
# Pydeck Interactive Map Visualization
    st.markdown("<h2 style='font-size:16px;'>Affiliation Map (Interactive, Grouped by Country)</h2>", unsafe_allow_html=True)

    try:
        # Create the interactive Pydeck map
        st.pydeck_chart(
            pdk.Deck(
                initial_view_state=pdk.ViewState(
                    latitude=15.8700,  # Start with Thailand in view
                    longitude=100.9925,
                    zoom=1.5,
                    pitch=20,
                ),
                layers=[
                    # Scatterplot Layer for Country Aggregated Data
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=country_map_agg,
                        get_position=["Longitude", "Latitude"],
                        get_radius="Publications * 30",  # Reduce the radius to be appropriate
                        get_fill_color=[255, 0, 0, 150],  # Red color for markers
                        pickable=True,
                    ),
                ],
                tooltip={
                "html": """
                <div style="font-family: Arial, sans-serif; font-size: 14px; color: #FFFFFF; background-color: #333333; padding: 10px; border-radius: 8px;">
                    <b>Country:</b> {Country}<br>
                    <b>Publications:</b> {Publications}<br>
                </div>
                """,
                "style": {
                    "backgroundColor": "#333333",
                    "color": "white",
                    "border-radius": "8px",
                    "padding": "10px",
                    "font-family": "Arial, sans-serif",
                    "font-size": "14px"
                }
            }
            )
        )
    except Exception as e:
        st.error(f"An error occurred while rendering the map: {e}")
with col7:
    # Display Country Affiliation Details as DataFrame
    st.markdown("<h2 style='font-size:16px;'>Country Affiliation Details</h2>", unsafe_allow_html=True)
    st.dataframe(country_map_display, height=500)

#================================================================================================================================================================================================#
## Publication Growth Graph filtered by date range and subject area
# Ensure year_month is in datetime format
filtered_df2['year'] = pd.to_datetime(filtered_df2['publishedDate']).dt.year
filtered_df2['year_month'] = pd.to_datetime(filtered_df2['publishedDate']).dt.to_period('M')
filtered_df2['year_month'] = filtered_df2['year_month'].dt.to_timestamp()

# Explode subject areas for easier filtering and analysis
subject_area_for_graph = filtered_df2.explode('subjectAreaID')

# Filter by selected subject areas
if "ALL" not in subject_areas_mapped:
    subject_area_for_graph = subject_area_for_graph[
        subject_area_for_graph['subjectAreaID'].isin(subject_areas_mapped)
    ]

# Group by year_month and subject area, and calculate publication counts
topic_publication_growth = (
    subject_area_for_graph
    .groupby(['year_month', 'subjectAreaID'])
    .size()
    .reset_index(name='Publication Count')
)

# Plot publication counts for each subject area
st.markdown("<h2 style='font-size:32px;'>Publication Growth Over Time</h2>", unsafe_allow_html=True)
publication_chart = alt.Chart(topic_publication_growth).mark_line(opacity=0.7).encode(
    x=alt.X('year_month:T', title='Year-Month', axis=alt.Axis(format='%Y')),
    y=alt.Y('Publication Count:Q', title='Number of Publications'),
    color=alt.Color('subjectAreaID:N', title='Topic Area'),  # Different color for each subject area
    tooltip=['year_month:T', 'subjectAreaID:N', 'Publication Count:Q']
).properties(
    width=800,
    height=400
)

# Display the chart
st.altair_chart(publication_chart, use_container_width=True)

#================================================================================================================================================================================================#
## Author per year graph
## Group by year and count authors per year
authors_per_year = (
    filtered_df2.groupby('year')['authors']
    .apply(lambda x: len(set(author for authors_list in x if isinstance(authors_list, list) for author in authors_list))) ## Unique authors per year
)

st.markdown("<h2 style='font-size:32px;'>Number of Authors Per Year</h2>", unsafe_allow_html=True)

chart_type_author = st.selectbox(
        "Choose Chart Type",
        options=['Bar Chart', 'Line Chart'],
        key='author_chart_type'
    )

if chart_type_author == 'Bar Chart':
    author_chart = alt.Chart(authors_per_year).mark_bar(opacity=0.8).encode(
        x=alt.X('year:O', title='Year', axis=alt.Axis(labelAngle=0)),  # Use ordinal scale for years
        y=alt.Y('Author_Count:Q', title='Number of Authors'),
        tooltip=['year:O', 'Author_Count:Q']  # Tooltip for interactivity
    ).properties(
        width=800,
        height=400
    )

   
else: # Line chart
       author_chart = alt.Chart(authors_per_year).mark_line(point=True).encode(
        x=alt.X('year:O', title='Year', axis=alt.Axis(labelAngle=0)),  # Use ordinal scale for years
        y=alt.Y('Author_Count:Q', title='Number of Authors'),
        tooltip=['year:O', 'Author_Count:Q']  # Tooltip for interactivity
    ).properties(
        width=800,
        height=400
    )

st.altair_chart(author_chart, use_container_width=True)

#================================================================================================================================================================================================#
## Total Citation Count per Year
citation_count_per_year = (
    filtered_df2.groupby('year')
    .apply(lambda x: x['refCount'].dropna().astype(int).sum()) 
    .reset_index(name='Citation_Count')
)

# Citation Count per Year Bar Chart
st.markdown("<h2 style='font-size:32px;'>Citation Count Per Year</h2>", unsafe_allow_html=True)

chart_type_cite = st.selectbox(
        "Choose Chart Type",
        options=['Bar Chart', 'Line Chart'],
        key='cite_chart_type'
    )

if chart_type_cite == 'Bar Chart':
    citation_chart = alt.Chart(citation_count_per_year).mark_bar(opacity=0.8).encode(
        x=alt.X('year:O', title='Year', axis=alt.Axis(labelAngle=0)),  # Use ordinal scale for years
        y=alt.Y('Citation_Count:Q', title='Number of Citations'),
        tooltip=['year:O', 'Citation_Count:Q'] 
    ).properties(
        width=800,
        height=400
    )
else:
    citation_chart = alt.Chart(citation_count_per_year).mark_line(point=True).encode(
        x=alt.X('year:O', title='Year', axis=alt.Axis(labelAngle=0)),  # Use ordinal scale for years
        y=alt.Y('Citation_Count:Q', title='Number of Citations'),
        tooltip=['year:O', 'Citation_Count:Q'] 
    ).properties(
        width=800,
        height=400
    )

st.altair_chart(citation_chart, use_container_width=True)

#================================================================================================================================================================================================#
## Top Author Table (DataFrame)
col1, col2 = st.columns([0.3,0.7])
with col1:
## *** Top author dataframe ***
    all_authors = [
        author 
        for authors_list in filtered_df2['authors'] 
        if isinstance(authors_list, list) 
        for author in authors_list
    ]

    # Count the number of publications for each author
    author_publication_count = Counter(all_authors)

    # Create a DataFrame for visualization
    top_authors_df = pd.DataFrame(author_publication_count.items(), columns=['Author', 'Publication_Count'])

    # Sort by Publication_Count in descending order
    top_authors_df = top_authors_df.sort_values(by='Publication_Count', ascending=False).reset_index(drop=True)

    # Display the top authors DataFrame
    st.markdown("<h2 style='font-size:32px;'>Top Authors Contributions</h2>", unsafe_allow_html=True)
    st.write(top_authors_df)

#================================================================================================================================================================================================#
## Top Author Activity Chart

with col2:
## *** Top Author Activity Chart ***
    author_activity_data = []

    for _, row in filtered_df2.iterrows():
        if isinstance(row['authors'], list):
            for author in row['authors']:
                author_activity_data.append({'Author': author, 'Year': row['year']})

    # Create a DataFrame for author activity
    author_activity_df = pd.DataFrame(author_activity_data)

    # Count publications per year for each author
    author_publication_yearly = (
        author_activity_df.groupby(['Year', 'Author'])
        .size()
        .reset_index(name='Publication_Count')
    )

    # Filter the top authors based on total publications
    top_authors = top_authors_df.head(5)['Author'].tolist()  # Take top 5 authors
    filtered_author_publication_yearly = author_publication_yearly[
        author_publication_yearly['Author'].isin(top_authors)
    ]

    # Line Chart for Author Activity
    st.markdown("<h2 style='font-size:32px;'>Top Author Activity Over Time</h2>", unsafe_allow_html=True)

    author_activity_chart = alt.Chart(filtered_author_publication_yearly).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Publication_Count:Q', title='Number of Publications'),
        color=alt.Color('Author:N', title='Author'),  # Color for each author
        tooltip=['Year:O', 'Author:N', 'Publication_Count:Q']  # Tooltip for interactivity
    ).properties(
        width=800,
        height=450
    )

    # Display the chart
    st.altair_chart(author_activity_chart, use_container_width=True)

    subject_area_for_graph = filtered_df2.explode('subjectAreaID')

# Filter by selected subject areas
if "ALL" not in subject_areas_mapped:
    subject_area_for_graph = subject_area_for_graph[
        subject_area_for_graph['subjectAreaID'].isin(subject_areas_mapped)
    ]

# Group by year_month and subject area, and calculate cumulative publication counts
topic_publication_growth = (
    subject_area_for_graph
    .groupby(['year_month', 'subjectAreaID'])
    .size()
    .reset_index(name='Publication Count')
)

# Calculate cumulative sum for each subject area
topic_publication_growth['Cumulative Count'] = (
    topic_publication_growth
    .groupby('subjectAreaID')['Publication Count']
    .cumsum()
)

# Plot cumulative publication counts for each subject area
st.markdown("<h2 style='font-size:32px;'>Cumulative Publication Growth Over Time</h2>", unsafe_allow_html=True)
cumulative_publication_chart = alt.Chart(topic_publication_growth).mark_line(point=True, opacity=0.7).encode(
    x=alt.X('year_month:T', title='Year-Month', axis=alt.Axis(format='%Y-%m')),
    y=alt.Y('Cumulative Count:Q', title='Cumulative Number of Publications'),
    color=alt.Color('subjectAreaID:N', title='Topic Area'),  # Different color for each subject area
    tooltip=['year_month:T', 'subjectAreaID:N', 'Cumulative Count:Q']
).properties(
    width=800,
    height=400
)

# Display the chart
st.altair_chart(cumulative_publication_chart, use_container_width=True)

#================================================================================================================================================================================================#
## Top Affiliation Table (DataFrame)
col1, col2 = st.columns([0.3,0.7])
with col1:
## *** Top author dataframe ***
    all_aff = [
        aff 
        for aff_list in filtered_df2['affiliates'] 
        if isinstance(aff_list, list) 
        for aff in aff_list
    ]

    # Count the number of publications for each author
    aff_publication_count = Counter(all_aff)

    # Create a DataFrame for visualization
    top_aff_df = pd.DataFrame(aff_publication_count.items(), columns=['Affiliation', 'Publication_Count'])

    # Sort by Publication_Count in descending order
    top_aff_df = top_aff_df.sort_values(by='Publication_Count', ascending=False).reset_index(drop=True)

    # Display the top authors DataFrame
    st.markdown("<h2 style='font-size:32px;'>Top Affiliation Contributions</h2>", unsafe_allow_html=True)
    st.write(top_aff_df)

#================================================================================================================================================================================================#
## Top Affiliation Activity Chart

with col2:
## *** Top Author Activity Chart ***
    aff_activity_data = []

    for _, row in filtered_df2.iterrows():
        if isinstance(row['affiliates'], list):
            for aff in row['affiliates']:
                aff_activity_data.append({'Affiliation': aff, 'Year': row['year']})

    # Create a DataFrame for author activity
    aff_activity_df = pd.DataFrame(aff_activity_data)

    # Count publications per year for each author
    aff_publication_yearly = (
        aff_activity_df.groupby(['Year', 'Affiliation'])
        .size()
        .reset_index(name='Publication_Count')
    )

    # Filter the top authors based on total publications
    top_aff = top_aff_df.head(5)['Affiliation'].tolist()  # Take top 5 authors
    filtered_aff_publication_yearly = aff_publication_yearly[
        aff_publication_yearly['Affiliation'].isin(top_aff)
    ]

    # Line Chart for Author Activity
    st.markdown("<h2 style='font-size:32px;'>Top Affiliation Activity Over Time</h2>", unsafe_allow_html=True)

    aff_activity_chart = alt.Chart(filtered_aff_publication_yearly).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Publication_Count:Q', title='Number of Publications'),
        color=alt.Color('Affiliation:N', title='Affiliation'),  # Color for each author
        tooltip=['Year:O', 'Affiliation:N', 'Publication_Count:Q']  # Tooltip for interactivity
    ).properties(
        width=800,
        height=450
    )

    # Display the chart
    st.altair_chart(aff_activity_chart, use_container_width=True)

    subject_area_for_graph = filtered_df2.explode('subjectAreaID')

# Filter by selected subject areas
if "ALL" not in subject_areas_mapped:
    subject_area_for_graph = subject_area_for_graph[
        subject_area_for_graph['subjectAreaID'].isin(subject_areas_mapped)
    ]

# Group by year_month and subject area, and calculate cumulative publication counts
topic_publication_growth = (
    subject_area_for_graph
    .groupby(['year_month', 'subjectAreaID'])
    .size()
    .reset_index(name='Publication Count')
)

# Calculate cumulative sum for each subject area
topic_publication_growth['Cumulative Count'] = (
    topic_publication_growth
    .groupby('subjectAreaID')['Publication Count']
    .cumsum()
)

#================================================================================================================================================================================================#
## Subject Area Heatmap 
# Group by year and subject area to get the count of publications
heatmap_data = (
    subject_area_for_graph
    .groupby(['year', 'subjectAreaID'])
    .size()
    .reset_index(name='Publication Count')
)

# Create the heatmap using Altair
st.markdown("<h2 style='font-size:32px;'>Subject Area Heatmap by Year</h2>", unsafe_allow_html=True)
heatmap_chart = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X('year:O', title='Year'),
    y=alt.Y('subjectAreaID:N', title='Subject Area', sort='-x'),
    color=alt.Color('Publication Count:Q', title='Publication Count', scale=alt.Scale(scheme='blues')),
    tooltip=['year:O', 'subjectAreaID:N', 'Publication Count:Q']
).properties(
    width=800,
    height=400
)

# Display the heatmap
st.altair_chart(heatmap_chart, use_container_width=True)

#================================================================================================================================================================================================#
## Average Reference Per Publication:
# # Ensure 'refCount' column is numeric
filtered_df2['refCount'] = pd.to_numeric(filtered_df2['refCount'], errors='coerce')
# Handle missing or NaN values in 'refCount'
filtered_df2['refCount'] = filtered_df2['refCount'].fillna(0)
# Calculate average references per subject area
average_references = (
    filtered_df2.explode('subjectAreaID')
    .groupby('subjectAreaID')
    .agg(Average_Ref=('refCount', 'mean'))
    .reset_index()
)
# Step 1: Data Preparation
average_references = (
    filtered_df2.explode('subjectAreaID')
    .groupby('subjectAreaID')
    .agg(Average_Ref=('refCount', 'mean'))
    .reset_index()
)
# Step 2: Create Visualizations
st.markdown("<h2 style='font-size:32px;'>Average References Per Publication by Subject Area</h2>", unsafe_allow_html=True)
# reverse_subject_map = {v: k for k, v in subject_map.items()}
# average_references['Full Name'] = average_references['subjectAreaID'].map(reverse_subject_map)

# Bar Chart
bar_chart = alt.Chart(average_references).mark_bar().encode(
    x=alt.X('subjectAreaID:N', title='Subject Area', sort='-y'),
    y=alt.Y('Average_Ref:Q', title='Average References Per Publication'),
    tooltip=['subjectAreaID:N', 'Average_Ref:Q']
).properties(
    width=800,
    height=400,
    title="Average References Per Publication (Bar Chart)"
)
st.altair_chart(bar_chart, use_container_width=True)

#================================================================================================================================================================================================#
## Co-country network analysis

import networkx as nx
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import math

def create_cocountry_graph_from_papers(papers):
    """
    Objective:
        Creates a co-author graph from multiple papers.
    Parameters:
        papers (list of lists): List of lists, where each sublist contains authors of a paper.
    Returns:
        G (networkx.Graph): A co-author graph with weighted edges.
    """
    G = nx.Graph()

    # Iterate through each paper
    for paper_countries in papers:
        for i, country1 in enumerate(paper_countries):
            for country2 in paper_countries[i + 1:]:
                if country1 is not None and country2 is not None:
                    if G.has_edge(country1, country2):
                        G[country1][country2]['weight'] += 1  # Increment weight for additional collaborations
                    else:
                        G.add_edge(country1, country2, weight=1)  # New collaboration

    return G

def visualize_cocountry_graph(G):
    """
    Objective:
        Visualizes a co-author graph using Plotly with node and edge size based on collaboration frequency.
    """
    # Generate layout for nodes
    pos = nx.spring_layout(G, k=0.5)  # You can also try 'circular_layout', 'kamada_kawai_layout', etc.
    
    # Create edge traces based on weights
    edge_trace = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = math.log(G[edge[0]][edge[1]]['weight'] +1)  # Edge weight corresponds to collaboration count
        edge_trace.append(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode='lines',
            line=dict(width=weight, color='gray'),
            hoverinfo='none'
        ))
    
    # Create node traces based on degree (connections) and position
    node_trace = []
    for node in G.nodes():
        x, y = pos[node]
        degree = G.degree(node)
        degree = math.log(degree + 1) # scaled degree
        node_trace.append(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            text=node,
            textposition='top center',
            marker=dict(
                size=degree * 10,  # Node size based on the degree
                color='skyblue',
                line=dict(width=2, color='darkblue')
            ),
            hoverinfo='text'
        ))
    
    # Create the figure using Plotly
    fig = go.Figure(data=edge_trace + node_trace)
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        title="Co-Affiliation Network Graph",
        title_x=0.5,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

country_list =[i for i in filtered_df2['country'].dropna().to_list() if i != None]
# author_list = top_authors_df['author_list'].to_list()

G = create_cocountry_graph_from_papers(country_list)
# G = threshold_graph(G)

# Streamlit app starts here
st.title("Co-Country Network Graph")

# Visualize the graph using Plotly
fig = visualize_cocountry_graph(G)
st.plotly_chart(fig)

#================================================================================================================================================================================================#
# ## Co-affiliation network analysis

# import networkx as nx
# import plotly.graph_objects as go
# import matplotlib.pyplot as plt

# def create_coaffiliation_graph_from_papers(papers):
#     """
#     Objective:
#         Creates a co-author graph from multiple papers.
#     Parameters:
#         papers (list of lists): List of lists, where each sublist contains authors of a paper.
#     Returns:
#         G (networkx.Graph): A co-author graph with weighted edges.
#     """
#     G = nx.Graph()

#     # Iterate through each paper
#     for paper_affiliations in papers:
#         for i, aff1 in enumerate(paper_affiliations):
#             for aff2 in paper_affiliations[i + 1:]:
#                 if G.has_edge(aff1, aff2):
#                     G[aff1][aff2]['weight'] += 1  # Increment weight for additional collaborations
#                 else:
#                     G.add_edge(aff1, aff2, weight=1)  # New collaboration

#     return G

# def visualize_coaffiliation_graph(G):
#     """
#     Objective:
#         Visualizes a co-author graph using Plotly with node and edge size based on collaboration frequency.
#     """
#     # Generate layout for nodes
#     pos = nx.spring_layout(G)  # You can also try 'circular_layout', 'kamada_kawai_layout', etc.
    
#     # Create edge traces based on weights
#     edge_trace = []
#     for edge in G.edges():
#         x0, y0 = pos[edge[0]]
#         x1, y1 = pos[edge[1]]
#         weight = G[edge[0]][edge[1]]['weight']  # Edge weight corresponds to collaboration count
#         edge_trace.append(go.Scatter(
#             x=[x0, x1], y=[y0, y1],
#             mode='lines',
#             line=dict(width=weight, color='gray'),
#             hoverinfo='none'
#         ))
    
#     # Create node traces based on degree (connections) and position
#     node_trace = []
#     for node in G.nodes():
#         x, y = pos[node]
#         degree = G.degree(node)
#         node_trace.append(go.Scatter(
#             x=[x], y=[y],
#             mode='markers+text',
#             text=node,
#             textposition='top center',
#             marker=dict(
#                 size=degree * 10,  # Node size based on the degree
#                 color='skyblue',
#                 line=dict(width=2, color='darkblue')
#             ),
#             hoverinfo='text'
#         ))
    
#     # Create the figure using Plotly
#     fig = go.Figure(data=edge_trace + node_trace)
#     fig.update_layout(
#         showlegend=False,
#         hovermode='closest',
#         title="Co-Affiliation Network Graph",
#         title_x=0.5,
#         xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#         yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#         margin=dict(t=50, b=50, l=50, r=50)
#     )
    
#     return fig

# affiliation_list = filtered_df2['affiliates'].to_list()
# # author_list = top_authors_df['author_list'].to_list()

# G = create_coaffiliation_graph_from_papers(affiliation_list)
# # G = threshold_graph(G)

# # Streamlit app starts here
# st.title("Co-Affiliation Network Graph")

# # Visualize the graph using Plotly
# fig = visualize_coaffiliation_graph(G)
# st.plotly_chart(fig)

#================================================================================================================================================================================================#
## Co-author network analysis

# import networkx as nx
# import plotly.graph_objects as go
# import matplotlib.pyplot as plt

# def create_coauthor_graph_from_papers(papers):
#     """
#     Objective:
#         Creates a co-author graph from multiple papers.
#     Parameters:
#         papers (list of lists): List of lists, where each sublist contains authors of a paper.
#     Returns:
#         G (networkx.Graph): A co-author graph with weighted edges.
#     """
#     G = nx.Graph()

#     # Iterate through each paper
#     for paper_authors in papers:
#         for i, author1 in enumerate(paper_authors):
#             for author2 in paper_authors[i + 1:]:
#                 if G.has_edge(author1, author2):
#                     G[author1][author2]['weight'] += 1  # Increment weight for additional collaborations
#                 else:
#                     G.add_edge(author1, author2, weight=1)  # New collaboration

#     return G

# def visualize_coauthor_graph(G):
#     """
#     Objective:
#         Visualizes a co-author graph using Plotly with node and edge size based on collaboration frequency.
#     """
#     # Generate layout for nodes
#     pos = nx.spring_layout(G)  # You can also try 'circular_layout', 'kamada_kawai_layout', etc.
    
#     # Create edge traces based on weights
#     edge_trace = []
#     for edge in G.edges():
#         x0, y0 = pos[edge[0]]
#         x1, y1 = pos[edge[1]]
#         weight = G[edge[0]][edge[1]]['weight']  # Edge weight corresponds to collaboration count
#         edge_trace.append(go.Scatter(
#             x=[x0, x1], y=[y0, y1],
#             mode='lines',
#             line=dict(width=weight, color='gray'),
#             hoverinfo='none'
#         ))
    
#     # Create node traces based on degree (connections) and position
#     node_trace = []
#     for node in G.nodes():
#         x, y = pos[node]
#         degree = G.degree(node)
#         node_trace.append(go.Scatter(
#             x=[x], y=[y],
#             mode='markers+text',
#             text=node,
#             textposition='top center',
#             marker=dict(
#                 size=degree * 10,  # Node size based on the degree
#                 color='skyblue',
#                 line=dict(width=2, color='darkblue')
#             ),
#             hoverinfo='text'
#         ))
    
#     # Create the figure using Plotly
#     fig = go.Figure(data=edge_trace + node_trace)
#     fig.update_layout(
#         showlegend=False,
#         hovermode='closest',
#         title="Co-Author Network Graph",
#         title_x=0.5,
#         xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#         yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#         margin=dict(t=50, b=50, l=50, r=50)
#     )
    
#     return fig

# def threshold_graph(G, min_weight=5):
#     """
#     Removes edges with weights below the given threshold.
#     """
#     edges_to_remove = [(u, v) for u, v, w in G.edges(data=True) if w['weight'] < min_weight]
#     G.remove_edges_from(edges_to_remove)
#     return G

# # author_list = [
# #     ['Alice', 'Bob', 'Charlie'],     # Paper 1 (Alice, Bob, Charlie co-authored)
# #     ['David', 'Alice'],              # Paper 2 (David and Alice co-authored)
# #     ['David', 'Bob'],                # Paper 3 (David and Bob co-authored)
# #     ['David', 'Charlie'],
# #     ("David", "Liam"),
# #     ("David", "Mia"),
# #     ("David", "Nina"),
# #     ("David", "Oscar"),
# #     ("David", "Paul"),
# #     ("David", "Quinn"),
# #     ("David", "Rose"),
# #     ("David", "Sam"),
# #     ("David", "Tina"),
# #     ("David", "Uma"),
# #     ['David', 'Charlie'], 
# #     ['David', 'Charlie'], 
# #     ['David', 'Charlie'], 
# #     ['David', 'Charlie'],            # Paper 4 (David and Charlie co-authored
# #     ['Eve', 'Bob'],                  # Paper 5 (Eve and Bob co-authored)
# #     ['David', 'Charlie', 'Eve'],     # Paper 6 (David, Charlie, and Eve co-authored)
# # ]

# author_list = filtered_df2['author_list'].to_list()
# # author_list = top_authors_df['author_list'].to_list()

# G = create_coauthor_graph_from_papers(author_list)
# # G = threshold_graph(G)

# # Streamlit app starts here
# st.title("Co-Author Network Graph")

# # Visualize the graph using Plotly
# fig = visualize_coauthor_graph(G)
# st.plotly_chart(fig)

#================================================================================================================================================================================================#

### Top Author Keywords
# Step 1: Extract Keywords from 'authorKeywords' (list of strings)
def extract_author_keywords_from_string(df, column='authorKeywords', top_n=20):
    """Extract and count keywords from a column where each entry is a list of strings."""
    keywords_list = []
    for keywords in df[column].dropna():
        try:
            # Convert string representation of list to an actual list
            keywords_parsed = ast.literal_eval(keywords)
            if isinstance(keywords_parsed, list):
                keywords_list.extend(keywords_parsed)
        except (ValueError, SyntaxError):
            # Skip rows that cannot be parsed
            continue
    # Count keyword frequencies
    keyword_counts = Counter([keyword.strip().lower() for keyword in keywords_list])  # Convert to lowercase for consistency
    return pd.DataFrame(keyword_counts.most_common(top_n), columns=['Keyword', 'Count'])
# Extract top keywords from the 'authorKeywords' column
keywords_df = extract_author_keywords_from_string(filtered_df2, column='authorKeywords')
# Step 2: User Selection for Visualization
st.markdown("<h2 style='font-size:32px;'>Top Author Keywords</h2>", unsafe_allow_html=True)
chart_type = st.selectbox("Choose Chart Type", options=['Word Cloud', 'Bar Chart'])
if chart_type == 'Word Cloud':
    # Word Cloud Visualization
    wordcloud = WordCloud(
        width=800, height=400, background_color='white'
    ).generate_from_frequencies(dict(zip(keywords_df['Keyword'], keywords_df['Count'])))
    # Display the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt.gcf())
elif chart_type == 'Bar Chart':
    # Bar Chart Visualization
    bar_chart = alt.Chart(keywords_df).mark_bar().encode(
        x=alt.X('Count:Q', title='Frequency'),
        y=alt.Y('Keyword:N', title='Keyword', sort='-x'),
        tooltip=['Keyword:N', 'Count:Q']
    ).properties(
        width=800,
        height=400,
        title="Top Author Keywords (Bar Chart)"
    )
    st.altair_chart(bar_chart, use_container_width=True)
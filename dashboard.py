from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import ast
import matplotlib.pyplot as plt
import pydeck as pdk
from streamlit_agraph import agraph, Node, Edge, Config

# uri = "mongodb+srv://Unun:mJfqV0d3g1KQ6uKP@dsdedata.hv1co.mongodb.net/DsdeData?tls=true&tlsAllowInvalidCertificates=true"
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
# db = client['DsdeData']  # Replace with your database name
# papers = db['papers']
# df_papers = pd.DataFrame(list(papers.find()))
DATA_URL = 'papers.csv'
@st.cache_data
def load_data(nrows=None):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data['refCount'] = data['reference'].apply(lambda x: ast.literal_eval(x)['ref_count'] if pd.notna(x) and 'ref_count' in ast.literal_eval(x) else 0)
    data['subjectAreaID'] = data['subjectArea'].apply(lambda x: list(ast.literal_eval(x).keys()) if pd.notna(x) else [])
    data['authors'] = data['author'].apply(lambda x: [author['name'] for author in ast.literal_eval(x).values()] if pd.notna(x) else [])
    data['affiliates'] = data['affiliation'].apply(lambda x: [affiliation['name'] for affiliation in ast.literal_eval(x).values()] if pd.notna(x) else [])
    data['subjectAreaFull'] = data['subjectArea'].apply(lambda x: list(ast.literal_eval(x).values()) if pd.notna(x) else [])
    data['country'] = data['affiliation'].apply(lambda x: [affiliation['country'] for affiliation in ast.literal_eval(x).values()] if pd.notna(x) else [])
    return data
st.set_page_config(layout="wide")
# Loading the data with caching
data_load_state = st.text("Loading data...")
df_papers = load_data()  # Caching this load for efficiency
data_load_state.text("Done! (using st.cache_data)")

st.title("Gopher Dashboard")

#Filter sidebar
st.sidebar.header("Filter:")
start_date = pd.to_datetime(st.sidebar.date_input("Start Date:", value=pd.to_datetime("2018-01-01")))
end_date = pd.to_datetime(st.sidebar.date_input("End Date:", value=pd.to_datetime("2023-12-12"),max_value=pd.to_datetime("2023-12-12")))

# Filter using subject area
#map
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
subject_area = st.sidebar.selectbox("Subject Area:", options=topics)
subject_area = subject_map[subject_area]
## filtered_df = filter by date range
## filtered_df  = filter by date and subject area
filtered_df = df_papers[(pd.to_datetime(df_papers['publishedDate']) >= start_date) & (pd.to_datetime(df_papers['publishedDate']) <= end_date)]
if subject_area != "ALL":
    filtered_df2 = filtered_df[filtered_df['subjectAreaID'].apply(lambda x: subject_area in x)]
else:
    filtered_df2 = filtered_df

citation_count = filtered_df2['refCount'].dropna()
citation_count = citation_count.astype(int)
author_count = filtered_df2['authors'].apply(len)
affiliation_count = filtered_df2['affiliates'].apply(len)
all_affiliates = df_papers['affiliates'].explode()
most_frequent_university = all_affiliates.value_counts().idxmax()
## metrics filtered by date and subject area

st.markdown("""
    <style>
        /* Style for the sidebar */
        [data-testid="stSidebar"] {
            background-color: #1c1c1c;
        }
        /* Style for text in sidebar */
        [data-testid="stSidebar"] p {
            color: #ffffff;
        }
        [data-testid="stSidebar"] h2 {
            color: #ffffff;
        }
        /* Style for the sidebar inputs */
        [data-testid="stSidebar"] input {
            color: black !important;
        }
        [data-testid="stSidebar"] select {
            color: black !important;
        }
        /* General styling for cards */
        .metric-box {
            font-size: 56px; 
            padding: 16px; 
            border-radius: 10px; 
            border: 1px solid #e6e6e6; 
            text-align: center; 
            background-color: #ffffff; 
            width: 250px; 
            height: 130px; 
            
        }
    </style>
    """, unsafe_allow_html=True)


st.header("Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 20px">
            <b>Publications</b><br>{filtered_df2.shape[0]}
        </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 20px">
            <b>Authors</b><br>{author_count.sum()}
        </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 20px">
            <b>Citation Count</b><br>{citation_count.sum()}
        </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 20px">
            <b>Affiliations</b><br>{affiliation_count.sum()}
        </div>
    ''', unsafe_allow_html=True)

with col5:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 20px">
            <b>Top U</b><br>{most_frequent_university}
        </div>
    ''', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
col1,col2,col3 = st.columns([0.5, 0.05,0.5])
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
                "Authors": len(row['authors'])
            })
    
    return pd.DataFrame(affiliation_data)

# Extract affiliation details from loaded data
affiliation_map_data = get_affiliation_details(filtered_df2)

# Aggregate Data by Country
country_map_agg = affiliation_map_data.groupby(
    ["Country", "Latitude", "Longitude"]
).agg({"Publications": "sum", "Authors": "sum"}).reset_index()

col6, col7 = st.columns([0.65, 0.35])
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
                    "html": "<b>Country:</b> {Country}<br><b>Publications:</b> {Publications}<br><b>Authors:</b> {Authors}",
                    "style": {"backgroundColor": "steelblue", "color": "white"}
                }
            )
        )
    except Exception as e:
        st.error(f"An error occurred while rendering the map: {e}")
with col7:
    # Display Country Affiliation Details as DataFrame
    st.markdown("<h2 style='font-size:16px;'>Country Affiliation Details</h2>", unsafe_allow_html=True)
    st.dataframe(country_map_agg, height=500)


## Publication Growth Graph filtered by date range and subject area

filtered_df2['year_month'] = pd.to_datetime(filtered_df2['publishedDate']).dt.to_period('M')
publication_growth = filtered_df2.groupby('year_month').size().reset_index(name='Publication Count')
publication_growth['year_month'] = publication_growth['year_month'].dt.to_timestamp()
st.markdown("<h2 style='font-size:32px;'>Publication Growth Over Time</h2>", unsafe_allow_html=True)
line_chart_detailed = alt.Chart(publication_growth).mark_line(point=True).encode(
    x=alt.X('year_month:T', title='Year-Month', axis=alt.Axis(format='%Y-%b')),
    y=alt.Y('Publication Count:Q', title='Number of Publications'),
    tooltip=['year_month:T', 'Publication Count']
).properties(
    width=800,
    height=400
)
st.altair_chart(line_chart_detailed, use_container_width=True)

## Co Author Network

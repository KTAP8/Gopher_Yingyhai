from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import streamlit as st
import altair as alt
import ast
import matplotlib.pyplot as plt
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
    return data

# Loading the data with caching
data_load_state = st.text("Loading data...")
df_papers = load_data()  # Caching this load for efficiency
data_load_state.text("Done! (using st.cache_data)")

st.title("Gopher Dashboard")

#Filter sidebar
st.sidebar.header("filter:")
start_date = pd.to_datetime(st.sidebar.date_input("Start Date:", value=pd.to_datetime("2018-01-01")))
end_date = pd.to_datetime(st.sidebar.date_input("End Date:", value=pd.to_datetime("2023-12-12"),max_value=pd.to_datetime("2023-12-12")))
subject_area = st.selectbox("Subject Area:", options=df_papers['subjectAreaID'].explode().unique())

## filtered_df = filter by date range
## filtered_df  = filter by date and subject area
filtered_df = df_papers[(pd.to_datetime(df_papers['publishedDate']) >= start_date) & (pd.to_datetime(df_papers['publishedDate']) <= end_date)]
filtered_df2 = filtered_df[filtered_df['subjectAreaID'].apply(lambda x: subject_area in x)]

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
        [data-testid="stSidebar"] * {
            color: #ffffff;
        }
        /* Style for the sidebar inputs */
        [data-testid="stSidebar"] input {
            color: black !important;
        }
        /* General styling for cards */
        .metric-box {
            font-size: 16px; 
            padding: 15px; 
            border-radius: 10px; 
            border: 1px solid #e6e6e6; 
            text-align: center; 
            background-color: #ffffff; 
            width: 130px; 
            height: 100px; 
        }
    </style>
    """, unsafe_allow_html=True)


st.header("Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 16px; padding: 15px; border-radius: 10px; border: 1px solid #e6e6e6; text-align: center; background-color: #ffffff;">
            <b>Publications</b><br>{filtered_df2.shape[0]}
        </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 16px; padding: 15px; border-radius: 10px; border: 1px solid #e6e6e6; text-align: center; background-color: #ffffff;">
            <b>Authors</b><br>{author_count.sum()}
        </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 16px; padding: 15px; border-radius: 10px; border: 1px solid #e6e6e6; text-align: center; background-color: #ffffff;">
            <b>Citation Count</b><br>{citation_count.sum()}
        </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 16px; padding: 15px; border-radius: 10px; border: 1px solid #e6e6e6; text-align: center; background-color: #ffffff;">
            <b>Affiliations</b><br>{affiliation_count.sum()}
        </div>
    ''', unsafe_allow_html=True)

with col5:
    st.markdown(f'''
        <div class="metric-box" style="font-size: 16px; padding: 15px; border-radius: 10px; border: 1px solid #e6e6e6; text-align: center; background-color: #ffffff;">
            <b>Top U</b><br>{most_frequent_university}
        </div>
    ''', unsafe_allow_html=True)




## publication share by subject area, filtered by date range
subject_area_data = filtered_df['subjectAreaID'].explode().value_counts().reset_index()
subject_area_data.columns = ['Subject Area', 'Count']

st.header("Publication Share by Subject Area")
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

## Top affiliations by publication count, filtered by date range
st.header("Top Affiliations by Publication Count")

affiliation_data = filtered_df['affiliates'].explode().value_counts().reset_index()
affiliation_data.columns = ['Affiliation', 'Count']
top_affiliation_data = affiliation_data.head(15)

plt.figure(figsize=(10, 6))
plt.bar(top_affiliation_data['Affiliation'], top_affiliation_data['Count'], color='skyblue')
plt.yscale('log') 
plt.xlabel('Affiliation')
plt.ylabel('Number of Publications (Log Scale)')
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.title('Top Affiliations by Publication Count (Log Scale)')
plt.tight_layout()

st.pyplot(plt)
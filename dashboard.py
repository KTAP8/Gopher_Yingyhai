from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import streamlit as st
import altair as alt
import ast
# uri = "mongodb+srv://Unun:mJfqV0d3g1KQ6uKP@dsdedata.hv1co.mongodb.net/DsdeData?tls=true&tlsAllowInvalidCertificates=true"
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
# db = client['DsdeData']  # Replace with your database name
# papers = db['papers']
# df_papers = pd.DataFrame(list(papers.find()))
df_papers = pd.read_csv('papers.csv')
## data needed
## publication, filter by date range, filter by subject area
## authors, filter by date range, filter by subject area
## citation count, filter by date range, filter by subject area
## number of affiliations, filter by date range, filter by subject area
## top contributing regions ( affiliations? university name ), filter by date range, filter by subject area
df_papers['refCount'] = 0
df_papers['refCount'] = df_papers['reference'].apply(lambda x: ast.literal_eval(x)['ref_count'] if pd.notna(x) and 'ref_count' in ast.literal_eval(x) else 0)
df_papers['subjectAreaID'] = df_papers['subjectArea'].apply(lambda x: list(ast.literal_eval(x).keys()) if pd.notna(x) else [])
df_papers['authors'] = df_papers['author'].apply(lambda x: [author['name'] for author in ast.literal_eval(x).values()] if pd.notna(x) else [])
df_papers['affiliates'] = df_papers['affiliation'].apply(lambda x: [affiliation['name'] for affiliation in ast.literal_eval(x).values()] if pd.notna(x) else [])
#Title
st.title("Gopher Dashboard")

#Filter sidebar
st.sidebar.header("filter:")
start_date = pd.to_datetime(st.sidebar.date_input("Start Date:", value=pd.to_datetime("2018-01-01")))
end_date = pd.to_datetime(st.sidebar.date_input("End Date:", value=pd.to_datetime("2023-12-12"),max_value=pd.to_datetime("2023-12-12")))
subject_area = st.sidebar.selectbox("Subject Area:", options=df_papers['subjectAreaID'].explode().unique())


filtered_df = df_papers[(pd.to_datetime(df_papers['publishedDate']) >= start_date) & (pd.to_datetime(df_papers['publishedDate']) <= end_date)]
filtered_df = filtered_df[filtered_df['subjectAreaID'].apply(lambda x: subject_area in x)]

citation_count = filtered_df['refCount'].dropna()
citation_count = citation_count.astype(int)
author_count = filtered_df['authors'].apply(len)
affiliation_count = filtered_df['affiliates'].apply(len)
all_affiliates = df_papers['affiliates'].explode()
most_frequent_university = all_affiliates.value_counts().idxmax()
st.write("Total Publications:", filtered_df.shape[0])
st.write("Total Citations:", citation_count.sum())
st.write("Total Authors:", author_count.sum())
st.write("Total Affiliations:", affiliation_count.sum())
st.write("Top Contributing Regions:", most_frequent_university)







# #Key Metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)


#Columns for displaying charts
col1, col2 = st.columns(2)
chart_type = st.selectbox(
    "Choose Chart Type",
    options=['Bar Chart', 'Pie Chart', 'Donut Chart'],
)
with col1:
    st.header("Publication share by Subject Area")
    
    # if chart_type == "Bar Chart":
    #     chart = alt.Chart(df_papers['Subject Area']).mark_bar().encode(
    #         x=alt.X("Subject Area", title="Subject Area"),
    #         y=alt.Y("Publications", title="Publications"),
    #         tooltip=["Subject Area", "Publications"],
    #     )
    # st.altair_chart(chart, use_container_width=True)


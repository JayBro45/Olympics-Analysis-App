import streamlit as st
import helper
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

df = helper.preprocess(df, region_df)

st.sidebar.title('Olympics Analysis')
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRq0OOvJprk26JL9x_rG0PJRqQKAtqMy55VTg&s")

user_menu = st.sidebar.radio('Select an Option: ',('Medal Tally','Overall Analysis','Counrty-wise Analysis','Athlete-wise Analysis'))

if user_menu=='Medal Tally':
    st.sidebar.header('Medal Tally')
    years,countries = helper.year_country_list(df)
    selected_year = st.sidebar.selectbox('Select Year',years)
    selected_country = st.sidebar.selectbox('Select Country',countries)
    
    medal_tally=helper.medal_tally(df,selected_year,selected_country)
    if selected_country=='Overall' and selected_year=='Overall':
        st.title('Overall Medal Tally')
    elif selected_country=='Overall' and selected_year!='Overall':
        st.title(f'Medal Tally in {selected_year} Olympics')
    elif selected_country!='Overall' and selected_year=='Overall':
        st.title(f'{selected_country} Overall Performance')
    else:
        st.title(f"{selected_country}'s Performance in {selected_year} Olympics")
    if medal_tally is None or medal_tally.empty:
        st.warning("No data available to display the medal tally.")
    else:
        st.table(medal_tally)

if user_menu=='Overall Analysis':
    editons = df['Year'].nunique()
    hosts = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    nations = df['region'].nunique()
    Athletes = df['Name'].nunique()

    st.title('Top Statistics')
    col1,col2,col3 = st.columns(3)
    with col1:
        st.header('Editions')
        st.title(editons)
    with col2:
        st.header('Hosts')
        st.title(hosts)
    with col3:
        st.header('Sports')
        st.title(sports)

    col1,col2,col3 = st.columns(3)
    with col1:
        st.header('Events')
        st.title(events)
    with col2:
        st.header('Nations')
        st.title(nations)
    with col3:
        st.header('Athletes')
        st.title(Athletes)
    

    nations_over_time = df.groupby('Year')['region'].nunique().reset_index()
    nations_over_time.rename(columns={'Year':'Edition','region':'No. of Countries'},inplace=True)
    fig = px.line(nations_over_time,x='Edition',y='No. of Countries')    
    st.title('Participating Nations Over Time')
    if nations_over_time.empty:
        st.warning("No data available to display the line chart.")
    else:
        st.plotly_chart(fig)

    events_over_time = df.groupby('Year')['Event'].nunique().reset_index()
    events_over_time.rename(columns={'Year':'Edition','Event':'No. of Events'},inplace=True)
    fig = px.line(events_over_time,x='Edition',y='No. of Events')
    st.title('Events Over the Years')
    if events_over_time.empty:
        st.warning("No data available to display the line chart.")
    else:
        st.plotly_chart(fig)
    
    athletes_over_time = df.groupby('Year')['Name'].nunique().reset_index()
    athletes_over_time.rename(columns={'Year':'Edition','Name':'No. of Athletes'},inplace=True)
    fig = px.line(athletes_over_time,x='Edition',y='No. of Athletes')
    st.title('Athletes Over the Years')
    if athletes_over_time.empty:
        st.warning("No data available to display the line chart.")
    else:
        st.plotly_chart(fig)

    st.title('No. of Events over Time (Every Sport)')
    fig,ax = plt.subplots(figsize=(20,20))
    x = df.drop_duplicates(subset=['Year','Sport','Event'])
    pivot = x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count', fill_value=0)
    if pivot.empty:
        st.warning("No data available to display the heatmap.")
    else:
        ax = sns.heatmap(pivot, annot=True)
        st.pyplot(fig)

    st.title('Most Successful Athletes')
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')
    selected_sport = st.selectbox('Select Sport',sport_list)
    x = helper.most_successful(df,selected_sport)
    if x is None or x.empty:
        st.warning("No data available to display the table.")
    else:
        st.table(x)

if user_menu=='Counrty-wise Analysis':
    st.sidebar.title('Country-wise Analysis')
    countries = df['region'].dropna().unique().tolist()
    countries.sort()
    selected_country = st.sidebar.selectbox('Select Country',countries)
    country_medal_tally = helper.country_medal_tally(df,selected_country)
    st.title(f'{selected_country} Medal Tally Over the Years')
    if country_medal_tally is None:
        st.warning("No data available to display the medal tally plot.")
    else:
        st.plotly_chart(country_medal_tally)

    st.title(f'{selected_country} excel in following Sports')
    fig = helper.country_sport_heatmap(df,selected_country)
    if fig is None:
        st.warning("No data available to display the heatmap.")
    else:
        st.pyplot(fig)

    st.title(f'Top 10 Athletes of {selected_country}')
    top_athletes = helper.top_athletes(df,selected_country)
    if top_athletes is None or top_athletes.empty:
        st.warning("No data available to display the top athletes table.")
    else:
        st.table(top_athletes)

if user_menu=='Athlete-wise Analysis':
    st.title('Age Distribution of Athletes')
    fig = helper.age_distribution(df)
    st.plotly_chart(fig)

    st.title('Distribution of Age wrt Sports (Gold Medalist)')
    fig = helper.age_distribution_sport(df)
    st.plotly_chart(fig)

    st.title('Height vs Weight')
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')
    selected_sport = st.selectbox('Select Sport',sport_list)
    fig = helper.weight_height(df,selected_sport)
    st.pyplot(fig)

    st.title('Men vs Women Participation over the Years')
    fig = helper.men_vs_women(df)
    st.plotly_chart(fig)
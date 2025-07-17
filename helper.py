import sys
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import plotly.graph_objects as go

#data cleaning
def preprocess(df,region_df):
    df.drop_duplicates(inplace=True)
    region_df.drop_duplicates(inplace=True)
    athlete_df=df.merge(region_df, on='NOC', how='left')
    athlete_df=athlete_df[athlete_df['Season']=='Summer']
    return athlete_df

def year_country_list(athlete_df):
    years = athlete_df['Year'].dropna().unique().tolist()
    countries = athlete_df['region'].dropna().unique().tolist()
    years.sort()
    countries.sort()
    years.insert(0,'Overall')
    countries.insert(0,'Overall')
    return years,countries


#Medal_Tally
def medal_tally(athlete_df, year='Overall', country='Overall'):
    medal_tally = athlete_df[['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal','region']]
    medal_tally.drop_duplicates(subset=['NOC','Year','City','Sport','Event','Medal'],inplace=True)
    medal_tally=pd.concat([medal_tally, pd.get_dummies(medal_tally['Medal']).astype(int)], axis=1).drop(columns=['Medal'])

    medal_tally['Total Medals'] = medal_tally[['Gold', 'Silver', 'Bronze']].sum(axis=1)
    if(year=='Overall' and country=='Overall'):
        temp_df = medal_tally.groupby('region')[['Gold','Silver','Bronze','Total Medals']].agg(sum).sort_values(by=['Total Medals','Gold','Silver','Bronze'], ascending=[False,False,False,False]).reset_index()
        temp_df.index = temp_df.index + 1
        return temp_df

    if(year=='Overall' and country!='Overall'):
        temp_df = medal_tally[medal_tally['Team']==country].groupby('Year')[['Gold','Silver','Bronze','Total Medals']].agg(sum)
        return temp_df
    
    if(year!='Overall' and country=='Overall'):
        temp_df = medal_tally[medal_tally['Year']==int(year)].groupby('region')[['Gold','Silver','Bronze','Total Medals']].agg(sum).sort_values(by=['Total Medals','Gold','Silver','Bronze'], ascending=[False,False,False,False]).reset_index()
        temp_df.index = temp_df.index + 1
        return temp_df
    if(year!='Overall' and country!='Overall'):
        temp_df = medal_tally[(medal_tally['region']==country) & (medal_tally['Year']==int(year))].groupby('Sport')[['Gold','Silver','Bronze','Total Medals']].agg(sum)
        return temp_df

def most_successful(athlete_df, sport):
    most_successful = athlete_df[['Name', 'region', 'Sport', 'Event', 'Medal']].reset_index(drop=True)
    most_successful = pd.concat([most_successful, pd.get_dummies(most_successful['Medal']).astype(int)], axis=1).drop(columns=['Medal'])
    most_successful = most_successful[most_successful['Gold'] > 0]
    if sport == 'Overall':
        most_successful = (
            most_successful.groupby(['Name', 'region'])['Gold'].sum().sort_values(ascending=False).reset_index()
        )
    else:
        most_successful = most_successful[most_successful['Sport'] == sport]
        most_successful = (
            most_successful.groupby(['Name', 'region'])['Gold'].sum().sort_values(ascending=False).reset_index()
        )
    most_successful.index = most_successful.index + 1
    return most_successful.head(15)

def country_medal_tally(athlete_df, country):
    country_medal_tally = pd.concat([athlete_df, pd.get_dummies(athlete_df['Medal']).astype(int)], axis=1).drop(columns=['Medal'])
    country_medal_tally = country_medal_tally[country_medal_tally['region']==country][['Event','region','Year','Gold','Silver','Bronze']].drop_duplicates()
    country_medal_tally['Total Medals']=country_medal_tally[['Gold','Silver','Bronze']].sum(axis=1)
    country_medals_by_year = country_medal_tally.groupby('Year')[['Gold','Silver','Bronze','Total Medals']].sum().reset_index()
    if country_medals_by_year.empty:
        return None
    color_map = {
        'Gold': '#FFD700',
        'Silver': '#C0C0C0',
        'Bronze': '#CD7F32',
        'Total Medals': '#1f77b4'
    }
    fig = px.line(
        country_medals_by_year,
        x='Year',
        y=['Gold', 'Silver', 'Bronze', 'Total Medals'],
        color_discrete_map=color_map,
        labels={'value': 'Number of Medals', 'variable': 'Medal Type'}
    )
    return fig

def country_sport_heatmap(athlete_df, country):
    country_medal_tally = athlete_df.dropna(subset=['Medal'])
    country_medal_tally = pd.concat([country_medal_tally, pd.get_dummies(country_medal_tally['Medal']).astype(int)], axis=1).drop(columns=['Medal'])
    country_medal_tally = country_medal_tally[country_medal_tally['region']==country][['Sport','Event','region','Year','Gold','Silver','Bronze']].drop_duplicates()
    country_medal_tally['Total Medals']=country_medal_tally[['Gold','Silver','Bronze']].sum(axis=1)
    pivot = country_medal_tally.pivot_table(index='Sport', columns='Year', values='Total Medals', aggfunc='sum', fill_value=0)
    if pivot.empty:
        return None
    fig,ax = plt.subplots(figsize=(20,20))
    ax=sns.heatmap(pivot,annot=True)
    return fig

def top_athletes(athlete_df, country):
    country_medal_tally = athlete_df.dropna(subset=['Medal'])
    country_medal_tally = pd.concat([country_medal_tally, pd.get_dummies(country_medal_tally['Medal']).astype(int)], axis=1).drop(columns=['Medal'])
    country_medal_tally = country_medal_tally[country_medal_tally['region']==country][['Name','region','Sport','Gold','Silver','Bronze']]
    country_medal_tally['Total Medals']=country_medal_tally[['Gold','Silver','Bronze']].sum(axis=1)
    country_medal_tally = (
        country_medal_tally
        .groupby(['Name','Sport'])[['Gold', 'Silver', 'Bronze', 'Total Medals']]
        .sum()
        .sort_values(by=['Gold', 'Silver', 'Bronze', 'Total Medals'], ascending=[False, False, False, False])
        .reset_index()
    )
    country_medal_tally.index = country_medal_tally.index + 1
    return country_medal_tally.head(10)

def age_distribution(athlete_df):
    athletewise = athlete_df[['Name','Sex','Age','Height',"Weight",'region','Medal','Year']].copy()
    Overall = athletewise.drop_duplicates(subset=['Name','region','Year','Age']).copy()
    Gold = athletewise[athletewise['Medal']=='Gold'].drop_duplicates(subset=['Name','region','Year','Age']).copy()
    Silver = athletewise[athletewise['Medal']=='Silver'].drop_duplicates(subset=['Name','region','Year','Age']).copy()
    Bronze = athletewise[athletewise['Medal']=='Bronze'].drop_duplicates(subset=['Name','region','Year','Age']).copy()
    Overall = Overall['Age'].dropna()
    Gold = Gold['Age'].dropna()
    Silver = Silver['Age'].dropna()
    Bronze = Bronze['Age'].dropna()
    color_map = {
        'Overall Age': '#1f77b4',
        'Gold Medalist': '#FFD700',
        'Silver Medalist': '#C0C0C0',
        'Bronze Medalist': '#CD7F32',
    }
    fig = ff.create_distplot(
        [Overall, Gold, Silver, Bronze],
        ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
        show_hist=False,
        show_rug=False,
        colors=[
            color_map['Overall Age'],
            color_map['Gold Medalist'],
            color_map['Silver Medalist'],
            color_map['Bronze Medalist']
        ]
    )
    fig.update_layout(autosize=False,width=1000,height=600)
    return fig


def age_distribution_sport(athlete_df):
    x=[]
    name=[]
    famous_sports=['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                     'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                     'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                     'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens',
                     'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    for sport in famous_sports:
        temp_df=athlete_df[athlete_df['Sport']==sport]
        x.append(temp_df[temp_df['Medal']=='Gold']['Age'].dropna())
        name.append(sport)
    
    fig = ff.create_distplot(x,name,show_hist=False,show_rug=False)
    fig.update_layout(autosize=False,width=1000,height=600)
    return fig

import matplotlib.pyplot as plt
import seaborn as sns

def weight_height(athlete_df, sport):
    htwt = athlete_df[['Sex', 'Height', 'Weight', 'Medal', 'Sport']].copy()
    htwt['Medal'].fillna('No Medal', inplace=True)

    if sport != 'Overall':
        htwt = htwt.loc[htwt['Sport'] == sport]

    htwt.dropna(subset=['Height', 'Weight'], inplace=True)

    hue_order = ['Gold', 'Silver', 'Bronze', 'No Medal']
    palette = {
        'Gold': '#FFD700',
        'Silver': '#C0C0C0',
        'Bronze': '#CD7F32',
        'No Medal': '#1f77b4'
    }

    plt.figure(figsize=(10, 10))
    sns.scatterplot(
        x='Weight',
        y='Height',
        data=htwt,
        hue='Medal',
        hue_order=hue_order,
        palette=palette,
        style='Sex',
        s=100
    )

    plt.xlabel('Weight (kg)')
    plt.ylabel('Height (cm)')
    plt.legend(loc='upper right')

    return plt.gcf()

def men_vs_women(athlete_df):
    # Group by Year and Sex, count unique participants (assuming 'Name' is unique per athlete)
    participation = (
        athlete_df
        .drop_duplicates(subset=['Year', 'Name', 'Sex'])
        .groupby(['Year', 'Sex'])['Name']
        .count()
        .reset_index()
        .rename(columns={'Name': 'Count'})
    )

    # Create the line plot
    fig = px.line(
        participation,
        x='Year',
        y='Count',
        color='Sex',
        markers=True,
        labels={'Count': 'Number of Participants', 'Year': 'Edition', 'Sex': 'Gender'},
    )
    return fig


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from db_config import load_data


@st.cache_data
def get_df():
    df = load_data()
    df.drop_duplicates(subset=["Title"], keep="first", inplace=True)
    return df


df = get_df()

st.title("IMDb Movie Analysis")

# Top 10 Movies by Rating and Voting Counts
st.write("### Top 10 Movies by Rating and Voting Counts")
top_10_movies = df.sort_values(by=["Rating", "Votes"], ascending=[False, False]).head(10)
st.table(top_10_movies[["Title", "Rating", "Votes"]])

# Filters
st.sidebar.header("Filters")

duration_option = st.sidebar.radio("Select Duration Range", ["Below 2 hrs", "2-3 hrs", "Above 3 hrs"])
if duration_option == "Below 2 hrs":
    df = df.loc[df["Duration"] < 120]
elif duration_option == "2-3 hrs":
    df = df.loc[(df["Duration"] >= 120) & (df["Duration"] <= 180)]
else:
    df = df.loc[df["Duration"] > 180]

rating_filter = st.sidebar.slider(
    "IMDb Rating",
    min_value=float(df["Rating"].min()),
    max_value=float(df["Rating"].max()),
    value=(6.0, 10.0),
)
votes_filter = st.sidebar.slider(
    "Minimum Votes",
    min_value=int(df["Votes"].min()),
    max_value=int(df["Votes"].max()),
    value=10000,
)

genre_options = df["Genre"].unique()
genre_filter = st.sidebar.radio("Select Genre", options=["All"] + list(genre_options))

# Apply filters
filtered_df = df.loc[
    (df["Rating"] >= rating_filter[0])
    & (df["Rating"] <= rating_filter[1])
    & (df["Votes"] >= votes_filter)
]
if genre_filter != "All":
    filtered_df = filtered_df.loc[filtered_df["Genre"] == genre_filter]

st.write("### Filtered Movies", filtered_df)

# Genre Distribution
st.write("### Genre Distribution")
genre_counts = df["Genre"].value_counts()
fig_genre = px.bar(
    genre_counts,
    x=genre_counts.index,
    y=genre_counts.values,
    labels={"x": "Genre", "y": "Count"},
    title="Movies per Genre",
)
st.plotly_chart(fig_genre)

# Average Duration by Genre
st.write("### Average Duration by Genre")
fig = px.bar(
    df.groupby("Genre")["Duration"].mean().sort_values().reset_index(),
    x="Duration",
    y="Genre",
    orientation="h",
)
st.plotly_chart(fig)

# Voting Trends by Genre
st.write("### Voting Trends by Genre")
fig = px.bar(
    df.groupby("Genre")["Votes"].mean().sort_values().reset_index(),
    x="Genre",
    y="Votes",
)
st.plotly_chart(fig)

# Rating Distribution
st.write("### Rating Distribution")
fig = px.histogram(
    df,
    x="Rating",
    nbins=20,
    marginal="box",
    title="Distribution of Ratings",
)
st.plotly_chart(fig)

# Top-Rated Movies per Genre
st.write("### Top-Rated Movies per Genre")
top_movies = df.loc[df.groupby("Genre")["Rating"].idxmax()][["Genre", "Title", "Rating"]]
st.table(top_movies)

# Most Popular Genres by Voting
st.write("### Most Popular Genres by Voting")
fig = px.pie(
    df.groupby("Genre")["Votes"].sum().reset_index(),
    names="Genre",
    values="Votes",
)
st.plotly_chart(fig)

# Duration Extremes
st.write("### Shortest and Longest Movies")
shortest_movie = df.loc[df["Duration"].idxmin()][["Title", "Duration"]]
longest_movie = df.loc[df["Duration"].idxmax()][["Title", "Duration"]]
st.write(f"Shortest Movie: {shortest_movie['Title']} ({shortest_movie['Duration']} min)")
st.write(f"Longest Movie: {longest_movie['Title']} ({longest_movie['Duration']} min)")

# Ratings by Genre (Heatmap)
st.write("### Ratings by Genre")
avg_ratings = df.groupby("Genre")["Rating"].mean().reset_index()
fig = px.imshow(
    avg_ratings.pivot_table(index='Genre', values='Rating'),
    labels=dict(color="Average Rating"),
)
st.plotly_chart(fig)

# Correlation Analysis
st.write("### Correlation Analysis: Ratings vs Votes")
fig = px.scatter(
    df,
    x="Votes",
    y="Rating",
    opacity=0.5,
    title="Correlation between Ratings and Votes",
)
st.plotly_chart(fig)

# Load data
# def load_data():
#     file_path = "imdb_2024_cleaned.csv"
#     df = pd.read_csv(file_path)
#     return df

# df = load_data()
# df.drop_duplicates(subset=["Title"], keep="first", inplace=True)


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pymysql

connection = pymysql.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    port=4000,
    user="4HbKbrAWUhJxmRf.root",
    password="Cv0NKG96bWzF4um2",
    database="IMDB",
    ssl={"ca": r"C:\Users\Arjun\OneDrive\Desktop\guvi\isrgrootx1.pem"}
)
query = "SELECT * FROM Imdb_2024_cleaned"
df = pd.read_sql(query, connection)
df.drop_duplicates(subset=["title"], keep="first", inplace=True)


st.title("IMDb Movie Analysis")

# Top 10 Movies by Rating and Voting Counts
st.write("### Top 10 Movies by Rating and Voting Counts")
top_10_movies = df.sort_values(by=["rating", "votes"], ascending=[False, False]).head(10)
st.table(top_10_movies[["title", "rating", "votes"]])

# Filters
st.sidebar.header("Filters")

duration_option = st.sidebar.radio("Select Duration Range", ["Below 2 hrs", "2-3 hrs", "Above 3 hrs"])
if duration_option == "Below 2 hrs":
    df = df.loc[df["duration"] < 120]
elif duration_option == "2-3 hrs":
    df = df.loc[(df["duration"] >= 120) & (df["duration"] <= 180)]
else:
    df = df.loc[df["duration"] > 180]

rating_filter = st.sidebar.slider("IMDb Rating", min_value=float(df["rating"].min()), 
                                   max_value=float(df["rating"].max()), value=(6.0, 10.0))
votes_filter = st.sidebar.slider("Minimum Votes", min_value=int(df["votes"].min()), 
                                  max_value=int(df["votes"].max()), value=10000)

genre_options = df["genre"].unique()
genre_filter = st.sidebar.radio("Select Genre", options=["All"] + list(genre_options))

# Apply filters
filtered_df = df.loc[(df["rating"] >= rating_filter[0]) & (df["rating"] <= rating_filter[1]) &
                      (df["votes"] >= votes_filter)]
if genre_filter != "All":
    filtered_df = filtered_df.loc[df["genre"] == genre_filter]

st.write("### Filtered Movies", filtered_df)

# Genre Distribution
st.write("### Genre Distribution")
genre_counts = df['genre'].value_counts()
fig_genre = px.bar(genre_counts, x=genre_counts.index, y=genre_counts.values, labels={'x': 'Genre', 'y': 'Count'}, title="Movies per Genre")
st.plotly_chart(fig_genre)

# Average Duration by Genre
st.write("### Average Duration by Genre")
fig = px.bar(df.groupby("genre")["duration"].mean().sort_values().reset_index(), 
             x="duration", y="genre", orientation="h")
st.plotly_chart(fig)

# Voting Trends by Genre
st.write("### Voting Trends by Genre")
fig = px.bar(df.groupby("genre")["votes"].mean().sort_values().reset_index(), x="genre", y="votes")
st.plotly_chart(fig)

# Rating Distribution
st.write("### Rating Distribution")
fig = px.histogram(df, x="rating", nbins=20, marginal="box", title="Distribution of Ratings")
st.plotly_chart(fig)

# Top-Rated Movies per Genre
st.write("### Top-Rated Movies per Genre")
top_movies = df.loc[df.groupby("genre")["rating"].idxmax()][["genre", "title", "rating"]]
st.table(top_movies)

# Most Popular Genres by Voting
st.write("### Most Popular Genres by Voting")
fig = px.pie(df.groupby("genre")["votes"].sum().reset_index(), names="genre", values="votes")
st.plotly_chart(fig)

# Duration Extremes
st.write("### Shortest and Longest Movies")
shortest_movie = df.loc[df["duration"].idxmin()][["title", "duration"]]
longest_movie = df.loc[df["duration"].idxmax()][["title", "duration"]]
st.write(f"Shortest Movie: {shortest_movie['title']} ({shortest_movie['duration']} min)")
st.write(f"Longest Movie: {longest_movie['title']} ({longest_movie['duration']} min)")

# Ratings by Genre (Heatmap)
st.write("### Ratings by Genre")
avg_ratings = df.groupby("genre")["rating"].mean().reset_index()
fig = px.imshow(avg_ratings.pivot_table(index='genre', values='rating'), labels=dict(color="Average Rating"))
st.plotly_chart(fig)

# Correlation Analysis
st.write("### Correlation Analysis: Ratings vs Votes")
fig = px.scatter(df, x="votes", y="rating", opacity=0.5, title="Correlation between Ratings and Votes")
st.plotly_chart(fig)

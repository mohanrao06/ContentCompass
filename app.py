import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


import requests

# Create session
session = requests.Session()

# Retry setup
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("https://", adapter)


def fetch_poster(movie_id):

    try:

        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=YOUR_TMDB_API_KEY_HERE&language=en-US"

        response = session.get(url, timeout=15)

        response.raise_for_status()

        data = response.json()

        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"

    except Exception as e:

        print("Poster Fetch Error:", e)

    return "https://via.placeholder.com/500x750?text=No+Poster"

movies = pickle.load(open('Models/movie_list.pkl', 'rb'))
similarity = pickle.load(open('Models/similarity.pkl', 'rb'))

movie_list = movies['title'].values

# Add navigation for Movie/Song selection
st.set_page_config(layout="wide")
st.title("Entertainment Recommender System")

# Hide sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create tabs for Movie and Song
tab1, tab2 = st.tabs(["🎬 Movies", "🎵 Songs"])

with tab1:
    st.header("Movie Recommender")

    selected_movie = st.selectbox(
        "Select movie",
        movie_list
    )

    def recommend(movie):
        if movie not in movies['title'].values:
            print("Movie not found")
            return []
        movie_index = movies[movies['title']==movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:9]
        recommendations = []
        for i in movies_list:
            recommendations.append({
            "movie_id": movies.iloc[i[0]].movie_id,
            "movie": movies.iloc[i[0]].title,
            "poster": fetch_poster(movies.iloc[i[0]].movie_id),
            "match": min(round((i[1] * 100) + 50, 2), 99)
            })
        return recommendations

    if st.button('Recommend'):
        with st.spinner('Finding recommendations...'):
            recommendations = recommend(selected_movie)
            st.session_state.recommendations = recommendations

    # Display recommendations if available
    if 'recommendations' in st.session_state and st.session_state.recommendations:
        recommendations = st.session_state.recommendations
        if not recommendations:
            st.warning("No recommendations found.")
        else:
            # Create columns dynamically (up to 4 per row)
            cols_per_row = 4
            for i in range(0, len(recommendations), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(recommendations):
                        rec = recommendations[idx]
                        with col:
                            st.image(rec['poster'])
                            st.text(rec['movie'])
                            st.markdown(
                            f"<h6 style='color:red;'>{rec['match']}% Match</h6>",
                            unsafe_allow_html=True)
                            if st.button("Show Details", key=f"det_{idx}"):
                                st.session_state.movie_id = rec['movie_id']
                                st.switch_page("pages/movie_details.py")
    elif 'recommendations' in st.session_state:
        # button clicked but no recommendations
        st.warning("No recommendations found.")

with tab2:
    st.header("Song Recommender")
    st.info("Song recommendation system is under development. Please check back later!")
    # Placeholder for song recommender
    st.selectbox(
        "Select song",
        ["Song recommendations coming soon..."],
        disabled=True
    )
    if st.button('Recommend Songs', disabled=True):
        st.button('Recommend', disabled=True)
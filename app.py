import streamlit as st
import pickle
import pandas as pd
import requests
import os
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


def fetch_song_artwork(song, artist):
    """Return a large artwork URL from iTunes Search API for the song+artist, or None."""
    try:
        term = f"{artist} {song}"
        resp = session.get('https://itunes.apple.com/search', params={'term': term, 'entity': 'song', 'limit': 1}, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        if data.get('results'):
            art = data['results'][0].get('artworkUrl100')
            if art:
                return art.replace('100x100bb', '500x500bb')
    except Exception:
        return None
    return None


def fetch_poster(movie_id):

    try:

        # Determine TMDB API key (streamlit secrets -> environment)
        TMDB_KEY = None
        try:
            TMDB_KEY = st.secrets.get('TMDB_API_KEY')
        except Exception:
            TMDB_KEY = None
        if not TMDB_KEY:
            TMDB_KEY = os.getenv('TMDB_API_KEY')

        if not TMDB_KEY:
            print("Warning: TMDB_API_KEY not set. Movie poster fetch may fail.")

        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_KEY}&language=en-US"

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

# Load song model and similarity (if available)
try:
    df = pickle.load(open('Models/song_list.pkl', 'rb'))
    similer = pickle.load(open('Models/similer.pkl', 'rb'))
    # support different column name fallback
    if 'song' in getattr(df, 'columns', []):
        song_list = df['song'].values
    elif df.shape[1] >= 1:
        song_list = df.iloc[:, 0].values
    else:
        song_list = []
except Exception as e:
    df = None
    similer = None
    song_list = []
    print("Song model load error:", e)

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



def recommender(song_name):
    if df is None or similer is None:
        print("Song model not available")
        return []
    # Determine song column
    if 'song' in getattr(df, 'columns', []):
        song_col = 'song'
    else:
        song_col = df.columns[0]

    # Normalize strings for robust matching
    try:
        series = df[song_col].astype(str).str.strip().str.lower()
    except Exception:
        series = df.iloc[:, 0].astype(str).str.strip().str.lower()

    target = str(song_name).strip().lower()
    matches = df[series == target]
    if matches.empty:
        print("Sorry! Song not Found...")
        return []
    song_index = matches.index[0]
    distances = similer[song_index]
    song_idxs = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:9]
    recommendations = []
    for i in song_idxs:
        title = df.at[i[0], song_col] if song_col in df.columns else df.iloc[i[0], 0]
        # artist column detection
        if 'artists' in getattr(df, 'columns', []):
            artist_col = 'artists'
        elif 'artist' in getattr(df, 'columns', []):
            artist_col = 'artist'
        else:
            artist_col = df.columns[1] if len(df.columns) > 1 else None
        artist_name = df.at[i[0], artist_col] if artist_col and artist_col in df.columns else ''
        recommendations.append({
            "song": title,
            "artist": artist_name,
            "match": min(round((i[1] * 100) + 50, 2), 99)
        })
    return recommendations
    



with tab2:
    st.header("Song Recommender")
    if df is None or similer is None or len(song_list) == 0:
        st.error("Song model or data not found. Ensure `Models/song_list.pkl` and `Models/similer.pkl` exist.")
    else:
        selected_song = st.selectbox("Select song", song_list)

        if st.button('Recommend Songs', key='recommend_songs_btn'):
            with st.spinner('Finding song recommendations...'):
                recommendations = recommender(selected_song)
                st.session_state.song_recommendations = recommendations
        if st.button('Show Details', key='show_details_selected'):
            st.session_state.song_title = selected_song
            st.switch_page('pages/song_details.py')

        if 'song_recommendations' in st.session_state and st.session_state.song_recommendations:
            recs = st.session_state.song_recommendations
            cols_per_row = 4
            for i in range(0, len(recs), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(recs):
                        r = recs[idx]
                        with col:
                            # attempt to fetch artwork
                            art_url = fetch_song_artwork(r['song'], r.get('artist', ''))
                            if art_url:
                                st.image(art_url, width=300)
                            else:
                                st.image('https://via.placeholder.com/300x300?text=No+Artwork')
                            st.markdown(f"**{r['song']}**")
                            if r.get('artist'):
                                st.caption(r['artist'])
                            st.markdown(f"<h6 style='color:green;'>{r['match']}% Match</h6>", unsafe_allow_html=True)
                            if st.button('Show Details', key=f"song_det_{idx}"):
                                st.session_state.song_title = r['song']
                                st.switch_page('pages/song_details.py')
        elif 'song_recommendations' in st.session_state:
            st.warning("No song recommendations found.")
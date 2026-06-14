import streamlit as st
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

def fetch_movie_details(movie_id):
    try:
        # Resolve TMDB API key from Streamlit secrets or environment
        TMDB_KEY = None
        try:
            TMDB_KEY = st.secrets.get('TMDB_API_KEY')
        except Exception:
            TMDB_KEY = None
        if not TMDB_KEY:
            TMDB_KEY = os.getenv('TMDB_API_KEY')

        if not TMDB_KEY:
            st.error("TMDB_API_KEY not set. Please set it in .streamlit/secrets.toml or as an env var.")

        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_KEY}&language=en-US"
        response = session.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching movie details: {e}")
        return None

def fetch_movie_credits(movie_id):
    try:
        # Use resolved TMDB key
        TMDB_KEY = os.getenv('TMDB_API_KEY') if not (TMDB_KEY := (st.secrets.get('TMDB_API_KEY') if hasattr(st, 'secrets') else None)) else TMDB_KEY
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_KEY}&language=en-US"
        response = session.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching movie credits: {e}")
        return None

def fetch_movie_reviews(movie_id):
    try:
        TMDB_KEY = os.getenv('TMDB_API_KEY') if not (TMDB_KEY := (st.secrets.get('TMDB_API_KEY') if hasattr(st, 'secrets') else None)) else TMDB_KEY
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_KEY}&language=en-US"
        response = session.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching movie reviews: {e}")
        return None

def fetch_watch_providers(movie_id):
    try:
        TMDB_KEY = os.getenv('TMDB_API_KEY') if not (TMDB_KEY := (st.secrets.get('TMDB_API_KEY') if hasattr(st, 'secrets') else None)) else TMDB_KEY
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_KEY}"
        response = session.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching watch providers: {e}")
        return None

# Get movie_id from session state
if 'movie_id' not in st.session_state:
    st.error("No movie selected. Please go back and select a movie.")
    st.stop()

movie_id = st.session_state.movie_id

# Fetch data
with st.spinner('Loading movie details...'):
    data = fetch_movie_details(movie_id)
    credits = fetch_movie_credits(movie_id)
    reviews = fetch_movie_reviews(movie_id)
    providers = fetch_watch_providers(movie_id)

if not data:
    st.stop()

# Display movie poster and title
col1, col2 = st.columns([1, 2])

with col1:
    poster_url = f"https://image.tmdb.org/t/p/w500/{data['poster_path']}" if data.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Poster"
    st.image(poster_url, width=350)

with col2:
    st.title(data['title'])
    st.write(f"**Tagline:** {data.get('tagline', 'N/A')}")

    st.write("⭐ **Rating:**", f"{data['vote_average']}/10")
    st.write("📅 **Release Date:**", data['release_date'])
    st.write("⏱ **Runtime:**", data['runtime'], "minutes")
    st.write("💰 **Budget:**", f"${data.get('budget', 0):,}" if data.get('budget') else "N/A")
    st.write("💵 **Revenue:**", f"${data.get('revenue', 0):,}" if data.get('revenue') else "N/A")

    # Additional info to fill space
    st.write("---")
    if data.get('genres'):
        genres = [g['name'] for g in data['genres']]
        st.write("🎭 **Genres:**", " | ".join(genres))

    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.write("🌐 **Original Language:**", data.get('original_language', 'N/A').upper())
        st.write("📊 **Popularity:**", f"{data.get('popularity', 0):.1f}")
    with col_info2:
        st.write("📈 **Vote Count:**", f"{data.get('vote_count', 0):,}")
        st.write("📋 **Status:**", data.get('status', 'N/A'))

st.write("---")

# Overview
st.subheader("Overview")
st.write(data['overview'])

# Cast and Crew
if credits and credits.get('cast'):
    st.subheader("Top Cast")
    cast_cols = st.columns(5)
    for i, cast_member in enumerate(credits['cast'][:5]):  # Show top 5 cast
        with cast_cols[i]:
            if cast_member.get('profile_path'):
                st.image(f"https://image.tmdb.org/t/p/w200/{cast_member['profile_path']}")
            st.text(cast_member['name'])
            st.caption(cast_member['character'])

# Reviews
if reviews and reviews.get('results'):
    st.subheader("User Reviews")
    # We'll show reviews in rows of 4 columns
    review_list = reviews['results']
    # Process in chunks of 4
    for i in range(0, len(review_list), 4):
        cols = st.columns(4)
        for j in range(4):
            idx = i + j
            with cols[j]:
                if idx < len(review_list):
                    review = review_list[idx]
                    # Get rating
                    rating = review.get('author_details', {}).get('rating')
                    if rating is not None:
                        rating_5 = rating / 2.0
                        full_stars = int(rating_5)
                        star_display = '★' * full_stars + '☆' * (5 - full_stars)
                        st.write(f"{star_display} {rating_5}/5")
                    else:
                        st.write("☆☆☆☆☆ No rating")
                    # Truncate review text
                    st.write(review['content'][:150] + "..." if len(review['content']) > 150 else review['content'])
                else:
                    # Empty column
                    st.write("")

# Where to Watch
if providers and providers.get('results'):
    st.subheader("Where to Watch")
    us_data = providers['results'].get('US')
    if us_data:
        # Streaming
        if us_data.get('flatrate'):
            flatrate_providers = [p['provider_name'] for p in us_data['flatrate']]
            st.write("**Streaming:** " + " | ".join(flatrate_providers))
        # Rent
        if us_data.get('rent'):
            rent_providers = [p['provider_name'] for p in us_data['rent']]
            st.write("**Rent:** " + " | ".join(rent_providers))
        # Buy
        if us_data.get('buy'):
            buy_providers = [p['provider_name'] for p in us_data['buy']]
            st.write("**Buy:** " + " | ".join(buy_providers))
    else:
        st.write("Watch information not available for US region.")

# Back button
if st.button("← Back to Recommendations"):
    st.switch_page("app.py")
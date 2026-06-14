import streamlit as st
import pickle
import requests
import os
import pandas as pd

# Load song dataframe
try:
    df = pickle.load(open('Models/song_list.pkl', 'rb'))
except Exception as e:
    st.error('Song data not found: ' + str(e))
    st.stop()

# Require a selected song in session state
if 'song_title' not in st.session_state:
    st.error('No song selected. Please go back and choose a song.')
    st.stop()

song_title = st.session_state.song_title

# Determine song and artist columns
if 'track_name' in getattr(df, 'columns', []):
    title_col = 'track_name'
elif 'song' in getattr(df, 'columns', []):
    title_col = 'song'
else:
    title_col = df.columns[0]

if 'artists' in getattr(df, 'columns', []):
    artist_col = 'artists'
elif 'artist' in getattr(df, 'columns', []):
    artist_col = 'artist'
else:
    artist_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

# Find the song row (case-insensitive)
series = df[title_col].astype(str).str.strip().str.lower()
matches = df[series == str(song_title).strip().lower()]
if matches.empty:
    st.error('Selected song not found in dataset.')
    st.stop()

row = matches.iloc[0]
artist = row.get(artist_col, '')

# Load song metadata from the dataset for album and details.
album = ''
genre_val = None
matched_row = None
duration_ms_meta = None
tempo_val = None
country_val = None
explicit_flag = None
try:
    csv_path = os.path.join('Data', 'songs_data', 'dataset.csv')
    usecols = ['track_name', 'artists', 'album_name', 'track_genre', 'duration_ms', 'tempo', 'explicit']
    meta_df = pd.read_csv(csv_path, usecols=[c for c in usecols if c in pd.read_csv(csv_path, nrows=0).columns], encoding='utf-8', low_memory=True)
    target_song = str(song_title).strip().lower()
    target_artist = str(artist).split(';')[0].strip().lower() if artist else ''
    meta_df['t_song'] = meta_df['track_name'].astype(str).str.strip().str.lower()
    meta_df['t_artist'] = meta_df['artists'].astype(str).str.split(';').str[0].str.strip().str.lower()
    matches_meta = meta_df[(meta_df['t_song'] == target_song) & ((meta_df['t_artist'] == target_artist) | (meta_df['t_artist'].str.contains(target_artist)))]
    if matches_meta.empty:
        matches_meta = meta_df[meta_df['t_song'] == target_song]
    if not matches_meta.empty:
        matched_row = matches_meta.iloc[0]
        album = matched_row.get('album_name', '') if 'album_name' in matched_row.index else ''
        genre_val = matched_row.get('track_genre') if 'track_genre' in matched_row.index else None
        if pd.notna(matched_row.get('duration_ms')):
            try:
                duration_ms_meta = int(matched_row.get('duration_ms'))
            except Exception:
                duration_ms_meta = None
        if pd.notna(matched_row.get('tempo')):
            tempo_val = matched_row.get('tempo')
        if 'explicit' in matched_row.index and pd.notna(matched_row.get('explicit')):
            explicit_flag = matched_row.get('explicit')
    else:
        album = ''
except Exception:
    album = ''
    genre_val = None
    duration_ms_meta = None
    tempo_val = None
    explicit_flag = None
    country_val = None

# Attempt to fetch artwork, preview and country via iTunes Search API with better matching
artwork = None
preview_url = None
track_view_url = None
try:
    term = f"{artist} {song_title}"
    itunes = requests.get('https://itunes.apple.com/search', params={'term': term, 'entity': 'song', 'limit': 5}, timeout=10)
    if itunes.status_code == 200:
        data = itunes.json()
        results = data.get('results', [])
        chosen = None
        target_song = str(song_title).strip().lower()
        target_artist = str(artist).strip().lower()
        for r in results:
            if str(r.get('trackName', '')).strip().lower() == target_song and str(r.get('artistName', '')).strip().lower() == target_artist:
                chosen = r
                break
        if chosen is None:
            for r in results:
                if str(r.get('trackName', '')).strip().lower() == target_song:
                    chosen = r
                    break
        if chosen is None and results:
            chosen = results[0]
        if chosen:
            artwork = chosen.get('artworkUrl100')
            preview_url = chosen.get('previewUrl')
            track_view_url = chosen.get('trackViewUrl') or chosen.get('collectionViewUrl')
            country_val = chosen.get('country')
            if artwork:
                artwork = artwork.replace('100x100bb', '500x500bb')
except Exception:
    artwork = None
    preview_url = None
    track_view_url = None
    country_val = None

# Create an overview using metadata only; do not reuse lyrics text.
overview_text = None
summary_parts = []
if genre_val and pd.notna(genre_val):
    summary_parts.append(f"a {genre_val} track")
if album:
    summary_parts.append(f"from the album {album}")
if duration_ms_meta:
    mins = duration_ms_meta // 60000
    secs = (duration_ms_meta % 60000) // 1000
    summary_parts.append(f"lasting {mins}:{secs:02d}")
if country_val:
    summary_parts.append(f"originating from {country_val}")
if summary_parts:
    overview_text = "This song is " + ", ".join(summary_parts) + "."

st.set_page_config(layout='wide')
st.title('Song Details')

# Select the main detail field: genre only.
primary_field = None
primary_value = None
if genre_val and pd.notna(genre_val):
    primary_field = 'Genre'
    primary_value = str(genre_val).split(';')[0].split(',')[0].strip()

col1, col2 = st.columns([1, 2])
with col1:
    if artwork:
        st.image(artwork, width=500)
    else:
        st.image('https://via.placeholder.com/500x500?text=No+Artwork', width=500)
    if preview_url:
        st.audio(preview_url)

with col2:
    st.header(song_title)
    st.write('**Artist:**', artist)
    st.write('**Album:**', album if album else 'Unknown Album')
    if overview_text:
        st.write('**Overview:**', overview_text)
    if primary_field and primary_value:
        st.write(f'**{primary_field}:**', primary_value)
    if duration_ms_meta:
        mins = duration_ms_meta // 60000
        secs = (duration_ms_meta % 60000) // 1000
        st.write('**Duration:**', f"{mins}:{secs:02d}")

    # External links
    query = requests.utils.quote(f"{song_title} {artist}")
    youtube_url = f"https://www.youtube.com/results?search_query={query}"
    spotify_url = f"https://open.spotify.com/search/{query}"
    youtube_logo = 'https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg'
    spotify_logo = 'https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg'
    st.markdown(
        f"<div style='margin-top:12px;'>"
        f"<a href='{youtube_url}' target='_blank' style='text-decoration:none;margin-right:16px;'>"
        f"<img src='{youtube_logo}' width='24' style='vertical-align:middle;margin-right:6px;'/>YouTube</a>"
        f"<a href='{spotify_url}' target='_blank' style='text-decoration:none;'>"
        f"<img src='{spotify_logo}' width='24' style='vertical-align:middle;margin-right:6px;'/>Spotify</a>"
        f"</div>",
        unsafe_allow_html=True,
    )
    if track_view_url:
        st.markdown(
            f"<div style='margin-top:8px;'>"
            f"<a href='{track_view_url}' target='_blank' style='text-decoration:none;color:#1DB954;font-weight:bold;'>"
            f"Open full song on iTunes</a>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.write('---')

# Lyrics: try lyrics.ovh
lyrics = None
try:
    artist_for_api = str(artist).split(';')[0] if artist else ''
    lyrics_resp = requests.get(f'https://api.lyrics.ovh/v1/{artist_for_api}/{song_title}', timeout=10)
    if lyrics_resp.status_code == 200:
        lyrics = lyrics_resp.json().get('lyrics')
except Exception:
    lyrics = None

st.subheader('Lyrics')
# Center lyrics with styling
cols = st.columns([1, 2, 1])
with cols[1]:
    if lyrics:
        safe_lyrics = str(lyrics).replace('\n', '<br/>')
        st.markdown(
            f"<div style='background:#f8f9fa;padding:16px;border-radius:8px;line-height:1.6;font-size:16px;color:#111;'>" \
            f"{safe_lyrics}" \
            "</div>",
            unsafe_allow_html=True,
        )
        # download button for lyrics
        try:
            st.download_button('Download Lyrics', data=str(lyrics), file_name=f"{song_title} - lyrics.txt", mime='text/plain', key='download_lyrics')
        except Exception:
            pass
    else:
        st.info('Lyrics not available via lyrics.ovh. You can provide lyrics in the dataset or integrate another lyrics API.')

st.write('---')

# Additional metadata table
meta = {}
for col in ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'speechiness', 'loudness', 'key', 'mode', 'time_signature']:
    if col in df.columns:
        meta[col] = row.get(col)
if matched_row is not None and 'track_genre' in matched_row.index:
    meta['genre'] = matched_row.get('track_genre')
if meta:
    st.subheader('Audio Features')
    st.write(meta)

if st.button('← Back to Recommendations', key='back_from_song'):
    st.switch_page('app.py')
# ContentCompass: Entertainment Recommender System

![Movie Recommendation](https://img.shields.io/badge/Movie%20System-Implemented-brightgreen)
![Song Recommendation](https://img.shields.io/badge/Song%20System-Planned-yellow)
![Streamlit App](https://img.shields.io/badge/Built%20With-Streamlit-FF4B4B)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A comprehensive entertainment recommender system that provides personalized movie recommendations using natural language processing and cosine similarity. The system features a clean Streamlit interface with tabs for Movies and Songs (song system planned for future implementation).

## 🎬 Features

### ✅ Currently Implemented (Movie System)
- **Smart Movie Recommendations**: Select a movie and get 8 personalized recommendations with match percentages
- **Detailed Movie Pages**: Comprehensive information including:
  - 🎥 Movie poster and title
  - 🏷️ Tagline, rating, release date, runtime
  - 💰 Budget and revenue (formatted)
  - 🎭 Genres, original language, popularity, vote count, status
  - 📖 Full overview
  - 👥 Top cast with profile pictures and character names
  - ⭐ User reviews with star ratings
  - 📺 Watch providers (streaming, rent, buy options)
- **User-Friendly Interface**: Clean, responsive design with intuitive navigation
- **Performance Optimized**: Utilizes pickle files for fast loading of precomputed similarity matrices
- **Real-time Data**: Fetches current information from The Movie Database (TMDB) API

### 🎵 Planned (Song System)
- **Audio Feature Analysis**: Extract and analyze audio characteristics (tempo, key, timbre, etc.)
- **Lyric Processing**: Natural language processing of song lyrics for thematic similarity
- **Metadata Integration**: Utilize artist, album, genre, and release information
- **Hybrid Recommendation**: Combine content-based and collaborative filtering approaches
- **Rich Song Details**: Display album art, lyrics excerpts, artist bio, and streaming links
- **Mood-Based Suggestions**: Recommend songs based on emotional valence and energy levels

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ContentCompass.git
   cd ContentCompass
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install streamlit pandas requests scikit-learn nltk
   ```

4. **Download the required NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt')"
   ```

5. **Ensure the model files are present**
   - The repository should contain `Models/movie_list.pkl` and `Models/similarity.pkl`
   - If missing, run the provided Jupyter notebook (`Notebooks/movie-recommeder-system.ipynb`) to generate these files

## 🚀 Usage

1. **Start the Streamlit application**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to the provided local URL (typically http://localhost:8501)

3. **Movie Recommendations**:
   - Select a movie from the dropdown in the "Movies" tab
   - Click "Recommend" to see 8 similar movies with match percentages
   - Click any movie poster to view detailed information
   - Use the "← Back to Recommendations" button to return

4. **Song Recommendations** (Coming Soon):
   - Navigate to the "Songs" tab
   - Select a song from the dropdown (placeholder until implementation)
   - Click "Recommend Songs" to get personalized suggestions

## 📂 Project Structure

```
ContentCompass/
├── app.py                 # Main Streamlit application with Movie/Song tabs
├── README.md              # This file
├── LICENSE                # MIT License
├── Notebooks/
│   └─ movie-recommeder-system.ipynb   # Jupyter notebook for movie model generation
├── Models/
│   ├─ movie_list.pkl     # Pickled DataFrame with movie data and tags
│   └─ similarity.pkl     # Pickled cosine similarity matrix (movie-movie)
├── pages/
│   ├─ movie_details.py   # Detailed view for selected movie
│   └─ song_details.py    # Stub for future song details page
├── Data/
│   ├─ movie_data/
│   │   ├─ movies.csv     # Raw movie metadata from TMDB (~4800 movies)
│   │   └─ credits.csv    # Raw cast and crew data
│   └─ songs_data/
│       ├─ dataset.csv.zip # Placeholder for song audio/lyrics features
│       └─ regional_metadata.xlsx # Placeholder for song metadata
└── venv/                  # Virtual environment (if created)
```

## 🔧 How It Works

### Movie Recommendation Pipeline
1. **Data Preprocessing** (in `Notebooks/movie-recommeder-system.ipynb`):
   - Load and merge movie credits data from TMDB CSV files
   - Extract features: overview, genres, keywords, cast, crew
   - Convert JSON-string features to cleaned lists of strings
   - Create comprehensive tags by combining all features
   - Apply text stemming (PorterStemmer) and vectorization (CountVectorizer)
   - Compute cosine similarity matrix between all movie tag vectors
   - Save processed data as `movie_list.pkl` and similarity matrix as `similarity.pkl`

2. **Real-time Recommendation**:
   - User selects a movie → find its index in the DataFrame
   - Retrieve cosine similarity scores for that movie vs. all others
   - Sort by similarity score (descending) and exclude the movie itself
   - Return top 8 movies as recommendations
   - Match percentage = min((similarity_score × 100) + 50, 99) for better UX

3. **Details Page Enhancement**:
   - Uses TMDB API with hardcoded key (replace with your own for production)
   - Fetches poster, details, credits, reviews, and watch providers
   - Formats data attractively with Streamlit components

### Future Song Recommendation Pipeline
1. **Audio Analysis**:
   - Extract features using Librosa: MFCC, chroma, spectral contrast, zero-crossing rate
   - Get audio characteristics: tempo, key, loudness, danceability, energy
2. **Lyric Processing**:
   - Clean and tokenize lyrics
   - Apply TF-IDF or word embeddings (Word2Vec/GloVe)
   - Detect sentiment and thematic elements
3. **Metadata Fusion**:
   - Combine audio features, lyric vectors, and metadata (artist, genre, year)
   - Create unified song embeddings
4. **Similarity Computation**:
   - Calculate cosine similarity in the unified embedding space
   - Apply hybrid weighting (audio 40%, lyrics 30%, metadata 30%)
5. **Recommendation Generation**:
   - Return top songs with similarity scores and explanations

## 🔑 API Key Configuration

The application uses TMDB API with a demonstration key. For production use:

1. **Get your own API key** from [TMDB](https://www.themoviedb.org/settings/api)
2. **Replace the key** in both files:
   - In `app.py` line 30: `api_key=YOUR_KEY_HERE`
   - In `pages/movie_details.py` lines 33, 43, 53, 63: `api_key=YOUR_KEY_HERE`

> ⚠️ **Important**: Never commit real API keys to public repositories. Consider using environment variables or Streamlit secrets for deployment.

## 🗺️ Roadmap

### Phase 1: Movie System (Complete)
- [x] Core recommendation algorithm
- [x] Detailed movie pages
- [x] TMDB API integration
- [x] Streamlit interface

### Phase 2: Song System Foundation
- [ ] Audio feature extraction pipeline
- [ ] Lyric processing module
- [ ] Metadata normalization
- [ ] Similarity computation implementation

### Phase 3: Song System UI
- [ ] Song recommendation tab in main app
- [ ] Song details page
- [ ] Audio preview integration
- [ ] Lyric display with highlights

### Phase 4: Enhancements
- [ ] User accounts and preferences
- [ ] Feedback loop (like/dislike recommendations)
- [ ] Trending and new release sections
- [ ] Mood-based and activity-based suggestions
- [ ] Cross-media recommendations (movies with soundtracks)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Keep functions focused and well-documented
- Add type hints where beneficial
- Write clear commit messages
- Test changes locally before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) - For the fantastic app framework
- [TMDB API](https://www.themoviedb.org/documentation/api) - For comprehensive movie data
- [scikit-learn](https://scikit-learn.org) - For machine learning utilities
- [NLTK](https://www.nltk.org) - For natural language processing tools
- [Pandas](https://pandas.pydata.org) - For data manipulation and analysis
- [NumPy](https://numpy.org) - For numerical computations

---

*Made with ❤️ by ContentCompass Team*  
*Last updated: May 2026*
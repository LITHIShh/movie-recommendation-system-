import pickle
import streamlit as st
import requests
import difflib
import pandas as pd

st.set_page_config(
    page_title="app.py",
    page_icon=":rocket:",  # You can set an emoji or an image path as the icon
    layout="wide",  # or "centered" or "wide"
    initial_sidebar_state="expanded"  # or "collapsed"
)
# Load movie data from CSV
movies_data = pd.read_csv('movies.csv')

# Load similarity matrix from pickled file
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Function to fetch movie poster using The Movie Database (TMDb) API
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

# Function to recommend movies
def recommend(movie_name, movies_data, similarity, num_suggestions=5):
    list_of_all_titles = movies_data['title'].tolist()

    find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)

    if not find_close_match:
        print(f"No close match found for '{movie_name}'.")
        return [], []  # Return empty lists if no close match is found

    close_match = find_close_match[0]

    matching_movies = movies_data[movies_data.title == close_match]

    if matching_movies.empty:
        print(f"No movie found for '{close_match}'.")
        return [], []

    index_of_the_movie = matching_movies.index[0]

    if index_of_the_movie >= len(similarity):
        print(f"Index out of bounds for movie '{close_match}'.")
        return [], []

    similarity_score = list(enumerate(similarity[index_of_the_movie]))

    sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

    recommended_movie_names = []
    recommended_movie_posters = []

    print('Movies suggested for you:\n')

    for i, movie in enumerate(sorted_similar_movies):
        index = movie[0]
        if index < len(movies_data):
            title_from_index = movies_data[movies_data.index == index]['title'].values[0]
            movie_id = movies_data[movies_data.index == index]['id'].values[0]  # Assuming the column name is 'id'
            if i < num_suggestions:
                recommended_movie_names.append(title_from_index)
                recommended_movie_posters.append(fetch_poster(movie_id))
                print(f"{i + 1}. {title_from_index}")

    return recommended_movie_names, recommended_movie_posters

# Streamlit app
st.header('Movie Recommender System')

# Dropdown to select a movie
movie_list = movies_data['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

# Button to trigger recommendation
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies_data, similarity)
    
    # Display recommended movies and posters in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    for i, (name, poster) in enumerate(zip(recommended_movie_names, recommended_movie_posters)):
        with col1 if i == 0 else col2 if i == 1 else col3 if i == 2 else col4 if i == 3 else col5:
            st.text(name)
            st.image(poster)

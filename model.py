import pandas as pd
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies_data = pd.read_csv("movies.csv")
selected_features = ['genres', 'cast', 'director']

for feature in selected_features:
    movies_data[feature] = movies_data[feature].fillna('')

combined_features = movies_data['genres'] + ' ' + movies_data['cast'] + ' ' + movies_data['director']

vectorizer = TfidfVectorizer()
feature_vectors = vectorizer.fit_transform(combined_features)
similarity = cosine_similarity(feature_vectors)

# Function to get movie recommendations
def get_movie_recommendations(movie_name):
    find_close_match = difflib.get_close_matches(movie_name, movies_data['title'].tolist())

    if not find_close_match:
        return None

    close_match = find_close_match[0]
    index_of_the_movie = movies_data[movies_data.title == close_match].index[0]
    similarity_score = list(enumerate(similarity[index_of_the_movie]))
    sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)[:10]

    recommendations = []
    for i, (index, score) in enumerate(sorted_similar_movies, start=1):
        title_from_index = movies_data.loc[index, 'title']
        recommendations.append({"title": title_from_index, "similarity_score": score})

    return recommendations


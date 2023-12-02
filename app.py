from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create the database and the table
with app.app_context():
    db.create_all()


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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error='Username already exists. Please choose a different one.')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        with app.app_context():
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with app.app_context():
            user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            return redirect(url_for('movies'))
        else:
            return 'Login failed. Check your username and password.'

    return render_template('login.html')




@app.route('/movies')
def movies():
    return render_template('movies.html')

@app.route('/recommend', methods=['GET','POST'])
def recommend():
    movie_name = request.form.get('movie_name', '')
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        recommendations = get_movie_recommendations(movie_name)

        if recommendations is None:
            return render_template('movies.html', error_message="Sorry, no close match found for the entered movie.")

        return render_template('movies.html', movie_name=movie_name, recommendations=recommendations)
    
@app.route('/about')
def about():
    return render_template('about.html')




if __name__ == '__main__':
    app.run(debug=True)
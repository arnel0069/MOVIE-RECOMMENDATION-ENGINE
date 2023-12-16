from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from model import get_movie_recommendations



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

        return render_template('movies.html') 
        
@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/projectsynopsis')
def projectsynopsis():
    return render_template('projectsynopsis.html')


if __name__ == '__main__':
    app.run(debug=True)
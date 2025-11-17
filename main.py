from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired
import requests



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

MOVIE_DB_API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyZjA1YmFhYWIwYTJmN2JhZWU2N2Q5NTYzYWQ4NjUxMSIsIm5iZiI6MTc2Mjk5MTQ1Mi40NTIsInN1YiI6IjY5MTUxZDVjNWZiNzZjZTFmOGEwZGIyOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.SPhJFVgzbI-91P1E3UUXyEuQE8Gd6ZbzRVyCYwrIeNI'
MOVIE_DB_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_IMAGE="https://image.tmdb.org/t/p/original/"


# CREATE DB
class Base(DeclarativeBase):
    pass
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///project.db'
db=SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE
class  Movie(db.Model):
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True,nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    ratings: Mapped[int] = mapped_column(Integer, nullable=False)
    rankings: Mapped[int] = mapped_column(Integer, nullable=False)
    reviews: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

with app.app_context():
    db.create_all()

class MyForm(FlaskForm):
    rating= StringField('rating')
    review= StringField('review')
    submit=SubmitField('Done')

class AddMovie(FlaskForm):
    movie_name= StringField('Movie name')
    submit=SubmitField('Add Movie')


@app.route("/")
def home():
    result =db.session.execute(db.select(Movie))
    all_books=result.scalars().all()
    return render_template("index.html", all_books=all_books)

@app.route("/edit", methods=['GET','POST'])
def edit():
    form=MyForm()
    movie_id=request.args.get('id')
    movie_to_edit=db.get_or_404(Movie,movie_id)
    if form.validate_on_submit():
        movie_to_edit.ratings=form.rating.data
        movie_to_edit.reviews=form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html',form=form,movie=movie_to_edit)

@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add',methods=['GET','POST'])
def add():
    form=AddMovie()
    if form.validate_on_submit():
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {MOVIE_DB_API_KEY}"
        }
        params = {
            'query': form.movie_name.data
        }
        response = requests.get(url=MOVIE_DB_URL, headers=headers, params=params)
        data = response.json()
        movie_list = data['results']
        return render_template('select.html', movie_list=movie_list)
    return render_template('add.html',form=form)

@app.route("/get_movie")
def get_movie():
    movie_id=request.args.get('id')
    if movie_id:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {MOVIE_DB_API_KEY}"
        }
        response = requests.get(url=f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US", headers=headers)
        data = response.json()
        title=data["original_title"]
        img_url=f"{MOVIE_DB_IMAGE}{data['poster_path']}"
        description=data['overview']
        year=data['release_date']
        new_movie=Movie(title=title,
                        year=year,
                        description=description,
                        img_url=img_url,ratings=0,rankings=0,reviews='')
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit',id=new_movie.id))



if __name__ == '__main__':
     app.run(debug=True)


from models.movie_model import get_movies


movies = get_movies(5)


for movie in movies:
    print(movie)
import requests
from dotenv import load_dotenv
import os
import re

from backend.config import db

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
#print("API KEY:", TMDB_API_KEY)

movies_collection = db["movies"]

def clean_title(title):
    match = re.match(r"(.+)\s\((\d{4})\)", title)
    if match:
        name = match.group(1)
        year = match.group(2)
        return name, year

    return title, None

def get_movie_images(title):
    name, year = clean_title(title)
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": name,
        "year": year
    }

    response = requests.get(
        url,
        params=params
    )

    data = response.json()
    print(data)

    if data.get("results"):
        movie = data["results"][0]
        return (
            movie.get("poster_path"),
            movie.get("backdrop_path"),
            movie.get("overview")
        )

    return None, None, None

def update_movies():
    movies = movies_collection.find()

    for movie in movies:
        title = movie["title"]
        poster, backdrop, overview = get_movie_images(title)
        print(title)
        print("Poster:", poster)
        print("Backdrop:", backdrop)

        if poster or backdrop:
            movies_collection.update_one(
                {
                    "_id": movie["_id"]
                },
                {
                    "$set": {
                        "poster":
                        "https://image.tmdb.org/t/p/w500" + poster
                        if poster else None,

                        "backdrop":
                        "https://image.tmdb.org/t/p/original" + backdrop
                        if backdrop else None,
                        "overview": overview
                    }
                }
            )

if __name__ == "__main__":

    update_movies()
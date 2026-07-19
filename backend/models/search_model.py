import re
from backend.config import db

movies_collection = db["movies"]
ratings_collection = db["ratings"]

# ovde izdvajamo naziv filma bez godine
def add_display_title(movie):

    movie["display_title"] = re.sub(
        r"\s*\(\d{4}\)$",
        "",
        movie["title"]
    )

    return movie

def search_movies(query="", genre="", year="", limit=100):

    filters = []

    if query:
        filters.append({
            "title": {
                "$regex": re.escape(query),
                "$options": "i"
            }
        })

    if genre:
        filters.append({
            "genres": {
                "$regex": rf"(^|\|){re.escape(genre)}(\||$)",
                "$options": "i"
            }
        })

    if year:
        filters.append({
            "title": {
                "$regex": rf"\({re.escape(year)}\)$"
            }
        })

    mongo_filter = {}

    if filters:
        mongo_filter = {
            "$and": filters
        }

    movies = list(
        movies_collection.find(
            mongo_filter
        ).limit(limit)
    )

    movie_ids = [
        movie["movieId"]
        for movie in movies
    ]

    if not movie_ids:
        return movies

    pipeline = [
        {
            "$match": {
                "movieId": {
                    "$in": movie_ids
                }
            }
        },
        {
            "$group": {
                "_id": "$movieId",
                "average_rating": {
                    "$avg": "$rating"
                },
                "rating_count": {
                    "$sum": 1
                }
            }
        }
    ]

    statistics = list(
        ratings_collection.aggregate(pipeline)
    )

    statistics_by_movie = {
        item["_id"]: item
        for item in statistics
    }

    for movie in movies:
        add_display_title(movie)

        stats = statistics_by_movie.get(
            movie["movieId"]
        )

        if stats is None:
            movie["average_rating"] = None
            movie["rating_count"] = 0
        else:
            movie["average_rating"] = round(
                stats["average_rating"],
                2
            )

            movie["rating_count"] = int(
                stats["rating_count"]
            )

    return movies


def get_all_genres():

    genre_strings = movies_collection.distinct("genres")

    genres = set()

    for genre_string in genre_strings:

        if not genre_string:
            continue

        for genre in genre_string.split("|"):
            genres.add(genre)

    return sorted(genres)


def get_all_years():

    years = set()

    cursor = movies_collection.find(
        {},
        {
            "title": 1
        }
    )

    for movie in cursor:

        title = movie.get("title", "")

        match = re.search(r"\((\d{4})\)$", title)

        if match:
            years.add(match.group(1))

    return sorted(years, reverse=True)
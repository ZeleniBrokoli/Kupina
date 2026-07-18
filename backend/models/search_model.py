import re

from backend.config import db


movies_collection = db["movies"]


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

    return list(
        movies_collection.find(mongo_filter).limit(limit)
    )


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
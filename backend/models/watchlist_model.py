from backend.config import db
from datetime import datetime
import re

watchlist_collection = db["watchlist"]
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

def add_to_watchlist(user_id, movie_id):

    item = {
        "userId": user_id,
        "movieId": movie_id,
        "addedAt": int(datetime.now().timestamp())
    }
    watchlist_collection.insert_one(item)

def remove_from_watchlist(user_id, movie_id):

    watchlist_collection.delete_one(
        {
            "userId": user_id,
            "movieId": movie_id
        }
    )

def is_in_watchlist(user_id, movie_id):

    item = watchlist_collection.find_one(
        {
            "userId": user_id,
            "movieId": movie_id
        }
    )
    return item is not None

def get_user_watchlist(user_id):

    watchlist_items = list(
        watchlist_collection.find(
            {
                "userId": user_id
            }
        ).sort(
            "addedAt",
            -1
        )
    )

    movie_ids = [
        item["movieId"]
        for item in watchlist_items
    ]

    if not movie_ids:
        return []

    movies = list(
        movies_collection.find(
            {
                "movieId": {
                    "$in": movie_ids
                }
            }
        )
    )

    ratings_pipeline = [
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
        ratings_collection.aggregate(
            ratings_pipeline
        )
    )

    movies_by_id = {
        movie["movieId"]: movie
        for movie in movies
    }

    statistics_by_movie_id = {
        item["_id"]: item
        for item in statistics
    }

    results = []

    for item in watchlist_items:

        movie = movies_by_id.get(
            item["movieId"]
        )

        if movie is None:
            continue

        add_display_title(movie)

        movie_statistics = (
            statistics_by_movie_id.get(
                movie["movieId"]
            )
        )

        if movie_statistics is None:
            movie["average_rating"] = None
            movie["rating_count"] = 0
        else:
            movie["average_rating"] = round(
                movie_statistics[
                    "average_rating"
                ],
                2
            )

            movie["rating_count"] = int(
                movie_statistics[
                    "rating_count"
                ]
            )

        movie["addedAt"] = item.get(
            "addedAt"
        )

        results.append(movie)

    return results
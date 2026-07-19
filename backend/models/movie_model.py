from backend.config import db
import re
movies_collection = db["movies"]
ratings_collection = db["ratings"]

# Ovo koristimo za prikaz filmova na Movies stranici
def get_movies(limit):
    movies = list(
        movies_collection
        .find()
        .limit(limit)
    )

    movie_ids = [
        movie["movieId"]
        for movie in movies
    ]

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

    statistics_by_movie_id = {
        item["_id"]: item
        for item in statistics
    }

    for movie in movies:
        add_display_title(movie)

        movie_statistics = statistics_by_movie_id.get(
            movie["movieId"]
        )

        if movie_statistics is None:
            movie["average_rating"] = None
            movie["rating_count"] = 0
            continue

        movie["average_rating"] = round(
            movie_statistics["average_rating"],
            2
        )

        movie["rating_count"] = int(
            movie_statistics["rating_count"]
        )

    return movies

# ovo koristimo za prikaz pojedinacnog filma
def get_movie_by_id(movie_id):
    movie = movies_collection.find_one({"movieId": movie_id})
    if movie:
        add_display_title(movie)

    return movie

# ovde izdvajamo naziv filma bez godine
def add_display_title(movie):

    movie["display_title"] = re.sub(
        r"\s*\(\d{4}\)$",
        "",
        movie["title"]
    )

    return movie

# izbacuje filmove koji imaju manje od 50 ocena
def get_top_movies(limit):
    pipeline = [
        {
            "$group": {
                "_id": "$movieId",
                "average_rating": { "$avg": "$rating" },
                "rating_count": { "$sum": 1 }
            }
        },
        {
            "$match": {
                "rating_count": { "$gte": 50 }
            }
        },
        {
            "$sort": {
                "average_rating": -1,
                "rating_count": -1,
            }
        },
        {
            "$limit": limit
        }
    ]

    ratings = list(
        ratings_collection.aggregate(pipeline)
    )

    movie_ids = [
        r["_id"]
        for r in ratings
    ]

    movies = list(
        movies_collection.find(
            {
                "movieId": { "$in": movie_ids }
            }
        )
    )

    movies_by_id = {
        movie["movieId"]: movie
        for movie in movies
    }

    results = []

    for item in ratings:
        movie = movies_by_id.get(item["_id"])

        add_display_title(movie)

        if movie is None:
            continue

        movie["average_rating"] = round(
            item["average_rating"],
            2
        )
        movie["rating_count"] = item["rating_count"]

        results.append(movie)

    return results

# Filmovi koje je ocenio najveći broj korisnika
def get_trending_movies(limit):
    pipeline = [
        {
            "$group": {
                "_id": "$movieId",
                "rating_count": {
                    "$sum": 1
                },
                "average_rating": {
                    "$avg": "$rating"
                }
            }
        },
        {
            "$sort": {
                "rating_count": -1,
                "average_rating": -1
            }
        },
        {
            "$limit": limit
        }
    ]

    statistics = list(
        ratings_collection.aggregate(pipeline)
    )

    movie_ids = [
        item["_id"]
        for item in statistics
    ]

    movies = list(
        movies_collection.find(
            {
                "movieId": {
                    "$in": movie_ids
                }
            }
        )
    )

    movies_by_id = {
        movie["movieId"]: movie
        for movie in movies
    }

    results = []

    for item in statistics:
        movie = movies_by_id.get(
            item["_id"]
        )

        add_display_title(movie)

        if movie is None:
            continue

        movie["rating_count"] = int(
            item["rating_count"]
        )

        movie["average_rating"] = round(
            item["average_rating"],
            2
        )

        results.append(movie)

    return results
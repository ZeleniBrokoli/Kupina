from backend.config import db

movies_collection = db["movies"]
ratings_collection = db["ratings"]

# ovo koristimo za prikaz filmova u kartici movies
def get_movies(limit):
    return list(movies_collection.find().limit(limit))

# ovo koristimo za prikaz pojedinacnog filma
def get_movie_by_id(movie_id):
    return movies_collection.find_one({"movieId": movie_id})

# izbacuje filmove koji imaju manje od 50 ocena
def get_top_movies(limit):
    pipeline = [
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
        },
        {
            "$match": {
                "rating_count": {
                    "$gte": 50
                }
            }
        },
        {
            "$sort": {
                "average_rating": -1
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
                "movieId": {
                    "$in": movie_ids
                }
            }
        )
    )

    return movies

# filmovi koje je ocenilo najvise ljudi
def get_trending_movies(limit):

    pipeline = [
        {
            "$group": {
                "_id": "$movieId",
                "rating_count": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "rating_count": -1
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
                "movieId": {
                    "$in": movie_ids
                }
            }
        )
    )

    return movies
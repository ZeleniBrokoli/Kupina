from backend.config import db
from datetime import datetime


ratings_collection = db["ratings"]


def add_rating(user_id, movie_id, rating):

    existing_rating = ratings_collection.find_one(
        {
            "userId": user_id,
            "movieId": movie_id
        }
    )


    if existing_rating:

        ratings_collection.update_one(

            {
                "userId": user_id,
                "movieId": movie_id
            },

            {
                "$set": {

                    "rating": rating,
                    "timestamp": int(datetime.now().timestamp())

                }
            }

        )


    else:

        rating_document = {

            "userId": user_id,
            "movieId": movie_id,
            "rating": rating,
            "timestamp": int(datetime.now().timestamp())

        }


        ratings_collection.insert_one(
            rating_document
        )


def get_movie_ratings(movie_id):

    return list(
        ratings_collection.find(
            {
                "movieId": movie_id
            }
        )
    )

def get_movie_average_rating(movie_id):

    ratings = get_movie_ratings(movie_id)


    if len(ratings) == 0:
        return 0, 0


    total = sum(
        r["rating"] for r in ratings
    )


    average = round(
        total / len(ratings),
        1
    )


    return average, len(ratings)

def get_user_rating(user_id, movie_id):

    rating = ratings_collection.find_one(
        {
            "userId": user_id,
            "movieId": movie_id
        }
    )

    if rating:
        return rating["rating"]

    return 0

def get_rating(user_id, movie_id):

    rating = ratings_collection.find_one({

        "userId": user_id,
        "movieId": movie_id

    })

    return rating
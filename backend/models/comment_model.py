from backend.config import db
from datetime import datetime
from backend.models.rating_model import get_rating

comments_collection = db["comments"]


def add_comment(user_id, username, movie_id, text):

    comments_collection.insert_one({

        "userId": user_id,

        "username": username,

        "movieId": movie_id,

        "text": text,

        "createdAt": datetime.now()

    })


def get_movie_comments(movie_id):

    comments = list(

        comments_collection.find(
            {
                "movieId": movie_id
            }
        ).sort("createdAt", -1)

    )

    for comment in comments:

        rating = get_rating(
            comment["userId"],
            movie_id
        )

        comment["rating"] = rating["rating"] if rating else None

    return comments
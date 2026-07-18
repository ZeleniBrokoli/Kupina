from backend.config import db
from datetime import datetime

watchlist_collection = db["watchlist"]

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

    return list(
        watchlist_collection.find(
            {
                "userId": user_id
            }
        )
    )
from backend.config import db
from werkzeug.security import generate_password_hash, check_password_hash

users_collection = db["app_users"]

def create_user(username, email, password):

    hashed_password = generate_password_hash(password)

    last_user = users_collection.find_one(
        sort=[("als_userId", -1)]
    )

    if last_user and "als_userId" in last_user:
        new_als_id = last_user["als_userId"] + 1
    else:
        new_als_id = 6041 #MovieLens ima korisnike od 0 do 6040, pa ovo ide od 6041

    user = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "als_userId": new_als_id
    }

    result = users_collection.insert_one(user)
    return result.inserted_id

def find_user_by_email(email):

    return users_collection.find_one(
        {
            "email": email
        }
    )

def check_password(user, password):

    return check_password_hash(
        user["password"],
        password
    )
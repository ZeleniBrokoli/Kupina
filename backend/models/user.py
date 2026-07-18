from flask_login import UserMixin

#trenutno prijavljeni korisnik
class User(UserMixin):

    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.als_userId = user_data["als_userId"]
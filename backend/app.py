from flask import Flask
from routes.main import main
from flask_login import LoginManager
from backend.models.user_model import users_collection
from backend.models.user import User
from bson.objectid import ObjectId
# from datetime import timezone


app = Flask(__name__)
app.secret_key = "kupina-secret-key"

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "main.login"

app.register_blueprint(main)

@login_manager.user_loader
def load_user(user_id):

    user = users_collection.find_one(
        {
            "_id": ObjectId(user_id)
        }
    )


    if user:

        return User(user)


    return None

@app.template_filter("format_datetime")
def format_datetime(value):
    """
    Pretvara MongoDB datetime u čitljiv format.
    """

    if value is None:
        return "Not available"

    # MongoDB datum može biti zapisan u UTC zoni
    if value.tzinfo is not None:
        value = value.astimezone()

    return value.strftime("%d.%m.%Y. %H:%M")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Blueprint, render_template, request, redirect, url_for, flash
from backend.models.movie_model import (get_movies, get_movie_by_id, get_trending_movies,
                                        get_top_movies)
from backend.models.user import User
from backend.models.user_model import create_user, find_user_by_email
from backend.models.user_model import check_password
from flask_login import login_user, logout_user, current_user, login_required
from backend.models.rating_model import add_rating, get_movie_average_rating, get_user_rating
from backend.models.watchlist_model import (add_to_watchlist, get_user_watchlist,
                                            is_in_watchlist, remove_from_watchlist)

from backend.models.comment_model import add_comment, get_movie_comments
from backend.models.analytics_model import (get_dashboard_stats, get_rating_distribution,
                                            get_top_genres, get_movies_by_year, get_all_spark_analytics,
                                            refresh_spark_analytics, get_als_model_metrics)
from backend.models.search_model import search_movies, get_all_genres, get_all_years
from backend.models.recommendation_model import (
    generate_recommendations_for_user, get_user_rating_count,
    get_user_recommendations, get_last_recommendation_time
)


main = Blueprint("main", __name__)

# Rucno sam probala nekoliko primera, da bih prilagodila izgled stranice na samom pocetku
# @main.route("/")
# def home():
#
#     movies = [
#
#         {
#             "title": "Interstellar",
#             "rating": 8.7,
#             "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
#         },
#
#         {
#             "title": "The Matrix",
#             "rating": 8.7,
#             "poster": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"
#         },
#
#
#         {
#             "title": "Inception",
#             "rating": 8.8,
#             "poster": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg"
#         }
#
#     ]
#
#
#     return render_template(
#         "home.html",
#         movies=movies,
#         top_movies=movies
#     )

@main.route("/")
def home():
    movies = get_trending_movies(10)
    top_movies = get_top_movies(10)

    return render_template(
        "home.html",
        movies=movies,
        top_movies=top_movies
    )

@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = find_user_by_email(email)

        if user and check_password(user, password):
            login_user(User(user))

            flash("Login successful!", "success")

            return redirect(url_for("main.home"))


        flash("Invalid email or password.", "error")


    return render_template("login.html")

@main.route("/logout")
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("main.home"))


@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]


        existing_user = find_user_by_email(email)


        if existing_user:
            return "User already exists"


        create_user(
            username,
            email,
            password
        )


        return redirect(url_for("main.login"))


    return render_template("register.html")

@main.route("/movies")
def movies():

    query = request.args.get(
        "query",
        ""
    ).strip()

    selected_genre = request.args.get(
        "genre",
        ""
    ).strip()

    selected_year = request.args.get(
        "year",
        ""
    ).strip()


    genres = get_all_genres()

    years = get_all_years()


    filters_are_active = (
        query
        or selected_genre
        or selected_year
    )


    if filters_are_active:

        movies_list = search_movies(
            query=query,
            genre=selected_genre,
            year=selected_year,
            limit=100
        )

    else:

        movies_list = get_movies(60)


    return render_template(
        "movies.html",
        movies=movies_list,
        query=query,
        genres=genres,
        years=years,
        selected_genre=selected_genre,
        selected_year=selected_year
    )

@main.route("/movie/<int:movie_id>")
@main.route("/movie/<int:movie_id>")
def movie_details(movie_id):

    movie = get_movie_by_id(movie_id)
    average_rating, number_of_ratings = get_movie_average_rating(movie_id)
    in_watchlist = False

    if current_user.is_authenticated:

        in_watchlist = is_in_watchlist(
            current_user.als_userId,
            movie_id
        )

    user_rating = 0

    if current_user.is_authenticated:
        user_rating = get_user_rating(
            current_user.als_userId,
            movie_id
        )

    comments = get_movie_comments(movie_id)

    return render_template(
        "movie_details.html",
        movie=movie,
        in_watchlist=in_watchlist,
        average_rating=average_rating,
        number_of_ratings=number_of_ratings,
        user_rating=user_rating,
        comments=comments
    )

@main.route("/analytics")
def analytics():

    stats = get_dashboard_stats()
    rating_labels, rating_values = get_rating_distribution()
    genre_labels, genre_values = get_top_genres()
    year_labels, year_values = get_movies_by_year()
    spark_analytics = get_all_spark_analytics()
    als_metrics = get_als_model_metrics()

    return render_template(

        "analytics.html",
        stats=stats,
        labels=rating_labels,
        values=rating_values,
        genre_labels=genre_labels,
        genre_values=genre_values,
        year_labels=year_labels,
        year_values=year_values,
        spark_analytics=spark_analytics,
        als_metrics=als_metrics

    )

@main.route(
    "/analytics/refresh-spark",
    methods=["POST"]
)
@login_required
def refresh_spark_analytics_route():
    try:
        refresh_spark_analytics()

        flash(
            "Spark analytics were refreshed successfully.",
            "success"
        )

    except Exception as error:
        print(error)

        flash(
            "Spark analytics could not be refreshed. "
            "Check the terminal for details.",
            "error"
        )

    return redirect(
        url_for("main.analytics")
    )

@main.route("/movie/<int:movie_id>/rate", methods=["POST"])
@login_required
def rate_movie(movie_id):

    rating = int(request.form["rating"])


    add_rating(
        current_user.als_userId,
        movie_id,
        rating
    )


    flash(
        "Your rating has been saved!",
        "success"
    )


    return redirect(
        url_for(
            "main.movie_details",
            movie_id=movie_id
        )
    )

@main.route("/movie/<int:movie_id>/watchlist", methods=["POST"])
@login_required
def add_movie_to_watchlist(movie_id):

    if is_in_watchlist(
        current_user.als_userId,
        movie_id
    ):

        remove_from_watchlist(
            current_user.als_userId,
            movie_id
        )

        flash(
            "Movie removed from watchlist.",
            "success"
        )


    else:

        add_to_watchlist(
            current_user.als_userId,
            movie_id
        )

        flash(
            "Movie added to watchlist!",
            "success"
        )


    return redirect(
        url_for(
            "main.movie_details",
            movie_id=movie_id
        )
    )

@main.route("/watchlist")
@login_required
def watchlist():

    movies = get_user_watchlist(
        current_user.als_userId
    )

    return render_template(
        "watchlist.html",
        movies=movies
    )

@main.route("/movie/<int:movie_id>/comment", methods=["POST"])
@login_required
def comment_movie(movie_id):

    text = request.form["comment"].strip()

    if text:

        add_comment(
            current_user.als_userId,
            current_user.username,
            movie_id,
            text
        )

        flash(
            "Comment posted!",
            "success"
        )

    return redirect(
        url_for(
            "main.movie_details",
            movie_id=movie_id
        )
    )

@main.route("/recommendations")
@login_required
def recommendations():
    user_id = current_user.als_userId

    if user_id is None:
        return render_template(
            "recommendations.html",
            movies=[],
            rating_count=0,
            last_generated=None
        )

    recommended_movies = get_user_recommendations(
        user_id=user_id,
        limit=10
    )

    rating_count = get_user_rating_count(
        user_id
    )

    last_generated = get_last_recommendation_time(
        user_id
    )

    return render_template(
        "recommendations.html",
        movies=recommended_movies,
        rating_count=rating_count,
        last_generated=last_generated
    )

@main.route(
    "/recommendations/generate",
    methods=["POST"]
)
@login_required
def generate_recommendations():
    user_id = current_user.als_userId

    if user_id is None:
        flash(
            "Your account is not connected to the "
            "recommendation system.",
            "error"
        )

        return redirect(
            url_for("main.recommendations")
        )

    rating_count = get_user_rating_count(user_id)

    if rating_count < 5:
        flash(
            f"You have rated {rating_count} movie(s). "
            "Rate at least 5 movies first.",
            "error"
        )

        return redirect(
            url_for("main.recommendations")
        )

    try:
        output = generate_recommendations_for_user(
            user_id
        )

        print(output)

        flash(
            "Your recommendations were generated "
            "successfully.",
            "success"
        )

    except Exception as error:
        print(error)

        flash(
            "Recommendations could not be generated. "
            "Check the terminal for details.",
            "error"
        )

    return redirect(
        url_for("main.recommendations")
    )
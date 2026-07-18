from backend.config import db
import subprocess
from pathlib import Path

movies_collection = db["movies"]
users_collection = db["users"]
ratings_collection = db["ratings"]
comments_collection = db["comments"]
als_model_metrics_collection = db["als_model_metrics"]
spark_analytics_collection = db["spark_analytics"]


def get_dashboard_stats():

    movies = movies_collection.count_documents({})
    users = users_collection.count_documents({})
    ratings = ratings_collection.count_documents({})
    avg_rating = list(
        ratings_collection.aggregate([
            {
                "$group": {
                    "_id": None,
                    "average": { "$avg": "$rating" }
                }
            }
        ])
    )

    average = round(avg_rating[0]["average"],2)

    return {
        "movies": movies,
        "users": users,
        "ratings": ratings,
        "average": average
    }

def get_rating_distribution():

    pipeline = [
        {
            "$group": {
                "_id": "$rating",
                "count": { "$sum": 1 }
            }
        },
        {
            "$sort": { "_id": 1 }
        }
    ]

    result = list(
        ratings_collection.aggregate(pipeline)
    )

    labels = []
    values = []

    for item in result:
        labels.append(str(item["_id"]))
        values.append(item["count"])

    return labels, values

def get_top_genres():

    pipeline = [

        {
            "$project": {
                "genres": {
                    "$split": [
                        "$genres",
                        "|"
                    ]
                }
            }
        },
        {
            "$unwind": "$genres"
        },
        {
            "$group": {
                "_id": "$genres",
                "count": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "count": -1
            }
        },
        {
            "$limit": 10
        }
    ]

    result = list(
        movies_collection.aggregate(pipeline)
    )

    labels = []
    values = []

    for item in result:
        labels.append(item["_id"])
        values.append(item["count"])

    return labels, values

def get_movies_by_year():

    pipeline = [
        {
            "$project": {
                "year": {
                    "$regexFind": {
                        "input": "$title",
                        "regex": r"\((\d{4})\)"
                    }
                }
            }
        },
        {
            "$match": {
                "year": {
                    "$ne": None
                }
            }
        },
        {
            "$project": {
                "year": {
                    "$arrayElemAt": [ "$year.captures", 0 ]
                }
            }
        },
        {
            "$group": {
                "_id": "$year",
                "count": { "$sum": 1 }
            }
        },
        {
            "$sort": { "_id": 1 }
        }
    ]

    result = list(
        movies_collection.aggregate(pipeline)
    )

    labels = []
    values = []

    for item in result:
        labels.append(item["_id"])
        values.append(item["count"])

    return labels, values


def get_spark_analysis(analysis_name):
    document = spark_analytics_collection.find_one(
        {
            "analysis": analysis_name
        },
        {
            "_id": 0
        }
    )

    if not document:
        return None

    return document


def get_all_spark_analytics():
    return {
        "most_rated_movies": get_spark_analysis(
            "most_rated_movies"
        ),
        "top_rated_movies": get_spark_analysis(
            "top_rated_movies"
        ),
        "most_active_users": get_spark_analysis(
            "most_active_users"
        ),
        "matrix_sparsity": get_spark_analysis(
            "matrix_sparsity"
        ),
        "user_activity_distribution": get_spark_analysis(
            "user_activity_distribution"
        ),
        "movies_by_decade": get_spark_analysis(
            "movies_by_decade"
        ),
        "average_rating_by_genre": get_spark_analysis(
            "average_rating_by_genre"
        ),
        "rating_count_vs_average": get_spark_analysis(
            "rating_count_vs_average"
        )
    }

# pokrece Spark analiticki proces iz .venv-spark okruzenja
def refresh_spark_analytics():
    project_root = Path(__file__).resolve().parents[2]

    spark_python = (
        project_root
        / ".venv-spark"
        / "Scripts"
        / "python.exe"
    )

    if not spark_python.exists():
        raise FileNotFoundError(
            "Spark virtual environment was not found."
        )

    result = subprocess.run(
        [
            str(spark_python),
            "-m",
            "spark.run_analytics"
        ],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=600,
        check=False
    )

    if result.returncode != 0:
        error_message = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Spark analytics process failed."
        )

        raise RuntimeError(error_message)

    return result.stdout.strip()

# Vraca poslednje sacuvane metrike ALS modela
def get_als_model_metrics():

    return als_model_metrics_collection.find_one(
        {
            "model": "ALS"
        },
        {
            "_id": 0
        }
    )
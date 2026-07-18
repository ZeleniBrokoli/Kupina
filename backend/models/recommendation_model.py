from backend.config import db
import subprocess
from pathlib import Path

recommendations_collection = db["recommendations"]
movies_collection = db["movies"]
ratings_collection = db["ratings"]

def get_user_recommendations(
    user_id: int,
    limit: int = 10
) -> list:
    recommendation_documents = list(
        recommendations_collection.find(
            {
                "userId": int(user_id)
            }
        )
        .sort("position", 1)
        .limit(limit)
    )

    if not recommendation_documents:
        return []

    movie_ids = [
        document["movieId"]
        for document in recommendation_documents
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

    for recommendation in recommendation_documents:
        movie = movies_by_id.get(
            recommendation["movieId"]
        )

        if movie is None:
            continue

        movie["predictedRating"] = round(
            recommendation.get(
                "predictedRating",
                0
            ),
            2
        )

        movie["recommendationPosition"] = (
            recommendation.get("position")
        )

        movie["generatedAt"] = recommendation.get(
            "generatedAt"
        )

        results.append(movie)

    return results

def generate_recommendations_for_user(
    user_id: int
) -> str:
    """
    Pokreće Spark proces za generisanje preporuka.
    """

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
            "spark.train_recommendations",
            str(int(user_id))
        ],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=900,
        check=False
    )

    if result.returncode != 0:
        error_message = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Recommendation generation failed."
        )

        raise RuntimeError(error_message)

    return result.stdout.strip()

def get_user_rating_count(user_id: int) -> int:
    """
    Vraća broj filmova koje je korisnik ocenio.
    """

    return ratings_collection.count_documents(
        {
            "userId": int(user_id)
        }
    )

def get_last_recommendation_time(user_id: int):
    latest_recommendation = (
        recommendations_collection
        .find_one(
            {
                "userId": int(user_id)
            },
            sort=[
                (
                    "generatedAt",
                    -1
                )
            ]
        )
    )

    if not latest_recommendation:
        return None

    return latest_recommendation.get(
        "generatedAt"
    )


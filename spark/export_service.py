from datetime import datetime, timezone

from pymongo import MongoClient

from spark.config import DATABASE_NAME, MONGODB_URI


def get_database():
    """
    Vraća vezu ka MongoDB bazi.
    """

    client = MongoClient(MONGODB_URI)

    return client, client[DATABASE_NAME]


def save_analysis_result(
    analysis_name: str,
    data: list[dict]
) -> None:
    """
    Čuva jedan rezultat Spark analize u kolekciji
    spark_analytics.
    """

    client, database = get_database()

    try:
        collection = database["spark_analytics"]

        collection.replace_one(
            {
                "analysis": analysis_name
            },
            {
                "analysis": analysis_name,
                "generatedAt": datetime.now(timezone.utc),
                "data": data
            },
            upsert=True
        )

    finally:
        client.close()


def save_sparsity_metrics(
    metrics: dict
) -> None:
    """
    Čuva pokazatelje gustine i retkosti matrice.
    """

    client, database = get_database()

    try:
        collection = database["spark_analytics"]

        collection.replace_one(
            {
                "analysis": "matrix_sparsity"
            },
            {
                "analysis": "matrix_sparsity",
                "generatedAt": datetime.now(timezone.utc),
                "data": {
                    "numberOfUsers": metrics["number_of_users"],
                    "numberOfMovies": metrics["number_of_movies"],
                    "numberOfRatings": metrics["number_of_ratings"],
                    "possibleRatings": metrics["possible_ratings"],
                    "density": metrics["density"],
                    "sparsity": metrics["sparsity"]
                }
            },
            upsert=True
        )

    finally:
        client.close()
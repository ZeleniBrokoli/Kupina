from datetime import datetime, timezone
import sys

from pymongo import MongoClient

from spark.als_service import (
    evaluate_model,
    generate_user_recommendations,
    split_ratings,
    train_model
)
from spark.config import DATABASE_NAME, MONGODB_URI
from spark.data_loader import load_movielens_data
from spark.data_preparation import prepare_ratings
from spark.session import create_spark_session


MINIMUM_USER_RATINGS = 5

MODEL_RANK = 10
MODEL_MAX_ITER = 10
MODEL_REG_PARAM = 0.1


def save_recommendations(
    user_id: int,
    recommendations_df
) -> int:
    """
    Čuva preporuke izabranog korisnika u MongoDB kolekciji.
    """

    rows = recommendations_df.collect()

    documents = [
        {
            "userId": int(row["userId"]),
            "movieId": int(row["movieId"]),
            "position": int(row["position"]),
            "predictedRating": float(
                row["predictedRating"]
            ),
            "rawPrediction": float(
                row["rawPrediction"]
            ),
            "generatedAt": datetime.now(timezone.utc)
        }
        for row in rows
    ]

    client = MongoClient(MONGODB_URI)

    try:
        database = client[DATABASE_NAME]
        collection = database["recommendations"]

        collection.delete_many(
            {
                "userId": int(user_id)
            }
        )

        if documents:
            collection.insert_many(documents)

    finally:
        client.close()

    return len(documents)


def save_model_metrics(
    rmse: float,
    training_count: int,
    test_count: int,
    prediction_count: int
) -> None:
    """
    Čuva osnovne informacije o poslednjem ALS modelu.
    """

    client = MongoClient(MONGODB_URI)

    try:
        database = client[DATABASE_NAME]
        collection = database["als_model_metrics"]

        collection.replace_one(
            {
                "model": "ALS"
            },
            {
                "model": "ALS",
                "rank": MODEL_RANK,
                "maxIter": MODEL_MAX_ITER,
                "regParam": MODEL_REG_PARAM,
                "rmse": float(rmse),
                "trainingRatings": int(training_count),
                "testRatings": int(test_count),
                "evaluatedPredictions": int(
                    prediction_count
                ),
                "generatedAt": datetime.now(timezone.utc)
            },
            upsert=True
        )

    finally:
        client.close()


def main(user_id: int) -> None:
    spark = create_spark_session(
        app_name="Kupina ALS Recommendations"
    )

    try:
        movies_df, ratings_df, users_df = (
            load_movielens_data(spark)
        )

        prepared_ratings_df = prepare_ratings(
            ratings_df
        )

        user_rating_count = (
            prepared_ratings_df
            .filter(
                prepared_ratings_df.userId == int(user_id)
            )
            .count()
        )

        if user_rating_count < MINIMUM_USER_RATINGS:
            raise ValueError(
                "User must rate at least "
                f"{MINIMUM_USER_RATINGS} movies."
            )

        # Model za evaluaciju
        train_df, test_df = split_ratings(
            prepared_ratings_df
        )

        evaluation_model = train_model(
            train_df,
            rank=MODEL_RANK,
            max_iter=MODEL_MAX_ITER,
            reg_param=MODEL_REG_PARAM
        )

        rmse, prediction_count = evaluate_model(
            evaluation_model,
            test_df
        )

        # Produkcioni model koristi sve dostupne ocene
        production_model = train_model(
            prepared_ratings_df,
            rank=MODEL_RANK,
            max_iter=MODEL_MAX_ITER,
            reg_param=MODEL_REG_PARAM
        )

        recommendations_df = (
            generate_user_recommendations(
                model=production_model,
                ratings_df=prepared_ratings_df,
                user_id=user_id,
                recommendation_count=10,
                candidate_count=50
            )
        )

        recommendation_count = save_recommendations(
            user_id,
            recommendations_df
        )

        save_model_metrics(
            rmse=rmse,
            training_count=train_df.count(),
            test_count=test_df.count(),
            prediction_count=prediction_count
        )

        print(
            f"Generated {recommendation_count} "
            f"recommendations for user {user_id}."
        )

        print(f"ALS RMSE: {rmse:.4f}")

    finally:
        spark.stop()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m "
            "spark.train_recommendations USER_ID"
        )

    main(int(sys.argv[1]))
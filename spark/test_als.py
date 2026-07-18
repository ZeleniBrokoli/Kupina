from spark.als_service import (
    evaluate_model,
    generate_user_recommendations,
    split_ratings,
    train_model
)
from spark.data_loader import load_movielens_data
from spark.data_preparation import prepare_ratings
from spark.session import create_spark_session


def main() -> None:
    spark = create_spark_session(
        app_name="Kupina ALS Test"
    )

    try:
        movies_df, ratings_df, users_df = (
            load_movielens_data(spark)
        )

        prepared_ratings_df = prepare_ratings(
            ratings_df
        )

        train_df, test_df = split_ratings(
            prepared_ratings_df
        )

        model = train_model(
            train_df,
            rank=10,
            max_iter=10,
            reg_param=0.1
        )

        rmse, prediction_count = evaluate_model(
            model,
            test_df
        )

        print(f"RMSE: {rmse:.4f}")
        print(
            "Evaluated predictions:",
            prediction_count
        )

        recommendations_df = (
            generate_user_recommendations(
                model=model,
                ratings_df=prepared_ratings_df,
                user_id=1,
                recommendation_count=10
            )
        )

        print("\nRecommendations for user 1:")

        recommendations_df.show(
            truncate=False
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
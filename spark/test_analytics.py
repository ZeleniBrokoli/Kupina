from spark.analytics_service import (
    calculate_matrix_sparsity,
    get_most_active_users,
    get_most_rated_movies,
    get_top_rated_movies
)
from spark.data_loader import load_movielens_data
from spark.session import create_spark_session


def main() -> None:
    spark = create_spark_session(
        app_name="Kupina Analytics Test"
    )

    try:
        movies_df, ratings_df, users_df = (
            load_movielens_data(spark)
        )

        print("\nMost rated movies:")
        get_most_rated_movies(
            ratings_df,
            movies_df
        ).show(
            truncate=False
        )

        print("\nTop rated movies:")
        get_top_rated_movies(
            ratings_df,
            movies_df
        ).show(
            truncate=False
        )

        print("\nMost active users:")
        get_most_active_users(
            ratings_df
        ).show(
            truncate=False
        )

        print("\nMatrix sparsity:")
        sparsity_metrics = calculate_matrix_sparsity(
            ratings_df
        )

        for key, value in sparsity_metrics.items():
            print(f"{key}: {value}")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
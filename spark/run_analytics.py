from spark.analytics_service import (
    calculate_matrix_sparsity,
    get_average_rating_by_genre,
    get_most_active_users,
    get_most_rated_movies,
    get_movies_by_decade,
    get_top_rated_movies,
    get_user_activity_distribution,
    get_rating_count_vs_average
)
from spark.data_loader import load_movielens_data
from spark.export_service import (
    save_analysis_result,
    save_sparsity_metrics
)
from spark.session import create_spark_session


def dataframe_to_records(dataframe) -> list[dict]:
    """
    Pretvara Spark DataFrame u listu Python rečnika.
    """

    return [
        row.asDict(recursive=True)
        for row in dataframe.collect()
    ]


def main() -> None:
    spark = create_spark_session(
        app_name="Kupina Spark Analytics"
    )

    try:
        movies_df, ratings_df, users_df = (
            load_movielens_data(spark)
        )

        most_rated_movies = get_most_rated_movies(
            ratings_df,
            movies_df,
            limit=10
        )

        top_rated_movies = get_top_rated_movies(
            ratings_df,
            movies_df,
            minimum_ratings=50,
            limit=10
        )

        most_active_users = get_most_active_users(
            ratings_df,
            limit=10
        )

        sparsity_metrics = calculate_matrix_sparsity(
            ratings_df
        )

        user_activity_distribution = (
            get_user_activity_distribution(
                ratings_df
            )
        )

        movies_by_decade = get_movies_by_decade(
            movies_df
        )

        average_rating_by_genre = (
            get_average_rating_by_genre(
                ratings_df,
                movies_df
            )
        )

        rating_count_vs_average = (
            get_rating_count_vs_average(
                ratings_df
            )
        )

        save_analysis_result(
            "most_rated_movies",
            dataframe_to_records(
                most_rated_movies
            )
        )

        save_analysis_result(
            "top_rated_movies",
            dataframe_to_records(
                top_rated_movies
            )
        )

        save_analysis_result(
            "most_active_users",
            dataframe_to_records(
                most_active_users
            )
        )

        save_sparsity_metrics(
            sparsity_metrics
        )

        save_analysis_result(
            "user_activity_distribution",
            dataframe_to_records(
                user_activity_distribution
            )
        )

        save_analysis_result(
            "movies_by_decade",
            dataframe_to_records(
                movies_by_decade
            )
        )

        save_analysis_result(
            "average_rating_by_genre",
            dataframe_to_records(
                average_rating_by_genre
            )
        )

        save_analysis_result(
            "rating_count_vs_average",
            dataframe_to_records(
                rating_count_vs_average
            )
        )

        print(
            "Spark analytics results were successfully "
            "saved to MongoDB."
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
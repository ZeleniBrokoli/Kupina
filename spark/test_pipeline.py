from spark.data_loader import load_movielens_data
from spark.data_preparation import prepare_ratings
from spark.session import create_spark_session


def main() -> None:
    spark = create_spark_session(
        app_name="Kupina Spark Pipeline Test"
    )

    try:
        movies_df, ratings_df, users_df = (
            load_movielens_data(spark)
        )

        prepared_ratings_df = prepare_ratings(
            ratings_df
        )

        print("\nSpark version:")
        print(spark.version)

        print("\nNumber of movies:")
        print(movies_df.count())

        print("\nNumber of ratings:")
        print(ratings_df.count())

        print("\nNumber of users:")
        print(users_df.count())

        print("\nPrepared ratings:")
        print(prepared_ratings_df.count())

        print("\nPrepared ratings schema:")
        prepared_ratings_df.printSchema()

        print("\nFirst prepared ratings:")
        prepared_ratings_df.show(
            5,
            truncate=False
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
from pyspark.sql import DataFrame, SparkSession

from spark.config import DATABASE_NAME


def load_collection(
    spark: SparkSession,
    collection_name: str
) -> DataFrame:
    """
    Učitava jednu MongoDB kolekciju u Spark DataFrame.
    """

    return (
        spark.read
        .format("mongodb")
        .option("database", DATABASE_NAME)
        .option("collection", collection_name)
        .load()
    )


def load_movielens_data(
    spark: SparkSession
) -> tuple[DataFrame, DataFrame, DataFrame]:
    """
    Učitava kolekcije movies, ratings i users.
    """

    movies_df = load_collection(
        spark,
        "movies"
    )

    ratings_df = load_collection(
        spark,
        "ratings"
    )

    users_df = load_collection(
        spark,
        "users"
    )

    return movies_df, ratings_df, users_df
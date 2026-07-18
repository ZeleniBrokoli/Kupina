from pyspark.sql import DataFrame
from pyspark.sql.functions import col, row_number
from pyspark.sql.types import FloatType, IntegerType
from pyspark.sql.window import Window


def prepare_ratings(
    ratings_df: DataFrame
) -> DataFrame:
    """
    Priprema podatke o ocenama za ALS model.

    Zadržava kolone userId, movieId, rating i timestamp,
    konvertuje numeričke tipove, uklanja neispravne zapise
    i za svaki korisnik-film par zadržava najnoviju ocenu.
    """

    prepared_df = (
        ratings_df
        .select(
            col("userId")
            .cast(IntegerType())
            .alias("userId"),

            col("movieId")
            .cast(IntegerType())
            .alias("movieId"),

            col("rating")
            .cast(FloatType())
            .alias("rating"),

            col("timestamp")
        )
        .dropna(
            subset=[
                "userId",
                "movieId",
                "rating"
            ]
        )
        .filter(
            (col("rating") >= 1.0)
            & (col("rating") <= 5.0)
        )
    )

    rating_window = (
        Window
        .partitionBy(
            "userId",
            "movieId"
        )
        .orderBy(
            col("timestamp").desc()
        )
    )

    return (
        prepared_df
        .withColumn(
            "row_number",
            row_number().over(rating_window)
        )
        .filter(
            col("row_number") == 1
        )
        .drop("row_number")
    )
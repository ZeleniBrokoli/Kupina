from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    avg,
    col,
    count,
    desc,
    explode,
    floor,
    regexp_extract,
    split,
    when
)


def get_most_rated_movies(
    ratings_df: DataFrame,
    movies_df: DataFrame,
    limit: int = 10
) -> DataFrame:
    """
    Vraća filmove sa najvećim brojem korisničkih ocena.
    """

    movie_rating_counts = (
        ratings_df
        .groupBy("movieId")
        .agg(
            count("rating").alias("number_of_ratings")
        )
    )

    return (
        movie_rating_counts
        .join(
            movies_df.select(
                "movieId",
                "title",
                "genres"
            ),
            on="movieId",
            how="inner"
        )
        .select(
            "movieId",
            "title",
            "genres",
            "number_of_ratings"
        )
        .orderBy(
            desc("number_of_ratings")
        )
        .limit(limit)
    )


def get_top_rated_movies(
    ratings_df: DataFrame,
    movies_df: DataFrame,
    minimum_ratings: int = 50,
    limit: int = 10
) -> DataFrame:
    """
    Vraća najbolje ocenjene filmove koji imaju
    najmanje zadati broj korisničkih ocena.
    """

    movie_statistics = (
        ratings_df
        .groupBy("movieId")
        .agg(
            avg("rating").alias("average_rating"),
            count("rating").alias("number_of_ratings")
        )
        .filter(
            col("number_of_ratings") >= minimum_ratings
        )
    )

    return (
        movie_statistics
        .join(
            movies_df.select(
                "movieId",
                "title",
                "genres"
            ),
            on="movieId",
            how="inner"
        )
        .select(
            "movieId",
            "title",
            "genres",
            "average_rating",
            "number_of_ratings"
        )
        .orderBy(
            desc("average_rating"),
            desc("number_of_ratings")
        )
        .limit(limit)
    )


def get_most_active_users(
    ratings_df: DataFrame,
    limit: int = 10
) -> DataFrame:
    """
    Vraća korisnike sa najvećim brojem datih ocena.
    """

    return (
        ratings_df
        .groupBy("userId")
        .agg(
            count("rating").alias("number_of_ratings")
        )
        .orderBy(
            desc("number_of_ratings")
        )
        .limit(limit)
    )


def calculate_matrix_sparsity(
    ratings_df: DataFrame
) -> dict:
    """
    Izračunava gustinu i retkost korisničko-filmske matrice.
    """

    number_of_users = (
        ratings_df
        .select("userId")
        .distinct()
        .count()
    )

    number_of_movies = (
        ratings_df
        .select("movieId")
        .distinct()
        .count()
    )

    number_of_ratings = ratings_df.count()

    possible_ratings = (
        number_of_users
        * number_of_movies
    )

    density = (
        number_of_ratings
        / possible_ratings
        if possible_ratings > 0
        else 0
    )

    sparsity = 1 - density

    return {
        "number_of_users": number_of_users,
        "number_of_movies": number_of_movies,
        "number_of_ratings": number_of_ratings,
        "possible_ratings": possible_ratings,
        "density": density,
        "sparsity": sparsity
    }

def get_user_activity_distribution(
    ratings_df: DataFrame
) -> DataFrame:
    """
    Grupisanje korisnika prema broju filmova koje su ocenili.
    """

    user_activity = (
        ratings_df
        .groupBy("userId")
        .agg(
            count("rating").alias("number_of_ratings")
        )
    )

    return (
        user_activity
        .withColumn(
            "activity_range",
            when(
                col("number_of_ratings") <= 50,
                "1-50"
            )
            .when(
                col("number_of_ratings") <= 100,
                "51-100"
            )
            .when(
                col("number_of_ratings") <= 250,
                "101-250"
            )
            .when(
                col("number_of_ratings") <= 500,
                "251-500"
            )
            .otherwise("501+")
        )
        .groupBy("activity_range")
        .agg(
            count("*").alias("number_of_users")
        )
    )

def get_movies_by_decade(
    movies_df: DataFrame
) -> DataFrame:
    """
    Izdvaja godinu iz naslova filma i grupiše filmove po decenijama.
    """

    movies_with_year = (
        movies_df
        .withColumn(
            "year",
            regexp_extract(
                col("title"),
                r"\((\d{4})\)",
                1
            ).cast("int")
        )
        .dropna(
            subset=["year"]
        )
        .filter(
            col("year") > 0
        )
    )

    return (
        movies_with_year
        .withColumn(
            "decade",
            (
                floor(
                    col("year") / 10
                ) * 10
            ).cast("int")
        )
        .groupBy("decade")
        .agg(
            count("*").alias("number_of_movies")
        )
        .orderBy("decade")
    )

def get_average_rating_by_genre(
    ratings_df: DataFrame,
    movies_df: DataFrame
) -> DataFrame:
    """
    Izračunava prosečnu korisničku ocenu po filmskom žanru.
    """

    movie_genres = (
        movies_df
        .select(
            "movieId",
            explode(
                split(
                    col("genres"),
                    r"\|"
                )
            ).alias("genre")
        )
    )

    return (
        ratings_df
        .join(
            movie_genres,
            on="movieId",
            how="inner"
        )
        .groupBy("genre")
        .agg(
            avg("rating").alias("average_rating"),
            count("rating").alias("number_of_ratings")
        )
        .orderBy(
            desc("average_rating")
        )
    )

def get_rating_count_vs_average(
    ratings_df: DataFrame
) -> DataFrame:
    """
    Izračunava broj ocena i prosečnu ocenu za svaki film.
    Rezultat se koristi za scatter dijagram.
    """

    return (
        ratings_df
        .groupBy("movieId")
        .agg(
            count("rating").alias("number_of_ratings"),
            avg("rating").alias("average_rating")
        )
        .orderBy(
            desc("number_of_ratings")
        )
    )
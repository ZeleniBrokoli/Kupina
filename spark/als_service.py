from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    desc,
    explode,
    greatest,
    least,
    lit,
    row_number
)
from pyspark.sql.window import Window

# kreira ALS estimator sa zadatim hiperparametrima
def create_als(
    rank: int = 10,
    max_iter: int = 10,
    reg_param: float = 0.1
) -> ALS:

    return ALS(
        userCol="userId",
        itemCol="movieId",
        ratingCol="rating",
        rank=rank,
        maxIter=max_iter,
        regParam=reg_param,
        implicitPrefs=False,
        nonnegative=True,
        coldStartStrategy="drop",
        seed=42
    )

# Deli ocene na trening i test skup
def split_ratings(
    ratings_df: DataFrame,
    training_ratio: float = 0.8
) -> tuple[DataFrame, DataFrame]:

    return ratings_df.randomSplit(
        [
            training_ratio,
            1 - training_ratio
        ],
        seed=42
    )

#Trenira ALS model nad prosleđenim ocenama.
def train_model(
    ratings_df: DataFrame,
    rank: int = 10,
    max_iter: int = 10,
    reg_param: float = 0.1
) -> ALSModel:

    als = create_als(
        rank=rank,
        max_iter=max_iter,
        reg_param=reg_param
    )

    return als.fit(ratings_df)

# Izračunava RMSE i broj uspešno evaluiranih predikcija
def evaluate_model(
    model: ALSModel,
    test_df: DataFrame
) -> tuple[float, int]:

    predictions = model.transform(test_df)

    evaluator = RegressionEvaluator(
        metricName="rmse",
        labelCol="rating",
        predictionCol="prediction"
    )

    rmse = evaluator.evaluate(predictions)

    return rmse, predictions.count()

# Trenira više modela i poredi RMSE rezultate
def test_rank_values(
    train_df: DataFrame,
    test_df: DataFrame,
    ranks: list[int],
    max_iter: int = 10,
    reg_param: float = 0.1
) -> list[dict]:

    results = []

    for rank in ranks:
        model = train_model(
            train_df,
            rank=rank,
            max_iter=max_iter,
            reg_param=reg_param
        )

        rmse, prediction_count = evaluate_model(
            model,
            test_df
        )

        results.append({
            "rank": rank,
            "rmse": rmse,
            "prediction_count": prediction_count
        })

    return results

# Generiše preporuke za jednog korisnika i uklanja
# filmove koje je korisnik već ocenio
def generate_user_recommendations(
    model: ALSModel,
    ratings_df: DataFrame,
    user_id: int,
    recommendation_count: int = 10,
    candidate_count: int = 50
) -> DataFrame:

    selected_user_df = (
        ratings_df
        .filter(
            col("userId") == int(user_id)
        )
        .select("userId")
        .distinct()
    )

    recommendation_candidates = (
        model
        .recommendForUserSubset(
            selected_user_df,
            candidate_count
        )
        .select(
            "userId",
            explode(
                col("recommendations")
            ).alias("recommendation")
        )
        .select(
            col("userId").alias("userId"),
            col("recommendation.movieId")
            .alias("movieId"),
            col("recommendation.rating")
            .alias("rawPrediction")
        )
    )

    rated_movies = (
        ratings_df
        .filter(
            col("userId") == int(user_id)
        )
        .select(
            "userId",
            "movieId"
        )
        .dropDuplicates()
    )

    unseen_recommendations = (
        recommendation_candidates
        .join(
            rated_movies,
            on=[
                "userId",
                "movieId"
            ],
            how="left_anti"
        )
    )

    recommendation_window = (
        Window
        .partitionBy("userId")
        .orderBy(
            desc("rawPrediction")
        )
    )

    return (
        unseen_recommendations
        .withColumn(
            "position",
            row_number().over(
                recommendation_window
            )
        )
        .filter(
            col("position") <= recommendation_count
        )
        .withColumn(
            "predictedRating",
            least(
                lit(5.0),
                greatest(
                    lit(1.0),
                    col("rawPrediction")
                )
            )
        )
        .select(
            "userId",
            "movieId",
            "position",
            "predictedRating",
            "rawPrediction"
        )
    )
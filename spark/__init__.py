from pyspark.sql import SparkSession

from spark.config import (
    DATABASE_NAME,
    MONGODB_CONNECTOR_PACKAGE,
    MONGODB_URI,
    SPARK_DRIVER_MEMORY,
)

# Kreira i vraca Spark sesiju povezanu sa MongoDB bazom
def create_spark_session(
    app_name: str = "Kupina Spark Pipeline"
) -> SparkSession:

    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config(
            "spark.driver.memory",
            SPARK_DRIVER_MEMORY
        )
        .config(
            "spark.jars.packages",
            MONGODB_CONNECTOR_PACKAGE
        )
        .config(
            "spark.mongodb.read.connection.uri",
            f"{MONGODB_URI}/{DATABASE_NAME}"
        )
        .config(
            "spark.mongodb.write.connection.uri",
            f"{MONGODB_URI}/{DATABASE_NAME}"
        )
        .getOrCreate()
    )

    return spark
from pyspark.sql import SparkSession
import os

from spark.config import (
    DATABASE_NAME,
    HADOOP_HOME,
    MONGODB_CONNECTOR_PACKAGE,
    MONGODB_URI,
    SPARK_DRIVER_MEMORY,
)


def create_spark_session(
    app_name: str = "Kupina Spark"
) -> SparkSession:
    """
    Kreira Spark sesiju povezanu sa MongoDB bazom.
    """

    os.environ["HADOOP_HOME"] = HADOOP_HOME
    os.environ["hadoop.home.dir"] = HADOOP_HOME

    hadoop_bin = os.path.join(
        HADOOP_HOME,
        "bin"
    )

    if hadoop_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = (
            hadoop_bin
            + os.pathsep
            + os.environ.get("PATH", "")
        )

    return (
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
        .config(
            "spark.hadoop.hadoop.home.dir",
            HADOOP_HOME
        )
        .getOrCreate()
    )
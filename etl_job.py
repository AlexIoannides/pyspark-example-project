"""
etl_job.py
~~~~~~~~~~

This Python module contains an Apache Spark ETL job definition. It can
be submitted to a Spark cluster (or locally) using the 'spark-submit'
command found in the '/bin' directory of all Spark distributions
(necessary for running any Spark job, locally or otherwise). For
example, this example script can be executed as follows,

    $SPARK_HOME/bin/spark-submit \
    --master spark://your_spark_cluster_ip:7077 \
    --py-files dependencies.zip \
    etl_job.py 21

For more details on submitting Spark applications, please see here:
http://spark.apache.org/docs/latest/submitting-applications.html

Our chosen approach for structuring jobs is to have the 'units' of ETL
defined as functions in the modules (i.e. the *.py file), which could
be reused in other scripts or called from within another environment
(e.g. a Jupyter or Zeppelin notebook), other than from the 'script' -
i.e. that defined under, >>> if __name__ == '__main__': , which Spark
will enter upon application submission.
"""

# imports from Python Standard Library
from sys import argv

# imports downloaded from PyPi
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import *

# local dependencies
from dependencies import logging


def extract_data(spark):
    """Create data locally and send data to Spark cluster.

    :param spark: Spark session object.
    :return: Spark DataFrame.
    """
    local_records = [
        Row(id=1, first_name='Dan', second_name='Germain', floor=1),
        Row(id=2, first_name='Dan', second_name='Sommerville', floor=1),
        Row(id=3, first_name='Alex', second_name='Ioannides', floor=2),
        Row(id=4, first_name='Ken', second_name='Lai', floor=2),
        Row(id=5, first_name='Stu', second_name='White', floor=3),
        Row(id=6, first_name='Mark', second_name='Sweeting', floor=3),
        Row(id=7, first_name='Phil', second_name='Bird', floor=4),
        Row(id=8, first_name='Kim', second_name='Suter', floor=4)
    ]

    df = spark.createDataFrame(local_records)
    return df


def transform_data(df, steps_per_floor_):
    """Transform original dataset.

    :param df: Input DataFrame.
    :param steps_per_floor_: The number of steps per-floor at 43 Tanner Street.
    :return: Transformed DataFrame.
    """
    df_transformed = df \
        .select(
            col('id'),
            concat_ws(' ', col('first_name'), col('second_name')).alias('name'),
            (col('floor') * lit(steps_per_floor_)).alias('steps_to_desk')
        )

    return df_transformed


def load_data_to_stdout(df):
    """Collect data locally and print to stdout.

    :param df: DataFrame to print.
    :return: None
    """
    df.show()
    return None


# entry point for PySpark application
if __name__ == '__main__':
    # get arguments supplied with script
    steps_per_floor = int(argv[1])

    # start application (ETL job) on Spark cluster and set session from cluster
    spark_conn = SparkSession\
        .builder \
        .appName('test_etl_job') \
        .getOrCreate()

    # get logger
    log = logging.Log4j(spark_conn)
    log.warn('test_etl_job is up-and-running')

    # ETL pipeline
    data = extract_data(spark_conn)
    data_transformed = transform_data(data, steps_per_floor)
    load_data_to_stdout(data_transformed)

    # finish
    log.warn('test_etl_job is finished')
    spark_conn.stop()

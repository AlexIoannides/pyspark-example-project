"""
test_etl_job.py
~~~~~~~~~~~~~~~

This module contains unit tests for the individual units of ETL
contained in etl_job.py. It makes use of a local version of PySpark
that is bundled with the PySpark package.
"""
import unittest

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

import etl_job


class SparkETLTests(unittest.TestCase):
    "Test suite for components in etl_job.py"

    def test_extract_data(self):
        """Test extract step
        """
        # start Spark locally and retrieve a session for this test app
        spark = SparkSession\
            .builder \
            .master('local[*]') \
            .appName('test_etl_job') \
            .getOrCreate()

        data = etl_job.extract_data(spark)
        num_rows = data.count()
        columns = data.columns

        self.assertEqual(type(data), DataFrame)
        self.assertEqual(num_rows, 8)
        self.assertTrue(
            [col in ['id', 'first_name', 'second_name', 'floor']
             for col in columns])

        spark.stop()


    def test_trandform_data(self):
        """Test transform step
        """
        # start Spark locally and retrieve a session for this test app
        spark = SparkSession\
            .builder \
            .master('local[*]') \
            .appName('test_etl_job') \
            .getOrCreate()

        data = etl_job.extract_data(spark)
        data_transformed = etl_job.transform_data(data, 21)
        num_rows = data_transformed.count()
        columns = data_transformed.columns

        self.assertEqual(type(data_transformed), DataFrame)
        self.assertEqual(num_rows, 8)
        self.assertTrue(
            [col in ['id', 'name', 'steps_to_desk'] for col in columns])

        spark.stop()


if __name__ == '__main__':

    # run unittests
    unittest.main()

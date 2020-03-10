# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

from src.configuration.configuration_manager import ConfigurationManager
from src.utils.logging_manager import LoggingManager


class Session(object):
    """
    Wrapper around Spark Session
    """

    _instance = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        config = ConfigurationManager()
        name = config.get_value('core', 'application')
        self.init_spark_session(name)

    def init_spark_session(self, application_name, spark_master=None):
        """Setup a spark session.

        :param spark_master: A master parameter used by spark session builder.
          Use default value (None) to use system
          environment configured spark cluster.
          Use 'local[*]' to run on a local box.

        :return: spark_session: A spark session
        """
        eva_spark_conf = SparkConf()
        eva_spark_conf.set('spark.logConf', 'true')

        session_builder = SparkSession \
            .builder \
            .appName(application_name) \
            .config(conf=eva_spark_conf)

        if spark_master:
            session_builder.master(spark_master)

        # Gets an existing SparkSession or,
        # if there is no existing one, creates a new one based
        # on the options set in this builder.
        self._session = session_builder.getOrCreate()

        # Configure logging
        log4j_level = LoggingManager().getLog4JLevel()
        spark_context = self._session.sparkContext
        spark_context.setLogLevel(log4j_level)

    def get_session(self):
        return self._session

    def get_context(self):
        return self._session.sparkContext

    def stop(self):
        self._session.stop()

    def __del__(self):
        self._session.stop()

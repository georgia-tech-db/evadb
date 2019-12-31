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


class Session:
    """
    Wrapper around Spark Session
    """

    def __init__(self, application_name, spark_master=None):
        """Setup a spark session.

        :param spark_master: A master parameter used by spark session builder.
          Use default value (None) to use system
          environment configured spark cluster.
          Use 'local[*]' to run on a local box.

        :return: spark_session: A spark session
        """
        print("Starting session")

        session_builder = SparkSession \
            .builder \
            .appName(application_name)

        if spark_master:
            session_builder.master(spark_master)

        # Gets an existing SparkSession or,
        # if there is no existing one, creates a new one based
        # on the options set in this builder.
        self._session = session_builder.getOrCreate()

    def get_session(self):
        print("Getting session")

        return self._session

    def __del__(self):
        # Stop spark session
        print("Stopping session")
        self._session.stop()

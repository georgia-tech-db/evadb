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

import logging

from enum import Enum


class LoggingLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class Logger(object):

    _instance = None
    _LOG = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)

            # LOGGING INITIALIZATION
            cls._LOG = logging.getLogger(__name__)
            LOG_handler = logging.StreamHandler()
            LOG_formatter = logging.Formatter(
                fmt='%(asctime)s [%(funcName)s:%(lineno)03d]'
                '%(levelname)-5s: %(message)s',
                datefmt='%m-%d-%Y %H:%M:%S'
            )
            LOG_handler.setFormatter(LOG_formatter)
            cls._LOG.addHandler(LOG_handler)

        return cls._instance

    def log(self, string, level: LoggingLevel = LoggingLevel.DEBUG):
        if level == LoggingLevel.DEBUG:
            self._LOG.debug(string)
        elif level == LoggingLevel.INFO:
            self._LOG.info(string)
        elif level == LoggingLevel.WARNING:
            self._LOG.warn(string)
        elif level == LoggingLevel.ERROR:
            self._LOG.error(string)
        elif level == LoggingLevel.CRITICAL:
            self._LOG.critical(string)

    def getEffectiveLevel(self):
        return logging.getLevelName(self._LOG.getEffectiveLevel())

    def getLog4JLevel(self):

        logger_level = self.getEffectiveLevel()

        # Reference:
        # https://logging.apache.org/log4j/1.2/apidocs/org/
        # apache/log4j/Level.html

        # for spark log level configuration
        if logger_level == 'DEBUG':
            return "DEBUG"
        elif logger_level == 'INFO':
            return "INFO"
        elif logger_level == 'WARNING':
            return "WARN"
        elif logger_level == 'ERROR':
            return "ERROR"
        elif logger_level == 'CRITICAL':
            return "FATAL"

    def exception(self, error):
        self._LOG.exception(error)

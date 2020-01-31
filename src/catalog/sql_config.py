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
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class SQLConfig(object):
    base = declarative_base()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SQLConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # blank password for travis ci
        self.engine = create_engine(
            'mysql+pymysql://root:@localhost/eva_catalog')
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = self.session_factory()
        self.base.metadata.create_all(self.engine)

    def get_session(self):
        if self.session is None:
            self.session = self.session_factory()
        return self.session


sql_conn = SQLConfig()

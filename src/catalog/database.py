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
from sqlalchemy.orm import sessionmaker, scoped_session
from src.configuration.dictionary import SQLALCHEMY_DATABASE_URI
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.exc import DatabaseError
from sqlalchemy_utils import database_exists, create_database, drop_database

engine = create_engine(SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                         bind=engine))


class CustomBase(object):
    """This overrides the default
    `_declarative_constructor` constructor.
    It skips the attributes that are not present
    for the model, thus if a dict is passed with some
    unknown attributes for the model on creation,
    it won't complain for `unkwnown field`s.
    """

    def __init__(self, **kwargs):
        cls_ = type(self)
        for k in kwargs:
            if hasattr(cls_, k):
                setattr(self, k, kwargs[k])
            else:
                continue

    """
    Set default tablename
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    """
    Add and try to flush.
    """

    def save(self):
        db_session.add(self)
        self._flush()
        return self

    """
    Update and try to flush.
    """

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
        return self.save()

    """
    Delete and try to flush.
    """

    def delete(self):
        db_session.delete(self)
        self._flush()

    """
    Try to flush. If an error is raised,
    the session is rollbacked.
    """

    def _flush(self):
        try:
            db_session.flush()
        except DatabaseError:
            db_session.rollback()


BaseModel = declarative_base(cls=CustomBase, constructor=None)
BaseModel.query = db_session.query_property()


def init_db():
    """
    Create database if doesn't exist and
    create all tables.
    """
    if not database_exists(engine.url):
        create_database(engine.url)
    BaseModel.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all of the record from tables and the tables
    themselves.
    Drop the database as well.
    """
    BaseModel.metadata.drop_all(bind=engine)
    drop_database(engine.url)

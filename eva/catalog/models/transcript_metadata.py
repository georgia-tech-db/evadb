# coding=utf-8
# Copyright 2018-2022 EVA
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
from ast import literal_eval
from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from eva.catalog.models.base_model import BaseModel


class TranscriptMetadata(BaseModel):
    __tablename__ = "transcript_metadata"

    # _id = Column("id", Integer, primary_key=True, autoincrement=True)
    # a table contains many videos, video_name helps distinguish which video transcript this word is for
    _table_id = Column('table_id', Integer, ForeignKey("df_metadata.id"))
    _video_name = Column("video_name", String(100))
    _word = Column("word", String(100))
    _start_time = Column("start_time", String(100))
    _end_time = Column("end_time", String(100))
    _confidence = Column("confidence", String(100))

    def __init__(
            self,
            # id: str,
            table_id: int,
            video_name: str,
            word: str,
            start_time: str,
            end_time: str,
            confidence: str
    ):
        # self._id = id
        self._table_id = table_id
        self._video_name = video_name
        self._word = word
        self._start_time = start_time
        self._end_time = end_time
        self._confidence = confidence

    @property
    def id(self):
        return self._id

    @property
    def table_id(self):
        return self._table_id

    @property
    def video_name(self):
        return self._video_name

    @property
    def word(self):
        return self._word

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def confidence(self):
        return self._confidence

    def __str__(self):
        column_str = "Column: (%s, %s, %s, %s, %s, %s)" % (
            self._video_name,
            self._table_id,
            self._word,
            self._start_time,
            self._end_time,
            self._confidence
        )

        return column_str

    def __eq__(self, other):
        return (
                self.id == other.id
                and self.table_id == other.table_id
                and self.video_name == other.video_name
                and self.word == other.word
                and self.start_time == other.start_time
                and self.end_time == other.end_time
                and self.confidence == other.confidence
        )

    def __hash__(self):
        return hash(
            (
                self.id,
                self.table_id,
                self.video_name,
                self.word,
                self.start_time,
                self.end_time,
                self.confidence
            )
        )

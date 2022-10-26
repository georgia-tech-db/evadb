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

from sqlalchemy.orm.exc import NoResultFound
from eva.catalog.models.transcript_metadata import TranscriptMetadata
from eva.catalog.services.base_service import BaseService
from eva.utils.logging_manager import logger


class TranscriptMetadataService(BaseService):
    def __init__(self):
        super().__init__(TranscriptMetadata)
    def create_transcript_metadata(self, video_name: str, word: str, start_time: str, end_time: str, confidence: str) -> TranscriptMetadata:
        """Creates a new transcript metadata entry
        """
        metadata = self.model(video_name, word, start_time, end_time, confidence)
        metadata = metadata.save()
        return metadata

    def transcript_metadata_by_word(self, word: str):
        """return the transcript entries that matches the word provided.
           None if no such entry found.
        """

        try:
            return self.model.query.filter(self.model._word == word)
        except NoResultFound:
            return None
    def get_all_transcript_metadata(self):
        try:
            return self.model.query.all()
        except NoResultFound:
            return []

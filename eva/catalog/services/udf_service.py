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

from eva.catalog.models.udf import UdfMetadata
from eva.catalog.services.base_service import BaseService
from eva.utils.logging_manager import logger


class UdfService(BaseService):
    def __init__(self):
        super().__init__(UdfMetadata)

    def create_udf(self, name: str, impl_path: str, type: str) -> UdfMetadata:
        """Creates a new udf entry

        Arguments:
            name (str): name of the udf
            impl_path (str): path to the udf implementation relative to eva/udf
            type (str): udf operator kind, classification or detection or etc

        Returns:
            UdfMetadata: Returns the new entry created
        """
        metadata = self.model(name, impl_path, type)
        metadata = metadata.save()
        return metadata

    def udf_by_name(self, name: str):
        """return the udf entry that matches the name provided.
           None if no such entry found.

        Arguments:
            name (str): name to be searched
        """

        try:
            return self.model.query.filter(self.model._name == name).one()
        except NoResultFound:
            return None

    def udf_by_id(self, id: int):
        """return the udf entry that matches the id provided.
           None if no such entry found.

        Arguments:
            id (int): id to be searched
        """

        try:
            return self.model.query.filter(self.model._id == id).one()
        except NoResultFound:
            return None

    def drop_udf_by_name(self, name: str):
        """Drop a udf entry from the catalog udfmetadata

        Arguments:
            name (str): udf name to be deleted

        Returns:
            True if successfully deleted else True
        """
        try:
            udf_record = self.udf_by_name(name)
            udf_record.delete()
        except Exception:
            logger.exception("Delete udf failed for name {}".format(name))
            return False
        return True

    def get_all_udfs(self):
        try:
            return self.model.query.all()
        except NoResultFound:
            return []

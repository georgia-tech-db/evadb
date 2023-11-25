# coding=utf-8
# Copyright 2018-2023 EvaDB
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

import requests
from pytube import extract
import pandas as pd
from evadb.third_party.types import DBHandler, DBHandlerResponse, DBHandlerStatus


class YoutubeHandler(DBHandler):
    SNIPPET_COLUMNS = [
        "publishedAt",
        "channelId",
        "title",
        "description",
        "thumbnails",
        "channelTitle",
        "tags",
        "categoryId",
    ]
    STATISTICS_COLUMNS = [
        "viewCount",
        "likeCount",
        "favoriteCount",
        "commentCount",
    ]
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        urls = kwargs.get("youtube_urls")
        if urls is not None:
            self.url_list = str(urls).strip().split(',')
        else:
            self.url_list = []
        query = kwargs.get("search_query")
        if query is not None:
            self.query = str(query)
        else:
            self.query = None
        maxResults = kwargs.get("max_results")
        if maxResults is not None:
            self.maxResults = int(maxResults)
        else:
            self.maxResults = None
        self.api_key = str(kwargs.get("youtube_token"))

    def connect(self):
        try:
            response = self._api_call(self.url_list[0], "snippet")
            if response.status_code == 200:
                return DBHandlerStatus(status=True)
            else:
                return DBHandlerStatus(status=False, error=response.json())
        except Exception as e:
            return DBHandlerStatus(status=False, error=str(e))

    def disconnect(self):
        pass

    def check_connection(self) -> DBHandlerStatus:
        try:
            response = self._api_call(self.url_list[0], "snippet")
            if response.status_code == 200:
                return DBHandlerStatus(status=True)
            else:
                return DBHandlerStatus(status=False, error=response.json())
        except Exception as e:
            return DBHandlerStatus(status=False, error=str(e))

    def get_tables(self) -> DBHandlerResponse:
        tables_df = pd.DataFrame(["snippet", "statistics"], columns=["table_name"])
        return DBHandlerResponse(data=tables_df)

    def get_columns(self, table_name: str) -> DBHandlerResponse:
        if table_name == "snippet":
            columns_df = pd.DataFrame(self.SNIPPET_COLUMNS, columns=["column_name"])
            return DBHandlerResponse(data=columns_df)
        elif table_name == "statistics":
            columns_df = pd.DataFrame(self.STATISTICS_COLUMNS, columns=["column_name"])
            return DBHandlerResponse(data=columns_df)
        else:
            return DBHandlerResponse(status=False, error="Invalid table name.")

    def _api_call(self, url: str, table_name: str) -> requests.models.Response:
        """Retrieves YouTube video information such as view count, title, etc.
        """

        video_id = extract.video_id(url)
        url = f'https://youtube.googleapis.com/youtube/v3/videos?part={table_name}&id={video_id}&key={self.api_key}'
        headers = {
          'Accept': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data={})

        return response

    def _search_api_call(self) -> requests.models.Response:
        """Retrieves YouTube video information such as view count, title, etc.
        """
        
        maxResults = "" if self.maxResults is None else f'&maxResults={self.maxResults}'
        url = f'https://youtube.googleapis.com/youtube/v3/search?part=snippet{maxResults}&q={self.query}&type=video&key={self.api_key}'
        headers = {
          'Accept': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data={})

        return response

    def _get_snippet_info(self) -> pd.DataFrame:
        df = pd.DataFrame(columns=self.SNIPPET_COLUMNS)
        for url_index in range(len(self.url_list)):
            url = self.url_list[url_index]
            response = self._api_call(url, "snippet").json()
            if response["pageInfo"]["totalResults"] == 0:
                df.loc[url_index] = {}
            else:
                snippet = response["items"][0]["snippet"]
                df.loc[url_index] = snippet
        if self.query is not None:
            response = self._search_api_call().json()
            results = len(response["items"])
            for result_index in range(results):
                snippet = response["items"][result_index]["snippet"]
                df.loc[len(df)] = snippet
        return df

    def _get_statistics_info(self) -> pd.DataFrame:
        df = pd.DataFrame(columns=self.STATISTICS_COLUMNS)
        for url_index in range(len(self.url_list)):
            url = self.url_list[url_index]
            response = self._api_call(url, "statistics").json()
            if response["pageInfo"]["totalResults"] == 0:
                df.loc[url_index] = {}
            else:
                statistics = response["items"][0]["statistics"]
                df.loc[url_index] = statistics
        if self.query != None:
            response = self._search_api_call().json()
            results = len(response["items"])
            for result_index in range(results):
                videoId = response["items"][result_index]["id"]["videoId"]
                url = f'https://www.youtube.com/watch?v={videoId}'
                stat_response = self._api_call(url, "statistics").json()
                statistics = stat_response["items"][0]["statistics"]
                df.loc[len(df)] = statistics
        return df


    def select(self, table_name: str) -> DBHandlerResponse:
        """
        Returns a generator that yields the data from the given table.
        Args:
            table_name (str): name of the table whose data is to be retrieved.
        Returns:
            DBHandlerResponse
        """

        if table_name == "snippet":
            snippet_df = self._get_snippet_info()
            return DBHandlerResponse(data=snippet_df)
        elif table_name == "statistics":
            statistics_df = self._get_statistics_info()
            return DBHandlerResponse(data=statistics_df)
        else:
            return DBHandlerResponse(data=None, error="Invalid table name.")

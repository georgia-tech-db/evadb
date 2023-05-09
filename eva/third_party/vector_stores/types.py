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
from dataclasses import dataclass
from typing import Any, List


@dataclass
class FeaturePayload:
    id: int
    embedding: List[float]


class VectorIndexQuery:
    embedding: List[float]
    top_k: int


class VectorIndexQueryResult:
    similarities: List[float]
    ids: List[int]


class VectorStore:
    def add(self, payload: List[FeaturePayload]) -> None:
        """Add embeddings to the vector store"""
        ...

    def persist(self, path: str) -> None:
        """Persist index to disk"""
        return None

    def query(self, query: VectorIndexQuery) -> VectorIndexQueryResult:
        """Query index"""
        ...

    def client(self) -> Any:
        ...

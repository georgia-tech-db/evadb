from dataclasses import dataclass
from typing import List


@dataclass
class FeaturePayload:
    id: int
    embedding: List[float]

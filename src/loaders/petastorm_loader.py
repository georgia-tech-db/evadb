from typing import Iterator

from petastorm import make_reader

from src.loaders.abstract_loader import AbstractVideoLoader
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.storage.frame import Frame


class PetastormLoader(AbstractVideoLoader):
    def __init__(self, *args, **kwargs):
        """
        Loads parquet data frames using petastorm
        """
        super().__init__(*args, **kwargs)

    def _load_frames(self) -> Iterator[Frame]:
        info = None
        with make_reader(self.video_metadata.file_url,
                         shard_count=self.total_shards,
                         cur_shard=self.shard) \
                as reader:
            for frame_ind, row in enumerate(reader):
                if info is None:
                    (height, width, num_channels) = row.frame_data.shape
                    info = FrameInfo(height, width, num_channels,
                                     ColorSpace.BGR)

                yield Frame(row.frame_id, row.frame_data, info)

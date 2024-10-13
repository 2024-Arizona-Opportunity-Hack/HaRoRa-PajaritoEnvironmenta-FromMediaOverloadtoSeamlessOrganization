import dataclasses
from typing import Optional, List


@dataclasses.dataclass
class ImageDetail:
    uuid: str  # sub = user_id = primary key?
    url: str  # primary key
    title: str
    caption: str  # scipdf gives authors in ';' separated string
    tags: str
    title_caption_tags_fts_vector: str
    embedding_vector: List[float]
    coordinates: List[float]
    capture_time: str
    extended_meta: dict
    season: str
    updated_at: str
    created_at: str

import dataclasses
from typing import Optional, List


@dataclasses.dataclass
class ImageDetail:
    url: str  # primary key
    title: str
    caption: str  # scipdf gives authors in ';' separated string
    tags: str
    title_caption_tags_fts_vector: str
    coordinates: List[float] | None
    capture_time: str | None
    extended_meta: dict | None
    season: str | None

class ImageDetailIn(ImageDetail):
    embedding_vector: List[float]

class ImageDetailResult(ImageDetail):
    uuid: str  # sub = user_id = primary key?
    updated_at: str
    created_at: str

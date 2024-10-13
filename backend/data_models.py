import dataclasses
from typing import Optional, List


@dataclasses.dataclass
class ImageDetail:
    url: str  # primary key
    thumbnail_url: str
    title: str
    caption: str  # scipdf gives authors in ';' separated string
    tags: str
    coordinates: List[float] | None
    capture_time: str | None  # dd/mm/yyyy
    extended_meta: str | None
    season: str | None

@dataclasses.dataclass
class ImageDetailIn(ImageDetail):
    embedding_vector: List[float]

@dataclasses.dataclass
class ImageDetailResult(ImageDetail):
    uuid: str  # sub = user_id = primary key?
    updated_at: str
    created_at: str

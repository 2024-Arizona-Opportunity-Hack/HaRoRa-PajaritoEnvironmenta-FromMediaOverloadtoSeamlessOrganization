import dataclasses
from typing import Optional, List


@dataclasses.dataclass
class ImageDetail:
    url: str  # primary key
    user_id: str  # primary key of the user that added this Imagein table
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


@dataclasses.dataclass
class User:
    user_id: str  # dropbox account
    user_name: str  # dropbox username
    email: str  # dropbox email
    access_token: str  # dropbox access token for the user for current app
    refresh_token: str  # dropbox refresh token once access token expires
    cursor: Optional[str] = None

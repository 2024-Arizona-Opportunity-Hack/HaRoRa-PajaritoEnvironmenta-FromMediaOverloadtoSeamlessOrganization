import os
import uuid
from typing import Optional, List

import psycopg2
from psycopg2 import sql

import data_models
from data_models import User, FileQueue, BatchQueue

# Connect to the database
PG_USER = os.environ["PG_USER"]
PG_PASSWORD = os.environ["PG_PASSWORD"]
PG_HOST = os.environ["PG_HOST"]
PG_PORT = os.environ["PG_PORT"]
PG_DB = os.environ["PG_DB"]


def with_connection(func):
    """
    Function decorator for passing connections
    """

    def connection(*args, **kwargs):
        # Here, you may even use a connection pool
        conn = psycopg2.connect(dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT)
        try:
            rv = func(conn, *args, **kwargs)
        except Exception as e:
            conn.rollback()
            raise e
        else:
            # Can decide to see if you need to commit the transaction or not
            conn.commit()
        finally:
            conn.close()
        return rv

    return connection


@with_connection
def create_tables(conn):
    cur = conn.cursor()
    with open("./database/DDL.sql", "r") as f:
        cur.execute(f.read())
    cur.close()


@with_connection
def get_search_query_result(
    conn,
    query_text: str,
    query_embedding: list[float],
    user_id: str,
    season: Optional[str] = None,
    tags: Optional[list[str]] = None,
    coordinates: Optional[list[float]] = None,
    distance_radius: Optional[float] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    match_count: Optional[int] = 50,
    full_text_weight: Optional[float] = 1,
    semantic_weight: Optional[float] = 1,
    rrf_k: Optional[int] = 50,
) -> Optional[List[data_models.ImageDetailResult]]:
    # Build the main SQL query
    search_query = f"""
    WITH fts_ranked_title_caption_tags AS (
        SELECT
            uuid,
            row_number() OVER (
                ORDER BY ts_rank_cd(title_caption_tags_fts_vector, websearch_to_tsquery(%(query_text)s)) DESC
            ) AS rank_ix
        FROM image_detail
        WHERE title_caption_tags_fts_vector @@ websearch_to_tsquery(%(query_text)s)
        AND user_id = %(user_id)s
        AND COALESCE(season = COALESCE(%(season)s, season), TRUE)
        AND COALESCE((%(longitude)s IS NULL OR %(latitude)s IS NULL OR ST_DWithin(
            coordinates,
            ST_MakePoint(%(longitude)s, %(latitude)s)::geography,
            %(distance_radius)s
        )), TRUE)
        AND COALESCE(capture_time >= COALESCE(%(date_from)s, capture_time), TRUE)
        AND COALESCE(capture_time <= COALESCE(%(date_to)s, capture_time), TRUE)
        ORDER BY rank_ix
        LIMIT LEAST(%(match_count)s, 30) * 2
    ),
    semantic AS (
        SELECT
            uuid,
            row_number() OVER (
                ORDER BY image_detail.embedding_vector <#> %(query_embedding)s::vector
            ) AS rank_ix
        FROM image_detail
        WHERE user_id = %(user_id)s
        AND COALESCE(season = COALESCE(%(season)s, season), TRUE)
        AND COALESCE((%(longitude)s IS NULL OR %(latitude)s IS NULL OR ST_DWithin(
            coordinates,
            ST_MakePoint(%(longitude)s, %(latitude)s)::geography,
            %(distance_radius)s
        )), TRUE)
        AND COALESCE(capture_time >= COALESCE(%(date_from)s, capture_time), TRUE)
        AND COALESCE(capture_time <= COALESCE(%(date_to)s, capture_time), TRUE)
        ORDER BY rank_ix
        LIMIT LEAST(%(match_count)s, 30) * 2
    )
    SELECT
        image_detail.url,
        image_detail.user_id,
        image_detail.thumbnail_url,
        image_detail.title,
        image_detail.caption,
        image_detail.tags,
        image_detail.coordinates,
        image_detail.capture_time,
        image_detail.extended_meta,
        image_detail.season,
        image_detail.uuid,
        image_detail.updated_at,
        image_detail.created_at
    FROM fts_ranked_title_caption_tags
        FULL OUTER JOIN semantic ON fts_ranked_title_caption_tags.uuid = semantic.uuid
        JOIN image_detail ON COALESCE(fts_ranked_title_caption_tags.uuid, semantic.uuid) = image_detail.uuid
    ORDER BY
        COALESCE(1.0 / (%(rrf_k)s + fts_ranked_title_caption_tags.rank_ix), 0.0) * %(full_text_weight)s +
        COALESCE(1.0 / (%(rrf_k)s + semantic.rank_ix), 0.0) * %(semantic_weight)s DESC
    LIMIT LEAST(%(match_count)s, 30);
    """

    # Define the parameters for the query
    params = {
        "query_text": query_text,
        "query_embedding": query_embedding,
        "user_id": user_id,
        "season": season,
        "tags": ",".join(tags) if tags else None,
        "longitude": coordinates[0] if coordinates else None,
        "latitude": coordinates[1] if coordinates else None,
        "distance_radius": distance_radius,
        "date_from": date_from,
        "date_to": date_to,
        "match_count": match_count,
        "full_text_weight": full_text_weight,
        "semantic_weight": semantic_weight,
        "rrf_k": rrf_k,
    }
    filled_query = search_query % params
    print("Executing query:", filled_query)

    # Execute the query
    with conn.cursor() as cur:
        cur.execute(sql.SQL(search_query), params)
        result = cur.fetchall()
        return [data_models.ImageDetailResult(*x) for x in result] if result else None


@with_connection
def insert(
    conn,
    url: str,
    thumbnail_url: str,
    title: str,
    caption: str,
    tags: str,
    embedded_vector: list[float],
    user_id: str,
    coordinates: Optional[list[float]] = None,
    capture_time: Optional[str] = None,
    extended_meta: Optional[str] = None,
    season: Optional[str] = None,
):
    entry = (
        str(uuid.uuid4()),
        url,
        thumbnail_url,
        title,
        caption,
        tags,
        embedded_vector,
        user_id,
        f"POINT({coordinates[0]} {coordinates[1]})" if coordinates is not None else None,
        capture_time,
        extended_meta,
        season,
    )
    insert_query = """
               INSERT INTO image_detail (
                   uuid, url, thumbnail_url, title, caption, tags, embedding_vector, user_id, coordinates, capture_time, extended_meta, season
               ) VALUES (%s, %s, %s, %s, %s, %s, %s::float8[], %s, ST_GeomFromText(%s), to_timestamp(%s, 'DD/MM/YYYY'), %s::json, %s)
           """
    with conn.cursor() as cur:
        cur.execute(insert_query, entry)


@with_connection
def update_tags(conn, uuid: str, tags: str):
    update_query = """
    UPDATE image_detail SET tags = %s WHERE uuid = %s"""

    with conn.cursor() as cur:
        cur.execute(update_query, (tags, uuid))


@with_connection
def check_image_exists(conn, url: str, user_id: str) -> bool:
    check_query = """
    SELECT EXISTS (
        SELECT 1 FROM image_detail WHERE url = %s AND user_id = %s
    )
    """
    params = (url, user_id)
    with conn.cursor() as cur:
        cur.execute(check_query, params)
        res = cur.fetchone()
        print(res)
        return res[0]


# ===
# User
# ===


@with_connection
def create_user(conn, user: User) -> None:
    insert_query = """
    INSERT INTO users (
      user_id, user_name, email, access_token, refresh_token, template_id, cursor
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        user.user_id,
        user.user_name,
        user.email,
        user.access_token,
        user.refresh_token,
        user.template_id,
        user.cursor,
    )
    filled_query = insert_query % params
    print("Executing query:", filled_query)

    with conn.cursor() as cur:
        cur.execute(insert_query, params)


@with_connection
def read_user(conn, user_id: str) -> Optional[User]:
    select_query = """
  SELECT user_id, user_name, email, access_token, refresh_token, template_id, cursor
  FROM users
  WHERE user_id = %s
  """
    with conn.cursor() as cur:
        cur.execute(select_query, (user_id,))
        result = cur.fetchone()
        return User(*result) if result else None


@with_connection
def update_user(conn, user_id: str, user: User):
    update_query = """
  UPDATE users SET
      user_name = %s, email = %s, access_token = %s,
      refresh_token = %s, template_id = %s, cursor = %s
  WHERE user_id = %s
  """
    with conn.cursor() as cur:
        cur.execute(
            update_query,
            (user.user_name, user.email, user.access_token, user.refresh_token, user.template_id, user.cursor, user_id),
        )


@with_connection
def delete_user(conn, user_id: str):
    delete_query = """
  DELETE FROM users WHERE user_id = %s
  """
    with conn.cursor() as cur:
        cur.execute(delete_query, (user_id,))


@with_connection
def get_all_users(conn) -> List[User]:
    select_query = """
    SELECT user_id, user_name, email, access_token, refresh_token, template_id, cursor
    FROM users
    """
    with conn.cursor() as cur:
        cur.execute(select_query)
        results = cur.fetchall()
        return [User(*result) for result in results] if results else []


# ===
# FileQueue
# ===
@with_connection
def create_file_queue(conn, file_queue: FileQueue):
    insert_query = """
    INSERT INTO FileQueue (
        tmp_file_loc, tag_list, access_token, user_id, batch_id,
        is_saved_to_db, is_cleaned_from_disk
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        cur.execute(
            insert_query,
            (
                file_queue.tmp_file_loc,
                file_queue.tag_list,
                file_queue.access_token,
                file_queue.user_id,
                file_queue.batch_id,
                file_queue.is_saved_to_db,
                file_queue.is_cleaned_from_disk,
            ),
        )


@with_connection
def read_file_queue(conn, tmp_file_loc: str) -> Optional[FileQueue]:
    select_query = """
    SELECT tmp_file_loc, tag_list, access_token, user_id, batch_id,
           is_saved_to_db, is_cleaned_from_disk
    FROM FileQueue
    WHERE tmp_file_loc = %s
    """
    with conn.cursor() as cur:
        cur.execute(select_query, (tmp_file_loc,))
        result = cur.fetchone()
        return FileQueue(*result) if result else None


@with_connection
def update_file_queue(conn, tmp_file_loc: str, file_queue: FileQueue):
    update_query = """
    UPDATE FileQueue SET
        tag_list = %s, access_token = %s, user_id = %s, batch_id = %s,
        is_saved_to_db = %s, is_cleaned_from_disk = %s
    WHERE tmp_file_loc = %s
    """
    with conn.cursor() as cur:
        cur.execute(
            update_query,
            (
                file_queue.tag_list,
                file_queue.access_token,
                file_queue.user_id,
                file_queue.batch_id,
                file_queue.is_saved_to_db,
                file_queue.is_cleaned_from_disk,
                tmp_file_loc,
            ),
        )


@with_connection
def delete_file_queue(conn, tmp_file_loc: str):
    delete_query = """
    DELETE FROM FileQueue WHERE tmp_file_loc = %s
    """
    with conn.cursor() as cur:
        cur.execute(delete_query, (tmp_file_loc,))


@with_connection
def get_unbatched_files(conn) -> list[FileQueue] | None:
    """get list of files who have batch_id as null and is not saved to db"""
    select_query = """
    SELECT tmp_file_loc, tag_list, access_token, user_id, batch_id,
           is_saved_to_db, is_cleaned_from_disk, created_at, updated_at
    FROM FileQueue
    WHERE batch_id IS NULL AND is_saved_to_db = FALSE
    ORDER BY created_at
    LIMIT 50;
    """
    with conn.cursor() as cur:
        cur.execute(select_query)
        results = cur.fetchall()
        return [FileQueue(*result) for result in results] if results else None


@with_connection
def get_uncleaned_files(conn) -> list[FileQueue] | None:
    """
    Get list of files that are not cleaned from disk
    """
    select_query = """
    SELECT tmp_file_loc, tag_list, access_token, user_id, batch_id,
           is_saved_to_db, is_cleaned_from_disk, created_at, updated_at
    FROM FileQueue
    WHERE is_cleaned_from_disk = FALSE AND is_saved_to_db = TRUE
    ORDER BY created_at;
    """
    with conn.cursor() as cur:
        cur.execute(select_query)
        results = cur.fetchall()
        return [FileQueue(*result) for result in results] if results else None


@with_connection
def mark_file_as_saved(conn, tmp_file_loc: str):
    update_query = """
    UPDATE FileQueue SET is_saved_to_db = TRUE WHERE tmp_file_loc = %s
    """
    with conn.cursor() as cur:
        cur.execute(update_query, (tmp_file_loc,))


@with_connection
def get_files_by_batch_id(conn, batch_id: str) -> Optional[List[FileQueue]]:
    select_query = """
    SELECT tmp_file_loc, tag_list, access_token, user_id, batch_id,
           is_saved_to_db, is_cleaned_from_disk, created_at, updated_at
    FROM FileQueue
    WHERE batch_id = %s
    """
    with conn.cursor() as cur:
        cur.execute(select_query, (batch_id,))
        results = cur.fetchall()
        return [FileQueue(*result) for result in results] if results else None


@with_connection
def is_file_saved_to_db(conn, tmp_file_loc: str) -> bool:
    select_query = """
    SELECT is_saved_to_db FROM FileQueue WHERE tmp_file_loc = %s
    """
    with conn.cursor() as cur:
        cur.execute(select_query, (tmp_file_loc,))
        result = cur.fetchone()
        return result[0] if result else False


# ===
# BatchQueue
# ===
@with_connection
def create_batch_queue(conn, batch_queue: BatchQueue):
    insert_query = """
    INSERT INTO BatchQueue (
        batch_id, input_file_id, batch_jsonl_filepath, batch_metadata_filepath, status,
        output_file_id, are_all_files_updated_in_db,
        are_files_deleted_from_oai_storage, is_cleaned_from_disk
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        cur.execute(
            insert_query,
            (
                batch_queue.batch_id,
                batch_queue.input_file_id,
                batch_queue.batch_jsonl_filepath,
                batch_queue.batch_metadata_filepath,
                batch_queue.status,
                batch_queue.output_file_id,
                batch_queue.are_all_files_updated_in_db,
                batch_queue.are_files_deleted_from_oai_storage,
                batch_queue.is_cleaned_from_disk,
            ),
        )


@with_connection
def read_batch_queue(conn, batch_id: str) -> Optional[BatchQueue]:
    select_query = """
    SELECT batch_id, input_file_id, batch_jsonl_filepath, batch_metadata_filepath, status,
           output_file_id, are_all_files_updated_in_db, are_files_deleted_from_oai_storage,
           is_cleaned_from_disk
    FROM BatchQueue
    WHERE batch_id = %s
    """
    with conn.cursor() as cur:
        cur.execute(select_query, (batch_id,))
        result = cur.fetchone()
        return BatchQueue(*result) if result else None


@with_connection
def update_batch_queue(conn, batch_id: str, batch_queue: BatchQueue):
    update_query = """
    UPDATE BatchQueue SET
        input_file_id = %s, batch_jsonl_filepath = %s, batch_metadata_filepath = %s,
        status = %s, output_file_id = %s, are_all_files_updated_in_db = %s,
        are_files_deleted_from_oai_storage = %s, is_cleaned_from_disk = %s
    WHERE batch_id = %s
    """
    with conn.cursor() as cur:
        cur.execute(
            update_query,
            (
                batch_queue.input_file_id,
                batch_queue.batch_jsonl_filepath,
                batch_queue.batch_metadata_filepath,
                batch_queue.status,
                batch_queue.output_file_id,
                batch_queue.are_all_files_updated_in_db,
                batch_queue.are_files_deleted_from_oai_storage,
                batch_queue.is_cleaned_from_disk,
                batch_id,
            ),
        )


@with_connection
def delete_batch_queue(conn, batch_id: str):
    delete_query = """
    DELETE FROM BatchQueue WHERE batch_id = %s
    """
    with conn.cursor() as cur:
        cur.execute(delete_query, (batch_id,))


@with_connection
def get_running_batch_jobs(conn) -> list[BatchQueue] | None:
    """get list of running batch jobs (status != 'completed')"""
    select_query = """
    SELECT batch_id, input_file_id, batch_jsonl_filepath, batch_metadata_filepath, status,
           output_file_id, are_all_files_updated_in_db, are_files_deleted_from_oai_storage,
           is_cleaned_from_disk, created_at, updated_at
    FROM BatchQueue
    WHERE status != 'completed'
    ORDER BY created_at;
    """
    with conn.cursor() as cur:
        cur.execute(select_query)
        results = cur.fetchall()
        return [BatchQueue(*result) for result in results] if results else None


@with_connection
def get_completed_jobs_but_not_cleaned(conn) -> list[BatchQueue] | None:
    select_query = """
    SELECT batch_id, input_file_id, batch_jsonl_filepath, batch_metadata_filepath, status,
           output_file_id, are_all_files_updated_in_db, are_files_deleted_from_oai_storage,
           is_cleaned_from_disk, created_at, updated_at
    FROM BatchQueue
    WHERE status = 'completed' AND (is_cleaned_from_disk = FALSE OR are_files_deleted_from_oai_storage = FALSE)
    ORDER BY created_at;
    """
    with conn.cursor() as cur:
        cur.execute(select_query)
        results = cur.fetchall()
        return [BatchQueue(*result) for result in results] if results else None


if __name__ == "__main__":
    create_tables()

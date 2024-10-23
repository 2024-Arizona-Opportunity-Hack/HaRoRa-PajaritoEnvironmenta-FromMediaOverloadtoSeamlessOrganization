import os
import uuid
from typing import Optional, List

import psycopg2
from psycopg2 import sql

import data_models

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
        conn = psycopg2.connect(
            dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        )
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
def get_search_query_result(conn,
                            query_text: str,
                            query_embedding: list[float],
                            season: Optional[str] = None,
                            tags: Optional[list[str]] = None,
                            coordinates: Optional[list[float]] = None,
                            distance_radius: Optional[float] = None,
                            date_from: Optional[str] = None,
                            date_to: Optional[str] = None,
                            match_count: Optional[int] = 50,
                            full_text_weight: Optional[float] = 1,
                            semantic_weight: Optional[float] = 1,
                            rrf_k: Optional[int] = 50) -> Optional[
    List[data_models.ImageDetailResult]]:
    def get_where_clause_part(season: Optional[str],
                              tags: Optional[list[str]], coordinates: Optional[list[float]],
                              distance_radius: Optional[float], date_from: Optional[str],
                              date_to: Optional[str]) -> str:
        where_clause_sql = " WHERE"
        if season is not None:
            where_clause_sql += " season ='{}'".format(season)
        if tags is not None:
            if where_clause_sql != " WHERE":
                where_clause_sql += " AND"
            where_clause_sql += " EXISTS (SELECT 1 FROM unnest(STRING_TO_ARRAY(tags, ',')) AS tag WHERE tag = ANY (STRING_TO_ARRAY('{}', ',')))".format(tags)
        if coordinates is not None:
            if where_clause_sql != " WHERE":
                where_clause_sql += " AND"
            where_clause_sql += " ST_DWithin(coordinates, ST_MakePoint({}, {})::geography, {})".format(coordinates[0],
                                                                                                       coordinates[1],
                                                                                                       distance_radius)
        if date_from is not None:
            if where_clause_sql != " WHERE":
                where_clause_sql += " AND"
            where_clause_sql += " capture_time >= '{}'".format(date_from)
        if date_to is not None:
            if where_clause_sql != " WHERE":
                where_clause_sql += " AND"
            where_clause_sql += " capture_time <= '{}'".format(date_to)

        #return "" if where_clause_sql == " WHERE" else where_clause_sql
        return ''

    search_query_with_part = f"""
    with fts_ranked_title_caption_tags as (
            select
            uuid,
            -- Note: ts_rank_cd is not indexable but will only rank matches of the where clause
            -- which shouldn't be too big
            row_number() over(order by ts_rank_cd(title_caption_tags_fts_vector, websearch_to_tsquery('{query_text}')) desc) as rank_ix
    from
        image_detail
    where
        title_caption_tags_fts_vector @@ websearch_to_tsquery('{query_text}')
    order by rank_ix
    limit least({match_count}, 30) * 2
    ),
    semantic as (
        select
            uuid,
            row_number() over(order by image_detail.embedding_vector <#> ARRAY{query_embedding}::vector) as rank_ix
    from
        image_detail
    order by rank_ix
    limit least({match_count}, 30) *2
    )"""


    search_query_select_part = """
    select
        image_detail.url,
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
    from
        fts_ranked_title_caption_tags
            full outer join semantic
                            on fts_ranked_title_caption_tags.uuid = semantic.uuid
            join image_detail
                 on coalesce(fts_ranked_title_caption_tags.uuid, semantic.uuid) = image_detail.uuid"""

    search_query_where_part = get_where_clause_part(season, tags, coordinates, distance_radius, date_from, date_to)

    search_query_order_by_limit_part = """
    order by
        coalesce(1.0 / ({} + fts_ranked_title_caption_tags.rank_ix), 0.0) * {} +
        coalesce(1.0 / ({} + semantic.rank_ix), 0.0) * {}
            desc
    limit
        least({}, 30);""".format(rrf_k, full_text_weight, rrf_k, semantic_weight, match_count)

    search_query = (search_query_with_part + search_query_select_part + search_query_where_part +
                    search_query_order_by_limit_part)
    print(search_query)

    with conn.cursor() as cur:
        cur.execute(sql.SQL(search_query))
        result = cur.fetchall()
        # print(result)
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
        season
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

if __name__ == '__main__':
    create_tables()

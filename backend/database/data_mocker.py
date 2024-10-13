import uuid
import random
import json
from datetime import datetime, timedelta
import psycopg2
from lorem import sentence

# Database connection parameters
DB_NAME = "peec_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5555"


def generate_random_vector(dimensions=768):
    return [random.random() for _ in range(dimensions)]


def generate_random_entry():
    entry = (
        str(uuid.uuid4()),  # Random UUID
        f"https://example.com/image{random.randint(1, 1000)}.jpg",  # Random image URL
        sentence(),  # Random title as a sentence
        sentence(),  # Random description as a sentence
        ', '.join(random.sample(['city', 'skyline', 'night', 'day', 'sunset', 'landscape'], 3)),  # Random tags
        generate_random_vector(),  # Random vector of 2048 dimensions
        f"POINT({random.uniform(-180.0, 180.0)} {random.uniform(-90.0, 90.0)})",  # Random geographic point
        (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S'),
        # Random timestamp within the last year
        json.dumps({"camera": random.choice(["Canon EOS R5", "Nikon D850", "Sony A7 III"]),
                    "location": random.choice(["New York", "Los Angeles", "Chicago"])}),  # Random JSON metadata
        (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S'),
        # Another random timestamp within the last year
        (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S')
    # Another random timestamp within the last year
    )
    return entry


def insert_entries_to_db(entries):
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO image_detail (
                uuid, url, title, caption, tags, embedding_vector, coordinates, capture_time, extended_meta, updated_at, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s::float8[], ST_GeomFromText(%s), %s, %s::json, %s, %s)
        """

        for entry in entries:
            cursor.execute(insert_query, entry)

        connection.commit()

    except Exception as error:
        print(f"Error inserting data: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()


def generate_and_insert_entries(n=1000):
    entries = [generate_random_entry() for _ in range(n)]
    insert_entries_to_db(entries)


# Generate and insert entries into the database
generate_and_insert_entries()

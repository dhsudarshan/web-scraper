import os
from typing import Optional
import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://tracker:trackerpass@db:5432/pricedb"
)


def init_db():
  base_url, db_name = DATABASE_URL.rsplit("/", 1)
  default_url = f"{base_url}/postgres"
  try:
    conn = psycopg2.connect(default_url)
    conn.autocommit = (
        True  
    )
    with conn.cursor() as cursor:
      cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
      exists = cursor.fetchone()
      if not exists:
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created successfully.")
    conn.close()
  except Exception as e:
    print(f"Error checking/creating database: {e}")

  conn = psycopg2.connect(DATABASE_URL)
  try:
    with conn.cursor() as cursor:
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    item_id VARCHAR(50) PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL
                );
            """)
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id SERIAL PRIMARY KEY,
                    item_id VARCHAR(50) REFERENCES products(item_id),
                    price INT NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
    conn.commit()
    print("Database tables initialized successfully.")
  except Exception as e:
    conn.rollback()
    print(f"Error creating tables: {e}")
  finally:
    conn.close()


def get_connection():
  return psycopg2.connect(DATABASE_URL)


def insert_data(item_id: str, title: str, url: str, price: int):
  init_db()

  conn = get_connection()
  try:
    with conn.cursor() as cursor:
      cursor.execute(
          """INSERT INTO products(item_id, title, url)
                VALUES(%s, %s, %s)
                ON CONFLICT (item_id)
                DO UPDATE SET title = EXCLUDED.title, url = EXCLUDED.url""",
          (item_id, title, url),
      )
      cursor.execute(
          """INSERT INTO price_history(item_id, price)
                VALUES(%s, %s)""",
          (item_id, price),
      )
      conn.commit()
  except Exception as e:
    conn.rollback()
    print(f"Database error: {e}")
  finally:
    conn.close()
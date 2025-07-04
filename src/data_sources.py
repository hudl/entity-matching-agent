import os
import csv
from typing import List
import psycopg2

# DB Credentials
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT", "5432")

# Validate that all required variables are set
if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
    raise ValueError("One or more required environment variables are not set.")


# --- Function to Fetch IDs from PostgreSQL ---
def fetch_ids_from_postgres(limit) -> List[str]:
    """Connects to PostgreSQL and fetches the first N GSL IDs from the team table."""
    conn = None
    try:
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        query = "SELECT id FROM team ORDER BY RANDOM() LIMIT %s;"

        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = [item[0] for item in cur.fetchall()]
            print(f"Successfully fetched {len(rows)} IDs from the database.")
            return rows

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


# --- Function to Fetch IDs from CSV ---
def fetch_ids_from_csv(file_path: str, limit: int = None) -> List[str]:
    """Reads GSL IDs from a CSV file with a single column named 'source_gsl_id'."""
    ids = []
    try:
        print(f"Reading IDs from CSV file: {file_path}")

        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return []

        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Check if the required column exists
            if "source_gsl_id" not in reader.fieldnames:
                print(
                    f"Error: Column 'source_gsl_id' not found in CSV. Available columns: {reader.fieldnames}"
                )
                return []

            for row in reader:
                gsl_id = row["source_gsl_id"].strip()  # Remove whitespace
                if gsl_id:  # Only add non-empty IDs
                    ids.append(gsl_id)

                    # Apply limit if specified
                    if limit and len(ids) >= limit:
                        break

        print(f"Successfully read {len(ids)} IDs from CSV file.")
        return ids

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except csv.Error as e:
        print(f"CSV error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error reading CSV: {e}")
        return []

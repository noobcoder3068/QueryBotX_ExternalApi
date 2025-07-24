import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def execute_sql(sql: str):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        return [f"❌ Error: {str(e)}"]
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_query = "SELECT NOW();"
    result = execute_sql(test_query)
    print("✅ DB Response:", result)

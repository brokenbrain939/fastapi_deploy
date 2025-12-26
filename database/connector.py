import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class Connector:
    def __init__(
        self, 
        host='localhost', 
        port=5432, 
        username='postgres', 
        database='postgres', 
        password=None
    ):
        self.db_config = {
            "host": host, 
            "port": port, 
            "user": username, 
            "database": database, 
            "password": password
        }

    @contextmanager
    def cursor(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            yield cursor 
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
                print(f"Error occured while making the cursor: {e}")
            else:
                print(f"Error occured while making the connection: {e}")
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query, params=None):
        print("neife")
        try:
            with self.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"Exception occurred in query: {e}")
            raise e

    #insert return nothing
    def insert_query(self, query, params=None):
        try:
            with self.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()["id"]
        except Exception as e:
            print(f"Exception occurred in insert query: {e}")
            raise e

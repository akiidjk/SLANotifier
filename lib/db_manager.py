import sqlite3
from typing import Any

from lib.logger import logging
from lib.utils import deserialize, serialize


class DBManager:
    def __init__(self):
        self.name_db = "db.sqlite3"
        if self.init():
            logging.info("Database initialization successful")

    def init(self) -> bool:
        try:
            with sqlite3.connect(self.name_db) as conn:
                cursor = conn.cursor()
                query = '''
                    CREATE TABLE IF NOT EXISTS table_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name_team VARCHAR(255),
                        score_team INTEGER,
                        name_service VARCHAR(255),
                        score_service INTEGER,
                        flags_submitted INTEGER,
                        flags_lost INTEGER,
                        sla_value FLOAT,
                        is_down BOOLEAN,
                        timestamp TIMESTAMPTZ NOT NULL
                    )
                '''
                cursor.execute(query)
                conn.commit()
                return True
        except sqlite3.OperationalError:
            return False

    @staticmethod
    def check_result(results):
        if len(results) == 0:
            return False
        return True

    @staticmethod
    def format_columns(columns: tuple) -> str:
        if "timestamp" in columns:
            logging.warning("The timestamp column is already specified")
            return ', '.join(columns)

        return ', '.join(columns) + ", timestamp"

    def insert_records(self, records: list) -> None:
        records = serialize(records)
        with sqlite3.connect(self.name_db) as conn:
            c = conn.cursor()
            query = '''
                INSERT INTO table_records (name_team, score_team, name_service, score_service, flags_submitted, flags_lost, sla_value, is_down, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            c.executemany(query, records)
            conn.commit()

    def remove_db(self) -> None:
        with sqlite3.connect(self.name_db) as conn:
            c = conn.cursor()
            c.execute('''DROP TABLE table_records ''')

    def fetch_by_team(self, team: str, columns: tuple) -> list[dict[str, Any]]:
        try:
            with sqlite3.connect(self.name_db) as conn:
                c = conn.cursor()
                logging.debug(columns)
                columns_str = self.format_columns(columns)
                logging.debug(columns_str)
                query = f'''
                    SELECT {columns_str}
                    FROM table_records
                    WHERE name_team = ?
                    ORDER BY timestamp
                '''
                logging.debug(query)
                c.execute(query, (team,))
                results = deserialize(columns, c.fetchall())
        except sqlite3.OperationalError as error:
            logging.error(f"Error with fetching records {error}")
            exit(1)

        if self.check_result(results):
            return results
        else:
            logging.error("Error with fetching records or db is empty")

    def fetch_by_service(self, service: str, columns: tuple) -> list[dict[str, Any]]:
        try:
            with sqlite3.connect(self.name_db) as conn:
                c = conn.cursor()
                columns_str = self.format_columns(columns)
                query = f'''
                    SELECT {columns_str}
                    FROM table_records
                    WHERE name_service = ?
                    ORDER BY timestamp
                '''
                c.execute(query, (service,))
                results = deserialize(columns, c.fetchall())
        except sqlite3.OperationalError as error:
            logging.error(f"Error with fetching records {error}")
            exit(1)

        if self.check_result(results):
            return results
        else:
            logging.error("Error with fetching records or db is empty")

    def fetch_by_team_service(self, team: str, service: str, columns: tuple) -> list[dict[str, Any]]:
        try:
            with sqlite3.connect(self.name_db) as conn:
                c = conn.cursor()
                columns_str = self.format_columns(columns)
                query = f'''
                            SELECT {columns_str}
                            FROM table_records
                            WHERE name_service = ? AND name_team = ?
                            ORDER BY timestamp
                        '''
                c.execute(query, (service, team,))
                results = deserialize(columns, c.fetchall())
        except sqlite3.OperationalError as error:
            logging.error(f"Error with fetching records {error}")
            exit(1)

        if self.check_result(results):
            return results
        else:
            logging.error("Error with fetching records or db is empty")

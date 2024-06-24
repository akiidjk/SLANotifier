import sqlite3

from lib.logger import logging


class DBManager:
    def __init__(self):
        self.name_db = "db.sqlite3"
        if self.init():
            logging.info("Database initialization successful")
        pass

    def init(self) -> bool:
        try:
            with sqlite3.connect(self.name_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS table_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name_team VARCHAR(255),
                        score_team INTEGER,
                        name_service VARCHAR(255),
                        score_service INTEGER,
                        flag_submitted INTEGER,
                        flags_lost INTEGER,
                        sla_value VARCHAR(255),
                        is_down BOOLEAN,
                        timestamp TIMESTAMPTZ NOT NULL
                    )
                ''')
                conn.commit()
                return True
        except sqlite3.OperationalError:
            return False

    def format_record(self, records):
        formatted_records = []
        for record in records:
            for service in record['stats_service']:
                formatted_record = (
                    record['name_team'],
                    record['score_team'],
                    service['name_service'],
                    service['score_service'],
                    service['flag_submitted'],
                    service['flags_lost'],
                    service['sla_value'],
                    service['is_down'],
                    service['timestamp']
                )
                formatted_records.append(formatted_record)

        return formatted_records

    def insert_records(self, records):
        records = self.format_record(records)
        logging.debug(records)
        with sqlite3.connect(self.name_db) as conn:
            c = conn.cursor()
            c.executemany('''
                INSERT INTO table_records (name_team, score_team, name_service, score_service, flag_submitted, flags_lost, sla_value, is_down, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', records)
            conn.commit()

    def remove_db(self):
        with sqlite3.connect(self.name_db) as conn:
            c = conn.cursor()
            c.execute('''DROP TABLE table_records''')

    def fetch_by_team(self, team: str):
        pass

    def fetch_by_service(self, service: str):
        pass

    def fetch_by_team_service(self, team, service: str):
        pass

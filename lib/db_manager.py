import sqlite3

from lib.logger import logging


class DBManager:
    def __init__(self):
        self.name_db = "db.sqlite3"
        if self.init():
            logging.info("Database initialization successful")

    def init(self) -> bool:
        """Initialize the database"""
        try:
            with sqlite3.connect(self.name_db) as conn:
                cursor = conn.cursor()
                query = '''
                    
                    )
                '''
                cursor.execute(query)
                conn.commit()
                return True
        except sqlite3.OperationalError:
            return False

    def remove_db(self, name_table: str) -> None:
        """Remove the database"""
        with sqlite3.connect(self.name_db) as conn:
            c = conn.cursor()
            c.execute(f'''DROP TABLE {name_table}''')

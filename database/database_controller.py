import sqlite3
import logging

stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class DatabaseController(object):

    def __init__(self, path):
        self.__path = path

        try:
            self.__connection = sqlite3.connect(path)
            self.__ensure_utxo_table()
        except sqlite3.Error as e:
            raise e

    def __del__(self):
        self.__connection.close()

    def __ensure_utxo_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS utxos (
            hash TEXT NOT NULL,
            vout INTEGER NOT NULL,
            height INTEGER NOT NULL,
            value INTEGER,
            script TEXT,
            type TEXT,
            target TEXT,
            PRIMARY KEY (hash, vout, height)
        );
        """
        self.execute_query(create_table_query)
        
        create_index_query = """
        CREATE INDEX IF NOT EXISTS target_index ON utxos (target);
        """
        self.execute_query(create_index_query)

    def execute_query(self, query):
        cursor = self.__connection.cursor()
        try:
            cursor.execute(query)
            self.__connection.commit()
        except sqlite3.Error as e:
            log.error(f"database error '{e}' occurred")
            raise e

    def execute_read_query(self, query, parameters = None):
        cursor = self.__connection.cursor()
        result = None
        try:
            if parameters is None:
                cursor.execute(query)
            else:
                cursor.execute(query, parameters)
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            log.error(f"database error '{e}' occurred")
            raise e

    def update_utxos(self, inputs, outputs):
        cursor = self.__connection.cursor()
        try:
            cursor.executemany("DELETE FROM utxos WHERE hash = ? AND vout = ?", [input.make_tuple() for input in inputs])
            cursor.executemany("INSERT INTO utxos VALUES (?,?,?,?,?,?,?)", [output.make_tuple() for output in outputs])
            self.__connection.commit()
        except sqlite3.Error as e:
            log.error(f"database error '{e}' occurred")
            raise e

    def vacuum(self):
        try:
            self.__connection.execute("VACUUM")
        except sqlite3.Error as e:
            log.error(f"database error '{e}' occurred")
            raise e
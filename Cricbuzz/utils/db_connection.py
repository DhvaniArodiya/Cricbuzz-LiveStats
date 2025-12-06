import sqlite3

def get_connection(db_path="cricbuzz.db"):
    """
    Create and return a new SQLite database connection.

    Args:
        db_path (str): Path to the SQLite database file. Defaults to 'cricbuzz.db'.

    Returns:
        sqlite3.Connection: SQLite connection object.
    """
    conn = sqlite3.connect(db_path)
    return conn

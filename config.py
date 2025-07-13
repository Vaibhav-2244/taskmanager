import os

DB_CONFIG = {
    'server': os.environ.get('DB_SERVER'),
    'database': os.environ.get('DB_NAME'),
    'username': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASS'),
    'driver': '{ODBC Driver 18 for SQL Server}'
}

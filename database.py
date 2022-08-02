import psycopg2
from psycopg2 import Error


try:
    db_connect = psycopg2.connect(database="appdb", user = "appuser", password = "apppass", host = "db", port = "5432")
    print("Opened PostgreSQL successfully")

except (Exception, Error) as error:
    print(error)


def add_events_table():
    try:
        db_cursor = db_connect.cursor()
        db_cursor.execute("DROP TABLE IF EXISTS events;")
        db_cursor.execute('''CREATE TABLE EVENTS
            (URL   VARCHAR(255)  PRIMARY KEY    NOT NULL,
            TITLE     VARCHAR(255),
            LOCATION     VARCHAR(255),
            DATE     DATE,
            TIME     VARCHAR(255),
            PRICE    VARCHAR(255),
            ARTISTS     VARCHAR(255),
            IMAGE     VARCHAR(500),
            CREATED_AT   TIMESTAMPTZ    NOT NULL   DEFAULT   NOW());''')
        print("Table created successfully")
        db_connect.commit()

    except (Exception, Error) as error:
        print(error)
        db_connect.rollback()


def insert_events_info(path, title, location, date, time, price, artists, img_link):
    try:
        db_cursor = db_connect.cursor()
        db_cursor.execute("""
            INSERT INTO events 
            (url, title, location, date, time, price, artists, image) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, 
            (path, title, location, date, time, price, artists, img_link));
        db_connect.commit()

    except (Exception, Error) as error:
        print( error)
        db_connect.rollback()


def fetch_events_info():
    try:
        db_cursor = db_connect.cursor()
        db_cursor.execute("""
            SELECT DISTINCT
            TO_CHAR(DATE(events.date), 'dd/mm')   AS day,
            COUNT(*)   AS count
            FROM events 
            GROUP BY day
            ORDER BY day ASC
        """);
        db_connect.commit()

        event_occurrence_with_date = db_cursor.fetchall()
        return event_occurrence_with_date

    except (Exception, Error) as error:
        print(error)
        db_connect.rollback()

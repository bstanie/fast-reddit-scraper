import sqlite3


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)


def generate_db(database_name):
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS posts (
                                        id integer PRIMARY KEY,
                                        post_id text NOT NULL UNIQUE,
                                        link text,
                                        timestamp timestamp,
                                        title text,
                                        text text,
                                        image text,
                                        subreddit text
                                    ); """

    # create a database connection
    conn = create_connection(database_name)

    # create tables
    if conn is not None:
        create_table(conn, sql_create_projects_table)
    else:
        print("Error! cannot create the database connection.")

    return conn


def make_chunks(data, rows=1000):
    """ Divides the data into 1000 rows each """

    for i in range(0, len(data), rows):
        yield data[i:i + rows]


def write_to_db(cur, data):
    divData = make_chunks(data)
    print('Inserting to database')
    for chunk in divData:
        cur.execute('BEGIN TRANSACTION')

        for post in chunk:
            cur.execute('INSERT OR IGNORE INTO posts (post_id, link, timestamp, title, text,image, subreddit) '
                        ''
                        'VALUES (?,?,?,?,?,?,?)', (post['post_id'], post['link'],
                                                   post['timestamp'], post['title'],
                                                   post['text'], post['image'],
                                                   post['subreddit']))

        cur.execute('COMMIT')

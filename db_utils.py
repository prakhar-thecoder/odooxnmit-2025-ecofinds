import mysql.connector
import config


# Minimal helpers: no error handling, no long docs.
def select_query(query, params=None):
    conn = mysql.connector.connect(
        host=getattr(config, 'MYSQL_HOST', 'localhost'),
        user=getattr(config, 'MYSQL_USER', None),
        password=getattr(config, 'MYSQL_PASSWORD', None),
        database=getattr(config, 'MYSQL_DATABASE', None),
    )
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def insert_query(query, params=None):
    conn = mysql.connector.connect(
        host=getattr(config, 'MYSQL_HOST', 'localhost'),
        user=getattr(config, 'MYSQL_USER', None),
        password=getattr(config, 'MYSQL_PASSWORD', None),
        database=getattr(config, 'MYSQL_DATABASE', None),
    )
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    rc = cur.rowcount
    cur.close()
    conn.close()
    return rc


def update_query(query, params=None):
    conn = mysql.connector.connect(
        host=getattr(config, 'MYSQL_HOST', 'localhost'),
        user=getattr(config, 'MYSQL_USER', None),
        password=getattr(config, 'MYSQL_PASSWORD', None),
        database=getattr(config, 'MYSQL_DATABASE', None),
    )
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    rc = cur.rowcount
    cur.close()
    conn.close()
    return rc


def delete_query(query, params=None):
    conn = mysql.connector.connect(
        host=getattr(config, 'MYSQL_HOST', 'localhost'),
        user=getattr(config, 'MYSQL_USER', None),
        password=getattr(config, 'MYSQL_PASSWORD', None),
        database=getattr(config, 'MYSQL_DATABASE', None),
    )
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    rc = cur.rowcount
    cur.close()
    conn.close()
    return rc

import pymysql

def connect():
    conn = pymysql.connect(
        user='circlejerk_bot',
        host='localhost',
        port=3306,
        passwd='tepra6hu7e4ruHunef7emepeh4raswa2',
        db='circlejerk_bot')
    return conn

import hashlib

from contextlib import closing

def remember_tweet(conn, url):
    q = '''
    INSERT INTO already_tweeted
    (url, sha_one)
    VALUES
    (%s, %s)
    '''
    with closing(conn.cursor()) as cur:
        hasher = hashlib.new('sha1')
        hasher.update(url)
        cur.execute(q, (url, hasher.hexdigest()))
        conn.commit()

def already_tweeted(conn, url):
    q = '''
    SELECT url
    FROM already_tweeted
    WHERE sha_one=%s
    '''
    with closing(conn.cursor()) as cur:
        hasher = hashlib.new('sha1')
        hasher.update(url)
        return cur.execute(q, (hasher.hexdigest(),)) != 0

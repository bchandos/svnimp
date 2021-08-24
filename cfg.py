from collections import namedtuple
import sqlite3

import aiosql



queries = aiosql.from_path('sql/repos.sql', 'sqlite3')

Repo = namedtuple('Repo', ['id', 'name', 'path'])

def get_conn():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

def load_repos():
    conn = get_conn()
    with conn:
        repos = [
            Repo(id=r['id'], name=r['name'], path=r['path'])
            for r in queries.get_all_repos(conn)
        ]

    return repos

def create_repo(name, path, cache_logs):
    conn = get_conn()
    with conn:
        queries.create_repo(conn, name, path, cache_logs)
    return load_repos()


schema = aiosql.from_path('sql/schema.sql', 'sqlite3')
conn = get_conn()
with conn:
    schema.create_schema(conn)

repos = load_repos()
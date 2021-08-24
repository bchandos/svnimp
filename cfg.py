from collections import namedtuple
import sqlite3

import aiosql

conn = sqlite3.connect('db.sqlite')
conn.row_factory = sqlite3.Row

schema = aiosql.from_path('sql/schema.sql', 'sqlite3')
schema.create_schema(conn)

queries = aiosql.from_path('sql/repos.sql', 'sqlite3')

Repo = namedtuple('Repo', ['id', 'name', 'path'])

def load_repos():
    repos = [
        Repo(id=r['id'], name=r['name'], path=r['path'])
        for r in queries.get_all_repos(conn)
    ]

    return repos

def create_repo(name, path, cache_logs):
    queries.create_repo(conn, name, path, cache_logs)
    return load_repos()

repos = load_repos()
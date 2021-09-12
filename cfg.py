from collections import namedtuple
import json
import sqlite3

import aiosql

repo_queries = aiosql.from_path('sql/repos.sql', 'sqlite3')
log_queries = aiosql.from_path('sql/logs.sql', 'sqlite3')

Repo = namedtuple('Repo', ['id', 'name', 'path', 'cache_logs'])

def get_conn():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

def load_repos():
    conn = get_conn()
    with conn:
        repos = [
            Repo(id=r['id'], name=r['name'], path=r['path'], cache_logs=r['cache_logs'])
            for r in repo_queries.get_all_repos(conn)
        ]

    return repos

def create_repo(name, path, cache_logs):
    conn = get_conn()
    with conn:
        repo_queries.create_repo(conn, name, path, cache_logs)
    return load_repos()

def get_cached_logs(repo_id, start_rev, end_rev=None):
    conn = get_conn()
    with conn:
        if end_rev:
            logs = log_queries.get_logs(conn, repo_id, start_rev, end_rev)
        else:
            logs = log_queries.get_log(conn, repo_id, start_rev)
    return [json.loads(l[0]) for l in logs]

def cache_log(repo_id, revision, log_entry):
    conn = get_conn()
    with conn:
        try:
            log_queries.cache_log(conn, repo_id, revision, log_entry)
        except sqlite3.IntegrityError:
            # Kindly ignore unique constraint failures
            pass

schema = aiosql.from_path('sql/schema.sql', 'sqlite3')
conn = get_conn()
with conn:
    schema.create_schema(conn)

repos = load_repos()
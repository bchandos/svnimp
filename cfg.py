from dataclasses import dataclass
import json
import sqlite3
from typing import Optional

import aiosql

repo_queries = aiosql.from_path('sql/repos.sql', 'sqlite3')
log_queries = aiosql.from_path('sql/logs.sql', 'sqlite3')

# Repo = namedtuple('Repo', ['id', 'name', 'path', 'cache_logs'])

@dataclass
class Repo:
    """ Class to represent an SVN repository """
    id: int
    name: str
    path: str
    cache_logs: bool

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

def load_repos() -> list:
    conn = get_conn()
    with conn:
        repos = [
            Repo(id=r['id'], name=r['name'], path=r['path'], cache_logs=r['cache_logs'])
            for r in repo_queries.get_all_repos(conn)
        ]

    return repos

def create_repo(name: str, path: str, cache_logs: bool) -> list:
    conn = get_conn()
    with conn:
        repo_queries.create_repo(conn, name, path, cache_logs)
    return load_repos()

def get_cached_logs(repo_id: int, start_rev: int, end_rev: Optional[int] = None, path: Optional[str] = None) -> list:
    conn = get_conn()
    with conn:
        if end_rev:
            logs = log_queries.get_logs(conn, repo_id, start_rev, end_rev)
        else:
            logs = log_queries.get_log(conn, repo_id, start_rev)
    
    parsed_logs = [json.loads(l[0]) for l in logs]
    if path:
        return [l for l in parsed_logs if path in l]
    return parsed_logs

def cache_log(repo_id: int, revision: int, log_entry: str):
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
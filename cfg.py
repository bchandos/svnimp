import json
import os
from collections import namedtuple

Repo = namedtuple('Repo', ['id', 'name', 'path'])

def load_repos():
    if not os.path.exists('cfg.json'):
        return list()
    
    with open('cfg.json', 'r') as j:
        cfg = json.loads(j.read())

    repos = [
        Repo(id=idx, name=c['name'], path=c['path'])
        for idx, c in enumerate(cfg['repos'])
    ]

    return repos

def create_repo(name, path):
    if os.path.exists('cfg.json'):
        with open('cfg.json', 'r') as j:
            cfg = json.loads(j.read())
    else:
        cfg = dict(repos=list())
    cfg['repos'].append(dict(name=name, path=path))

    with open('cfg.json', 'w') as j:
        j.write(json.dumps(cfg))
    
    return load_repos()


repos = load_repos()
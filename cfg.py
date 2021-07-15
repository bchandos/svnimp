from collections import namedtuple

Repo = namedtuple('Repo', ['id', 'name', 'path'])

repos = [
    Repo(id=1, name='eccares', path='/Users/chandos/eccares'),
    Repo(id=2, name='e3k', path='/Users/chandos/e3k'),
    Repo(id=3, name='ecparent', path='/Users/chandos/ecparent'),
]
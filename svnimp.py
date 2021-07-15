from urllib.parse import unquote

import bottle
from bottle import Bottle, route, run, jinja2_view, static_file

from svn import info, status, diff_file

from cfg import repos

bottle.debug(True)

app = Bottle()



def get_repo_from_id(repo_id):
    return next(x for x in repos if x['id'] == repo_id)

@app.get('/')
@jinja2_view('views/main.html')
def svn_info():
    return dict(
        repos=repos,
    )

@app.get('/repo/<repo_id:int>')
@jinja2_view('views/repo.html')
def svn_info(repo_id):
    repo = get_repo_from_id(repo_id)
    repo_path = repo.path
    info_ = info(repo_path)
    status_ = status(repo_path)
    return dict(
        name=repo.name,
        repo_id=repo.id,
        repository=info_['entry']['repository'],
        commit=info_['entry']['commit'],
        status=status_,
    )

@app.get('/diff/<repo_id:int>')
@jinja2_view('views/diff.html')
def svn_diff(repo_id):
    data = {k: v for k, v in bottle.request.params.items()}
    path = unquote(data.get('path'))
    repo = get_repo_from_id(repo_id)
    repo_path = repo.path
    return dict(
        lines=diff_file(repo_path, (path,)),
        repo=repo.id,
        path=path,
    )


@app.get("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="static/js")

run(app, host='localhost', port=4444)
import json
from urllib.parse import unquote

import bottle
from bottle import Bottle, route, run, jinja2_view, static_file, redirect

from svn import info, status, diff_file, add_paths, add_to_changelist, remove_from_changelist, commit_paths

from cfg import repos, create_repo

bottle.debug(True)

app = Bottle()

## HELPER FUNCTIONS ##
def get_repo_from_id(repo_id):
    return next(x for x in repos if x.id == repo_id)

def get_uq_paths_from_json(json_):
    paths = json_.get('paths')
    return [unquote(p) for p in paths]

## END HELPER FUNCTIONS - ALL FURTHER FUNCTION MUST BE UNHELPFUL ##
@app.get('/')
@jinja2_view('views/main.html')
def svn_info():
    return dict(
        repos=repos,
    )

# HTTP Views

@app.get('/repo/<repo_id:int>')
@jinja2_view('views/repo.html')
def svn_info(repo_id):
    repo = get_repo_from_id(repo_id)
    repo_path = repo.path
    info_ = info(repo_path)
    status_ = status(repo_path)
    changelists = status_.get('changelist',{})
    if isinstance(changelists, list):
        cl_names = [cl.get('name') for cl in changelists]
    else:
        cl_names = [changelists.get('name')] if changelists.get('name') else []
    
    return dict(
        name=repo.name,
        repo_id=repo.id,
        repository=info_['entry']['repository'],
        commit=info_['entry']['commit'],
        status=status_,
        cl_names=cl_names,
        repos=repos,
    )

# AJAX Views

@app.get('/diff/<repo_id:int>')
@jinja2_view('views/diff.html')
def svn_diff(repo_id):
    data = {k: v for k, v in bottle.request.params.items()}
    path = unquote(data.get('path'))
    repo = get_repo_from_id(repo_id)
    return dict(
        lines=diff_file(repo.path, (path,)),
        repo=repo.id,
        path=path,
    )

@app.post('/add-paths/<repo_id:int>')
def svn_add(repo_id):
    uq_paths = get_uq_paths_from_json(bottle.request.json)
    repo = get_repo_from_id(repo_id)
    added_paths = add_paths(repo.path, uq_paths)
    if (set(added_paths) == set(uq_paths)):
        return json.dumps(
            dict(
                status='ok'
            )
        )
    return json.dumps(dict(status='error'))

@app.post('/changelist/<repo_id:int>/<action:re:(add|remove)>')
def svn_cl(repo_id, action):
    uq_paths = get_uq_paths_from_json(bottle.request.json)
    repo = get_repo_from_id(repo_id)
    if action == 'add':
        cl_name = bottle.request.json.get('clName')
        processed_paths = add_to_changelist(repo.path, cl_name, uq_paths)
    elif action == 'remove':
        processed_paths = remove_from_changelist(repo.path, uq_paths)
    if (set(processed_paths) == set(uq_paths)):
        return json.dumps(
            dict(
                status='ok'
            )
        )
    return json.dumps(dict(status='error'))

@app.post('/commit/<repo_id:int>')
def commit(repo_id):
    """ Commit some paths """
    data = {k: v for k, v in bottle.request.params.items()}
    uq_paths = get_uq_paths_from_json(data)
    commit_msg = data.get('commitMessage')
    repo = get_repo_from_id(repo_id)
    processed_paths = commit_paths(repo.path, uq_paths, commit_msg)
    if (set(processed_paths) == set(uq_paths)):
        return json.dumps(
            dict(
                status='ok'
            )
        )
    return json.dumps(dict(status='error'))

@app.post('/repo/add')
def add_repo():
    """ Create a new repo """
    data = {k: v for k, v in bottle.request.params.items()}
    global repos
    repos = create_repo(data.get('repo-name', ''), data.get('repo-path', ''))
    redirect(bottle.request.get_header('referer', '/'))
# Static files

@app.get("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="static/js")

@app.get("/static/images/<filepath:re:(.*\.svg|.*\.png|.*\.ico)>")
def images(filepath):
    return static_file(filepath, root="static/images")

@app.get("/static/css/<filepath:re:(.*\.css)>")
def images(filepath):
    return static_file(filepath, root="static/css")

run(app, host='localhost', port=4444)
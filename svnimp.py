from datetime import datetime
from dateutil import tz
import json
from urllib.parse import unquote

import bottle
from bottle import Bottle, route, run, jinja2_view, static_file, redirect, BaseTemplate

from svn import get_head_revision, get_logs, info, status, diff_file, add_paths, add_to_changelist, remove_from_changelist, commit_paths, update, revert

from cfg import cache_log, repos, create_repo, get_cached_logs

bottle.debug(True)

app = Bottle()

## HELPER FUNCTIONS ##
def get_repo_from_id(repo_id: int):
    return next(x for x in repos if x.id == repo_id)

def get_uq_paths_from_json(json_):
    paths = json_.get('paths')
    return [unquote(p) for p in paths]

def dtfmt(val: str):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Pacific/Los_Angeles')
    t = datetime.strptime(val, '%Y-%m-%dT%H:%M:%S.%fZ')
    t = t.replace(tzinfo=from_zone)
    z = t.astimezone(to_zone)
    return z.strftime('%m/%d/%Y %I:%M%p')

BaseTemplate.settings.update({'filters': {'dtfmt': dtfmt}})

## END HELPER FUNCTIONS - ALL FURTHER FUNCTIONS MUST BE UNHELPFUL ##

# HTTP Views
@app.get('/')
@jinja2_view('views/main.html')
def svn_info():
    return dict(
        repos=repos,
    )


@app.get('/repo/<repo_id:int>')
@jinja2_view('views/repo.html')
def svn_info(repo_id: int):
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

@app.get('/repo/<repo_id:int>/logs')
@jinja2_view('views/logs.html')
def svn_logs(repo_id: int):
    data = {k: v for k, v in bottle.request.params.items()}
    repo = get_repo_from_id(repo_id)
    repo_path = repo.path
    last_rev = get_head_revision(repo_path)
    offset = 20 if last_rev > 20 else last_rev
    start_rev = int(data.get('start', str(last_rev - offset)))
    end_rev = int(data.get('end', last_rev))
    
    if repo.cache_logs:
        cached_logs = get_cached_logs(repo.id, start_rev, end_rev)
        revs_from_cache = {int(l['revision']) for l in cached_logs}
        if revs_from_cache == set(range(start_rev, end_rev + 1)):
            live_logs = list()
        else:
            live_logs = get_logs(repo_path, start_rev=start_rev, end_rev=end_rev)
            cached_logs = list()
            for log in live_logs:
                cache_log(repo.id, int(log['revision']), json.dumps(log))
    else:
        live_logs = get_logs(repo_path, start_rev=start_rev, end_rev=end_rev)
        cached_logs = list()

    logs = cached_logs + live_logs
    return dict(
        name=repo.name,
        repo_id=repo.id,
        logs=logs,
        repos=repos,
        start_rev=start_rev,
        end_rev=end_rev,
        last_rev=last_rev,
    )

# AJAX Views

@app.get('/diff/<repo_id:int>')
@jinja2_view('views/diff.html')
def svn_diff(repo_id: int):
    data = {k: v for k, v in bottle.request.params.items()}
    path = unquote(data.get('path'))
    repo = get_repo_from_id(repo_id)
    return dict(
        lines=diff_file(repo.path, (path,)),
        repo=repo.id,
        path=path,
    )

@app.post('/add-paths/<repo_id:int>')
def svn_add(repo_id: int):
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
def svn_cl(repo_id: int, action: str):
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
def commit(repo_id: int):
    """ Commit some paths """
    uq_paths = get_uq_paths_from_json(bottle.request.json)
    data = bottle.request.json
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
    repos = create_repo(
        data.get('repo-name', ''), 
        data.get('repo-path', ''),
        int(data.get('repo-cache-logs') == 'on')
    )
    redirect(bottle.request.get_header('referer', '/'))

@app.get('/update/<repo_id:int>')
def update_repo(repo_id: int):
    """ Update a repo """
    repo = get_repo_from_id(repo_id)
    update(repo.path)

    redirect(bottle.request.get_header('referer', '/'))

@app.post('/revert/<repo_id:int>')
def revert_paths(repo_id: int):
    """ Revert paths """
    repo = get_repo_from_id(repo_id)
    uq_paths = get_uq_paths_from_json(bottle.request.json)
    reverted = revert(repo, uq_paths)


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

# Testing

@app.get('/test-page')
@jinja2_view('views/test.html')
def test_page():
    """ A test page, obvi """
    return dict(
        repos=repos,
    )



# Run the Application

run(app, host='localhost', port=4444)

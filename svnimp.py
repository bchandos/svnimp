from datetime import datetime
from dateutil import tz
import json
from urllib.parse import unquote
from subprocess import TimeoutExpired
import os

import bottle
from bottle import Bottle, route, run, jinja2_view, static_file, redirect, BaseTemplate, install

from svn import get_head_revision, get_logs, info, list_paths, status, diff_file, add_paths, add_to_changelist, remove_from_changelist, commit_paths, update, revert

from cfg import cache_log, repos, create_repo, get_cached_logs

bottle.debug(True)

app = Bottle()

session_msg = None

project_directory = os.getcwd()

## HELPER FUNCTIONS ##

def get_repo_from_id(repo_id: int):
    return next(x for x in repos if x.id == repo_id)

def get_uq_paths_from_json(json_: dict) -> list:
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

## BEGIN PLUGINS

def timeout_catcher(callback):
    def wrapper(*args, **kwargs):
        try:
            return callback(*args, **kwargs)
        except TimeoutExpired:
            os.chdir(project_directory)
            referer = bottle.request.get_header('Referer', '/')
            global session_msg
            session_msg = 'SVN process timed out. Are you sure you can reach the server?'
            # if bottle.request.is_xhr:
                # return 
            return bottle.redirect(referer)
    return wrapper

app.install(timeout_catcher)

## END PLUGINS

# HTTP Views
@app.get('/')
@jinja2_view('main.html')
def svn_info():
    return dict(
        repos=repos,
        session_msg=session_msg,
    )


@app.get('/repo/<repo_id:int>')
@jinja2_view('repo.html')
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
        session_msg=session_msg
    )

@app.get('/repo/<repo_id:int>/logs/<direction:re:(ascending|descending)>')
@jinja2_view('logs.html')
def svn_logs(repo_id: int, direction: str):
    data = {k: v for k, v in bottle.request.params.items()}
    repo = get_repo_from_id(repo_id)
    repo_path = repo.path
    last_rev = get_head_revision(repo_path)
    if single_revision := data.get('single-revision'):
        start_rev = int(single_revision)
        end_rev = int(single_revision)
    else:
        offset = 20 if last_rev > 20 else last_rev
        start_rev = int(data.get('start', str(last_rev - offset)))
        end_rev = int(data.get('end', last_rev))
    
    specific_path = data.get('specific-path', '')

    if repo.cache_logs:
        cached_logs = get_cached_logs(repo.id, start_rev, end_rev, specific_path)
        revs_from_cache = {int(l['revision']) for l in cached_logs}
        if revs_from_cache == set(range(start_rev, end_rev + 1)):
            live_logs = list()
        else:
            live_logs = get_logs(repo_path, start_rev=start_rev, end_rev=end_rev, path=specific_path)
            cached_logs = list()
            for log in live_logs:
                cache_log(repo.id, int(log['revision']), json.dumps(log))
    else:
        live_logs = get_logs(repo_path, start_rev=start_rev, end_rev=end_rev, path=specific_path)
        cached_logs = list()
    available_paths = list_paths(repo_path, end_rev)
    logs = cached_logs + live_logs
    if direction == 'descending':
        logs.reverse()

    direction_url = f'/repo/{repo_id}/logs/{"ascending" if direction=="descending" else "descending"}?'
    direction_url += f'start={start_rev}'
    direction_url += f'&end={end_rev}'
    if single_revision:
        direction_url += f'&single-revision={single_revision}'
    if specific_path:
        direction_url += f'&specific-path={specific_path}'
    
    return dict(
        name=repo.name,
        repo_id=repo.id,
        logs=logs,
        repos=repos,
        start_rev=start_rev,
        end_rev=end_rev,
        last_rev=last_rev,
        direction=direction,
        direction_url=direction_url,
        session_msg=session_msg,
        available_paths=available_paths,
        specific_path=specific_path,
    )

# AJAX Views

@app.get('/diff/<repo_id:int>')
@jinja2_view('diff.html')
def svn_diff(repo_id: int):
    data = {k: v for k, v in bottle.request.params.items()}
    path = unquote(data.get('path'))
    repo = get_repo_from_id(repo_id)
    start_rev = data.get('start_rev')
    end_rev = data.get('end_rev')
    if start_rev and end_rev:
        start_rev, end_rev = map(int, (start_rev, end_rev))
    
    return dict(
        lines=diff_file(repo.path, (path,), start_rev, end_rev),
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
    processed_paths, revision = commit_paths(repo.path, uq_paths, commit_msg)
    if (set(processed_paths) == set(uq_paths)):
        return json.dumps(
            dict(
                status='ok',
                message=f'Succesfully commited {len(processed_paths)} path{"s" if len(processed_paths) > 1 else ""}, revision {revision}',
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
    update_result = update(repo.path)
    if not update_result:
        global session_msg
        session_msg = 'Possible merge conflicts, update manually until I know how to do that.'
    redirect(bottle.request.get_header('referer', '/'))

@app.post('/revert/<repo_id:int>')
def revert_paths(repo_id: int):
    """ Revert paths """
    repo = get_repo_from_id(repo_id)
    uq_paths = get_uq_paths_from_json(bottle.request.json)
    reverted = revert(repo.path, uq_paths)
    
    if all([uq_path in reverted for uq_path in uq_paths]):
        return json.dumps(
            dict(
                status='ok'
            )
        )
    return json.dumps(dict(status='error'))

@app.post('/set-session-msg')
def set_session_msg():
    """ Set a session message """
    data = bottle.request.json
    global session_msg
    session_msg = data.get('msg')

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
@jinja2_view('test.html')
def test_page():
    """ A test page, obvi """
    return dict(
        repos=repos,
    )



# Run the Application

run(app, host='0.0.0.0', port=4444)

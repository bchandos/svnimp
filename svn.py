import subprocess
import re
import os
from tempfile import NamedTemporaryFile
from typing import Optional

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

from xmltodict import pluralize_dict_key, xml_to_dict

def run_xml_cmd(repo: str, args: tuple, list_elems=tuple()) -> dict:
    cwd = os.getcwd()
    os.chdir(repo)
    newargs = args + ('--xml',)
    # Elements that we always want to be list/array type, 
    # regardless of how many child elements they have
    p = subprocess.run(newargs, stdout=subprocess.PIPE, timeout=10)
    try:
        d = xml_to_dict(ET.XML(p.stdout))
        for elem in list_elems:
            d = pluralize_dict_key(d, elem)
    except ParseError:
        d = dict()
    os.chdir(cwd)
    return d

def run_standard_cmd(repo: str, args: tuple):
    cwd = os.getcwd()
    os.chdir(repo)
    p = subprocess.run(args, stdout=subprocess.PIPE, timeout=10)
    res = p.stdout
    os.chdir(cwd)
    
    return res.decode('utf-8')

def status(repo: str) -> dict:
    return run_xml_cmd(repo, ('svn', 'status'), list_elems=('changelist', 'entry'))['status']

def info(repo: str) -> dict:
    return run_xml_cmd(repo, ('svn', 'info'))['info']

def repo_type(repo: str) -> str:
    i = info(repo)
    url = i.get('url')
    return url.split('://')[0]

def relative_url(repo: str) -> str:
    i = info(repo)
    ru = i['entry']['relative-url']
    return ru.split('^/')[1]

def diff_file(repo: str, paths: tuple, start_rev: Optional[int] = None, end_rev: Optional[int] = None) -> list:
    if start_rev and end_rev:
        rev = (f'-r{start_rev}:{end_rev}',)
    else:
        rev = tuple()
    if all([p[0] == '/' for p in paths]):
        tmp_paths = (p[1:] for p in paths)
        ru = relative_url(repo)
        paths = tuple(p.replace(f'{ru}/', '', 1) if ru else p for p in tmp_paths)
    print(paths)
    diffs = run_standard_cmd(repo, ('svn', 'diff') + rev + paths)
    return process_diffs(diffs)

def diff_cl(repo: str, cl_name: str) -> list:
    diffs = run_standard_cmd(repo, ('svn', 'diff', '--cl', cl_name))
    return process_diffs(diffs)

def process_diffs(diff_string: str) -> list:
    all_lines = diff_string.splitlines()
    pattern = 'Index: (.*)'
    for idx, line in enumerate(all_lines):
        m = re.match(pattern, line)
        if m:
            start_idx = idx + 4
            return all_lines[start_idx:]

def add_to_changelist(repo, cl_name, paths):
    added = run_standard_cmd(repo, ('svn', 'changelist', cl_name) + tuple(paths))
    idx = 5 + len(cl_name)
    return [p[idx:] for p in added.split('\n') if p]

def remove_from_changelist(repo, paths):
    removed = run_standard_cmd(repo, ('svn', 'changelist', '--remove') + tuple(paths))
    lines = [p for p in removed.split('\n') if p]
    m = re.search('D \[(.*)\]', lines[0])
    cl_name = m.group(1) if m else 0
    idx = 5 + len(cl_name)
    return [p[idx:] for p in lines]

def add_paths(repo, paths):
    # Add a collection of paths to version control
    added = run_standard_cmd(repo, ('svn', 'add') + tuple(paths))
    return [p[10:] for p in added.split('\n') if p]

def commit_paths(repo, paths, commit_msg):
    with NamedTemporaryFile(mode='w+') as tmp:
        tmp.write(commit_msg)
        tmp.seek(0)
        checked_in = run_standard_cmd(repo, ('svn', 'ci')  + tuple(paths) + ('--file', tmp.name))
        lines = [p for p in checked_in.split('\n') if p]
        ci_paths = list()
        for line in lines:
            if 'Transmitting file data' in line:
                continue
            if 'Committing transaction' in line:
                continue
            if 'Committed revision' in line:
                revision = int(line[18:].strip().replace('.',''))
                continue
            ci_paths.append(line[14:].strip())
        return (ci_paths, revision)

def get_logs(repo, start_rev, end_rev, paths=tuple()):
    # Get logs from SVN
    return run_xml_cmd(
        repo, 
        ('svn', 'log', '--verbose') + tuple(paths) + (f'-r{start_rev}:{end_rev}',),
        list_elems=('path',)
    ).get('log',{}).get('logentry',[])

def update(repo):
    # Update the repo, ignoring output
    # First, attempt to detect the possibility of merge conflicts
    status_update = run_xml_cmd(repo, ('svn', 'status', '-u'))
    print(status_update)
    # run_standard_cmd(repo, ('svn', 'up'))

def get_head_revision(repo):
    # Get the true head revision number by parsing svnversion
    args = ('svnversion',)
    cwd = os.getcwd()
    os.chdir(repo)
    p = subprocess.run(args, stdout=subprocess.PIPE)
    res = p.stdout.decode('utf-8')
    os.chdir(cwd)
    svn_v = res.split(':')[1] if ':' in res else res
    return int(svn_v.strip().replace('M',''))

def revert(repo, paths):
    # Revert paths
    reverted_paths = run_standard_cmd(repo, ('svn', 'revert') + tuple(paths))
    lines = [p for p in reverted_paths.split('\n') if p]
    return [line.split('Reverted')[1].strip().replace('\'', '') for line in lines if 'Reverted' in line]

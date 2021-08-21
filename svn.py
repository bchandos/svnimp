from collections import defaultdict
import json
import subprocess
import re
import os
from tempfile import NamedTemporaryFile

import xml.etree.ElementTree as ET

from xmltodict import XmlDictConfig

def run_xml_cmd(repo, args):
    cwd = os.getcwd()
    os.chdir(repo)
    newargs = args + ('--xml',)
    p = subprocess.run(newargs, stdout=subprocess.PIPE)
    d = XmlDictConfig(ET.XML(p.stdout))
    os.chdir(cwd)
    return d

def run_standard_cmd(repo, args):
    cwd = os.getcwd()
    os.chdir(repo)
    p = subprocess.run(args, stdout=subprocess.PIPE)
    res = p.stdout
    os.chdir(cwd)
    
    return res.decode('utf-8')

def status(repo):
    return run_xml_cmd(repo, ('svn', 'status'))

def info(repo):
    return run_xml_cmd(repo, ('svn', 'info'))

def diff_file(repo, paths):
    diffs = run_standard_cmd(repo, ('svn', 'diff') + paths)
    return process_diffs(diffs)

def diff_cl(repo, cl_name):
    diffs = run_standard_cmd(repo, ('svn', 'diff', '--cl', cl_name))
    return process_diffs(diffs)

def process_diffs(diff_string):
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
    

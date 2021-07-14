from collections import defaultdict
import json
import subprocess
import re
import os

import xml.etree.ElementTree as ET

from xmltodict import XmlDictConfig

def run_xml_cmd(repo, args):
    cwd = os.getcwd()
    os.chdir(repo)
    newargs = args + ('--xml',)
    p = subprocess.run(newargs, stdout=subprocess.PIPE)
    d = XmlDictConfig(ET.XML(p.stdout))
    os.chdir(cwd)
    # print(json.dumps(d, indent=1))
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

def create_changelist(repo, cl_name, paths):
    run_standard_cmd(repo, ('svn', 'changelist', cl_name) + paths)
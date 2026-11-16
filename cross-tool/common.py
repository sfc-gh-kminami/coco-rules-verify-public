"""Shared helpers: paths, random IDs, mapping, instruction-file writer."""
import hashlib
import json
import os
import secrets
import string
import subprocess
import threading
from pathlib import Path

ROOT = Path(os.environ.get('XTOOL_ROOT', '/tmp/xtool-verify')).resolve()
FIX = ROOT / 'fixtures'
HOOKS = ROOT / '_hooks'            # hook scripts live outside every workspace
RESULTS = ROOT / 'results'
MAPF = FIX / 'mapping.json'
INVLOG = HOOKS / 'invocations.log'

_lock = threading.Lock()


def rid(n=12):
    """Random upper-case alnum ID that contains at least one letter and one digit."""
    alpha = string.ascii_uppercase + string.digits
    while True:
        s = ''.join(secrets.choice(alpha) for _ in range(n))
        if any(c.isdigit() for c in s) and any(c.isalpha() for c in s):
            return s


def sha(p):
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except FileNotFoundError:
        return None


def load_map():
    if MAPF.exists():
        return json.loads(MAPF.read_text())
    return {'ids': {}, 'tags': {}}


class Mapping:
    def __init__(self):
        self.m = {'ids': {}, 'tags': {}}

    def add_id(self, path, label, kind='body'):
        i = rid()
        self.m['ids'][i] = {'path': str(path), 'label': label, 'kind': kind}
        return i

    def add_tag(self, path):
        t = rid(6)
        self.m['tags'][t] = str(path)
        return t

    def save(self):
        MAPF.parent.mkdir(parents=True, exist_ok=True)
        with _lock:
            MAPF.write_text(json.dumps(self.m, indent=1))


def write_instruction(mp, path, label, fm=None, rule=None, extra=''):
    """Write one instruction file holding a unique VERIFY-ID and a unique tag rule.

    fm: frontmatter dict; a separate FM-ID is placed inside it so we can tell
    whether frontmatter itself reached the model.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body_id = mp.add_id(path, label)
    tag = mp.add_tag(path)
    s = ''
    if fm is not None:
        fm_id = mp.add_id(path, label, kind='frontmatter')
        s += '---\n' + ''.join(f'{k}: {v}\n' for k, v in fm.items()) + f'note: "FM-ID {fm_id}"\n---\n'
    s += f'VERIFY-ID for this file: {body_id}\n'
    s += (rule or f'Always end every answer with the tag [TAG-{tag}]') + '\n' + extra
    path.write_text(s)
    return body_id


def git_init(d):
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '-q', str(d)], check=True)


def git_commit(d):
    subprocess.run('git add -A && git -c user.email=x@example.com -c user.name=x commit -qm init',
                   shell=True, cwd=d, check=False)


def append_jsonl(path, rec):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock, open(path, 'a') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

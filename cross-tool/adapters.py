"""Per-tool headless adapters.

Each adapter turns (mode, workspace, prompt) into a command line. Flags follow each tool's
official docs as of 2026-11 (see REQUIREMENTS.md section 9). CLIs change often: every flag can be
overridden with environment variables, and the exact command used is stored in every record.

Modes
  list      no tools (answer from context only)
  tools     read/write/edit/shell allowed (needed for trigger, hook and enforcement cases)
  flagdeny  read/shell allowed, write/edit denied by CLI flag

Environment overrides (per tool, TOOL = CORTEX | CLAUDE | CODEX | CURSOR | COPILOT)
  XTOOL_<TOOL>_BIN     executable path
  XTOOL_<TOOL>_MODEL   model name (omit to use the tool default; the record keeps what you set)
  XTOOL_<TOOL>_EXTRA   extra args, shell-split, appended before the prompt
"""
import json
import os
import shlex
import shutil
from pathlib import Path


def _bin(tool, *names):
    env = os.environ.get(f'XTOOL_{tool.upper()}_BIN')
    if env:
        return env
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return names[0]


def _model(tool):
    return os.environ.get(f'XTOOL_{tool.upper()}_MODEL')


def _extra(tool):
    return shlex.split(os.environ.get(f'XTOOL_{tool.upper()}_EXTRA', ''))


def _flag(tool, name):
    return os.environ.get(f'XTOOL_{tool.upper()}_{name}', '') in ('1', 'true', 'yes')


def answer_from_result_events(stdout):
    """stream-json / JSONL with a final {"type":"result","result":...} (CoCo, Claude Code, Cursor CLI)."""
    ans = None
    for ln in stdout.splitlines():
        try:
            j = json.loads(ln)
        except Exception:
            continue
        if isinstance(j, dict) and j.get('type') == 'result' and isinstance(j.get('result'), str):
            ans = j['result']
    return ans


def answer_generic(stdout):
    """Fallback for unknown JSONL: last string under common assistant-message keys."""
    last = None

    def walk(o):
        nonlocal last
        if isinstance(o, dict):
            role = str(o.get('role', '')) + str(o.get('type', ''))
            for k in ('text', 'content', 'message', 'result'):
                v = o.get(k)
                if isinstance(v, str) and ('assistant' in role or 'message' in role or 'result' in role):
                    last = v
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for ln in stdout.splitlines():
        try:
            walk(json.loads(ln))
        except Exception:
            continue
    return last


class Adapter:
    name = ''

    def version_cmd(self):
        return [self.bin(), '--version']

    def bin(self):
        raise NotImplementedError

    def build(self, mode, ws, prompt, tdir):
        """Return dict(cmd=[...], env={...}, cwd=..., answer_file=Path|None, log_dir=Path|None)."""
        raise NotImplementedError

    def answer(self, stdout, answer_file):
        if answer_file and Path(answer_file).exists():
            return Path(answer_file).read_text()
        return answer_from_result_events(stdout) or answer_generic(stdout)


class Cortex(Adapter):
    name = 'cortex'

    def bin(self):
        return _bin('cortex', 'cortex')

    def build(self, mode, ws, prompt, tdir):
        log = tdir / 'log'
        c = [self.bin(), 'exec', '--no-history', '--no-mcp', '--max-turns', '8', '--format', 'json']
        if not _flag('cortex', 'AUTOUPDATE'):
            c.insert(2, '--no-auto-update')   # otherwise the CLI may self-update mid-run (seen with 1.2.43 -> 1.2.44)
        if _model('cortex'):
            c += ['-m', _model('cortex')]
        allowed = {'list': [], 'tools': ['read', 'write', 'edit', 'bash'], 'flagdeny': ['read', 'bash']}[mode]
        for a in allowed:            # --allowed is variadic: repeat it and put -w before the prompt
            c += ['--allowed', a]
        if mode == 'flagdeny':
            c += ['--blocked', 'write', '--blocked', 'edit']
        c += ['-w', str(ws), *_extra('cortex'), prompt]
        env = {'CORTEX_ENABLE_MEMORY': 'false', 'COCO_LOG_DIR': str(log)}
        return dict(cmd=c, env=env, cwd=ws, answer_file=None, log_dir=log)


class Claude(Adapter):
    name = 'claude'
    ALL = 'Bash,Edit,Write,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch,Task'

    def bin(self):
        return _bin('claude', 'claude')

    def build(self, mode, ws, prompt, tdir):
        log = tdir / 'log'
        log.mkdir(parents=True, exist_ok=True)
        c = [self.bin(), '-p', '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
             '--debug-file', str(log / 'claude-debug.txt')]
        if _model('claude'):
            c += ['--model', _model('claude')]
        if mode == 'list':
            c += ['--disallowedTools', self.ALL]
        elif mode == 'tools':
            c += ['--allowedTools', 'Read,Edit,Write,Bash']
        else:
            c += ['--allowedTools', 'Read,Bash', '--disallowedTools', 'Edit,Write']
        c += [*_extra('claude'), prompt]
        env = {} if _flag('claude', 'AUTOUPDATE') else {'DISABLE_AUTOUPDATER': '1'}
        return dict(cmd=c, env=env, cwd=ws, answer_file=None, log_dir=log)


class Codex(Adapter):
    name = 'codex'

    def bin(self):
        return _bin('codex', 'codex')

    def build(self, mode, ws, prompt, tdir):
        log = tdir / 'log'
        log.mkdir(parents=True, exist_ok=True)
        ans = tdir / 'answer.txt'
        c = [self.bin(), 'exec', '--json', '--ephemeral', '--skip-git-repo-check', '-C', str(ws),
             '-o', str(ans), '-c', f'log_dir={log}']
        if _model('codex'):
            c += ['-m', _model('codex')]
        c += ['--sandbox', 'workspace-write' if mode == 'tools' else 'read-only']
        if _flag('codex', 'TRUST_HOOKS'):
            # Project hooks load only for trusted projects. Opt-in; recorded in every record.
            c += ['--dangerously-bypass-hook-trust']
        c += [*_extra('codex'), prompt]
        return dict(cmd=c, env={}, cwd=ws, answer_file=ans, log_dir=log)


class Cursor(Adapter):
    name = 'cursor'

    def bin(self):
        return _bin('cursor', 'agent', 'cursor-agent')

    def build(self, mode, ws, prompt, tdir):
        c = [self.bin(), '-p', '--output-format', 'stream-json', '--workspace', str(ws), '--trust']
        if _model('cursor'):
            c += ['--model', _model('cursor')]
        if mode != 'list' and _flag('cursor', 'FORCE'):
            # Headless shell commands may need --force (auto-approve). Opt-in; permissions.deny still applies per docs.
            c += ['--force']
        c += [*_extra('cursor'), prompt]
        return dict(cmd=c, env={}, cwd=ws, answer_file=None, log_dir=None)


class Copilot(Adapter):
    name = 'copilot'

    def bin(self):
        return _bin('copilot', 'copilot')

    def build(self, mode, ws, prompt, tdir):
        log = tdir / 'log'
        c = [self.bin(), '-p', prompt, '--output-format', 'json', '-C', str(ws), '--no-ask-user',
             '--log-dir', str(log), '--log-level', 'debug']
        if _model('copilot'):
            c += ['--model', _model('copilot')]
        if mode == 'list':
            c += ['--deny-tool=shell', '--deny-tool=write']
        elif mode == 'tools':
            c += ['--allow-tool=write', '--allow-tool=shell']
        else:
            c += ['--allow-tool=shell', '--deny-tool=write']
        c += _extra('copilot')
        return dict(cmd=c, env={}, cwd=ws, answer_file=None, log_dir=log)


ADAPTERS = {a.name: a for a in (Cortex(), Claude(), Codex(), Cursor(), Copilot())}

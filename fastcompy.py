import re
import keyword
import builtins
import sys as _sys
import os

__all__ = ["preprocess", "run_fastcompy_code", "run_fastcompy_file"]

# Gather all valid transformable names once
_kw = keyword.kwlist
_bi = [n for n in dir(builtins) if not n.startswith('_')]
_extra = ["os"]
_all = sorted(set(_kw + _bi + _extra))

# Precompiled single-regex for fastcompy.<name>
_fast_attr_rx = re.compile(r'\bfastcompy\.(' + '|'.join(map(re.escape, _all)) + r')\b')

# Precompile all fastcompy statement line prefixes
_stmt_rx = re.compile(r'^(\s*)fastcompy\s+(?=(?:' + '|'.join(map(re.escape, [
    "if", "elif", "else", "for", "while", "try", "except", "finally", "with", "def", "class"
])) + r')\b)')

def preprocess(src: str) -> str:
    """Quickly rewrite fastcompy DSL into pure Python code."""
    lines = src.splitlines()
    out = []
    for ln in lines:
        ln = _stmt_rx.sub(r'\1', ln)
        ln = _fast_attr_rx.sub(r'\1', ln)
        out.append(ln)
    return '\n'.join(out)

def run_fastcompy_code(code: str, filename='<string>'):
    exec(compile(preprocess(code), filename, 'exec'), {}, {})

def run_fastcompy_file(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        run_fastcompy_code(f.read(), path)

# Bind all builtins and extra modules into the fastcompy namespace
_self = _sys.modules[__name__]
for name in _all:
    if hasattr(builtins, name):
        setattr(_self, name, getattr(builtins, name))

# Add extra modules like os
_self.os = os

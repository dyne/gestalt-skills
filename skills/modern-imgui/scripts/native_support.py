# Copyright (c) 2026 Plan-B Foundation
# Copyright (c) 2026 Dyne.org foundation (adaptation)
# SPDX-License-Identifier: MIT
"""Owned temporary storage and artifact identities for optional native examples."""
import hashlib
import json
import os
from pathlib import Path
import tempfile

SKILL = Path(__file__).resolve().parents[1]

def evidence_directory(value):
    path = Path(value).resolve()
    if path == SKILL or SKILL in path.parents:
        raise ValueError('artifacts must remain outside the installed skill')
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path

def validated_scratch():
    # Ordinary operator execution has no managed owner packet. Preserve Python's
    # standard TMPDIR/TEMP/TMP/default selection in that case only.
    if 'GESTALT_SESSION_TMP_CONTEXT' not in os.environ:
        return Path(tempfile.gettempdir()).resolve()
    context = json.loads(os.environ['GESTALT_SESSION_TMP_CONTEXT'])
    required = ('directory', 'markerPath', 'ownerId', 'workspacePath')
    if not isinstance(context, dict) or any(not isinstance(context.get(k), str) or not context[k].strip() for k in required):
        raise ValueError('invalid managed scratch context')
    selected = os.environ.get('TMPDIR')
    if not selected or not selected.strip():
        raise ValueError('managed scratch requires TMPDIR')
    folder = Path(selected).resolve()
    if not folder.is_dir():
        raise ValueError('managed scratch directory is unavailable')
    marker = json.loads(Path(context['markerPath']).read_text())
    if not isinstance(marker, dict) or folder != Path(context['directory']).resolve() or marker.get('ownerId') != context['ownerId'] or marker.get('workspacePath') != context['workspacePath']:
        raise ValueError('disposable scratch ownership mismatch')
    return folder

def binary_identity(value):
    path = Path(value).resolve(strict=True)
    if not path.is_file() or not os.access(path, os.X_OK): raise ValueError('explicit executable required')
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}


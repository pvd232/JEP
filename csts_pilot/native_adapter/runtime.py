"""Explicit checkpoint identities for task-aware arms; no model is loaded here.

Execution engines, dtype, tokenizer files, software versions and tensor checks
belong to a separately frozen runtime receipt. BASE and IE remain distinct
checkpoint variants even though they share the same parser/prompt grammar.
"""

from __future__ import annotations

import copy
import hashlib

from .schema import encoded

PINNED_MODELS={
    'knowcoder_base':{'grammar':'knowcoder','model_id':'golaxy/KnowCoder-7B-base','revision':'4a7a076f573fe87fe0a97670c63c64214484742f','context_limit':2048},
    'knowcoder_ie':{'grammar':'knowcoder','model_id':'golaxy/KnowCoder-7B-IE','revision':'90ba076763dfb2e9efefd84a0e599f15ae533597','context_limit':2048},
    'gollie_7b':{'grammar':'gollie','model_id':'HiTZ/GoLLIE-7B','revision':'d3e41fef45f6a7d438c46ba7d9fce5d0d486c7a9','context_limit':16384},
}


def descriptor(alias):
    if alias not in PINNED_MODELS:raise ValueError('Unknown pinned model variant')
    return copy.deepcopy(PINNED_MODELS[alias])


def bind_runtime(alias,receipt):
    """Bind a caller's actual execution receipt; do not fabricate verification."""
    model=descriptor(alias)
    if receipt.get('model_id')!=model['model_id'] or receipt.get('revision')!=model['revision']:
        raise ValueError('Runtime checkpoint differs from its pinned variant')
    if receipt.get('tensor_load_verified') is not True:
        raise ValueError('Actual tensor loading must be verified by the runtime')
    for key in ('backend','dtype'):
        if not isinstance(receipt.get(key),str) or not receipt[key].strip():
            raise ValueError('A concrete runtime backend and dtype are required')
    for key in ('tokenizer_files_sha256','software_versions'):
        if not isinstance(receipt.get(key),dict) or not receipt[key]:
            raise ValueError('Tokenizer and software identities must be recorded')
    for digest in receipt['tokenizer_files_sha256'].values():
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Tokenizer files require SHA256 byte identities')
    if any(not isinstance(value,str) or not value or value.casefold() in {'latest','main','master'} for value in receipt['software_versions'].values()):
        raise ValueError('Software versions must be concrete')
    value={'alias':alias,'model':model,'runtime_receipt':copy.deepcopy(receipt)}
    return {**value,'runtime_sha256':hashlib.sha256(encoded(value)).hexdigest()}

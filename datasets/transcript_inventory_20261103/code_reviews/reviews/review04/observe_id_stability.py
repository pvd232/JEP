"""Run the historical ID generator with all writes intercepted in memory.

The only changed input is one source filename. No shared file is modified and
the observation contains file/record IDs only.
"""
import copy
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path('/workspace/scratch/8a7e64850a04')
WORK = ROOT / 'inventory_work'
SCRIPT = WORK / 'build_versiones_rows.py'
META = WORK / 'versiones_metadata.json'
OUT = Path(__file__).resolve().parent
original_read = Path.read_text
source = original_read(SCRIPT)
original_metadata = json.loads(original_read(META))


def run(metadata):
    """Execute actual generator source while replacing writes with a collector."""
    writes = {}

    def read(path, *args, **kwargs):
        return json.dumps(metadata) if path == META else original_read(path, *args, **kwargs)

    def write(path, text, *args, **kwargs):
        writes[str(path)] = text
        return len(text)

    with patch.object(Path, 'read_text', read), patch.object(Path, 'write_text', write), patch('builtins.print'):
        exec(compile(source, str(SCRIPT), 'exec'), {'__file__': str(SCRIPT), '__name__': 'review_only'})
    rows = json.loads(writes[str(WORK / 'versiones_rows_draft.json')])
    return {r['source_id']: r['unique_id'] for r in rows}


before = run(original_metadata)
changed_metadata = copy.deepcopy(original_metadata)
target = '1PN1Snb8AnIUiJtuykAqEc3KMGBbhvcrc'
for item in changed_metadata['files']:
    if item['id'] == target:
        item['title'] = 'AAA_' + item['title']
after = run(changed_metadata)
changed_ids = [{'source_file_id': fid, 'before': before[fid], 'after': after[fid]} for fid in before if before[fid] != after[fid]]
result = {'script': str(SCRIPT.relative_to(ROOT)), 'script_sha256': hashlib.sha256(source.encode()).hexdigest(), 'change': 'Prefix one existing canonical source title with AAA_; all Drive IDs and content unchanged', 'source_count_before': len(before), 'source_count_after': len(after), 'changed_record_ids': len(changed_ids), 'target': next(x for x in changed_ids if x['source_file_id'] == target), 'examples': changed_ids[:5], 'all_source_files_preserved': set(before) == set(after), 'filesystem_writes': 'All generator writes intercepted in memory'}
(OUT / 'id_stability_observations.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))

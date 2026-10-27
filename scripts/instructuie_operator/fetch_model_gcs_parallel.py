"""Fetch three immutable GCS objects concurrently, with disk reservations."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import time

from google.api_core.exceptions import NotFound
from google.cloud import storage

ROOT = Path('/home/machina/jep-instructuie-pilot-20261026')
MODEL = ROOT / 'model'
MANIFEST = json.loads((ROOT / 'relay-manifest.json').read_text())
PREFIX = 'jep/instructuie-pilot-20261026/model/' + MANIFEST['revision'] + '/'
MODEL.mkdir(exist_ok=True)
CLIENT = storage.Client()
BUCKET = CLIENT.bucket('mantra-mlfg-prod-uscentral1-8e7a')
SLOTS = 3
HEADROOM = 2 * 2**30


def emit(event, **fields):
    print(json.dumps({'event': event, **fields}), flush=True)


def identity(path, entry):
    if path.stat().st_size != entry['size_bytes']:
        return False
    with path.open('rb') as stream:
        if entry.get('sha256'):
            return hashlib.file_digest(stream, 'sha256').hexdigest() == entry['sha256']
        digest = hashlib.sha1(f"blob {entry['size_bytes']}\0".encode())
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
        return digest.hexdigest() == entry['git_blob_sha1']


class TransferWriter:
    """Compute the manifest hash during the CRC32C-checked download."""
    def __init__(self, stream, entry):
        self.stream, self.entry = stream, entry
        self.reset()

    def reset(self):
        self.digest = hashlib.sha256() if self.entry.get('sha256') else hashlib.sha1(
            f"blob {self.entry['size_bytes']}\0".encode())

    def write(self, data):
        if self.stream.tell() + len(data) > self.entry['size_bytes']:
            raise RuntimeError('Transfer exceeds manifest length')
        count = self.stream.write(data)
        self.digest.update(data[:count])
        if count != len(data):
            raise IOError('Short disk write')
        return count

    def seek(self, offset, whence=0):
        if whence == 0 and offset == 0:
            result = self.stream.seek(0)
            self.reset()
            return result
        if whence == 0 and offset == self.stream.tell():
            return offset
        raise RuntimeError('Unexpected transfer seek')

    def __getattr__(self, name):
        return getattr(self.stream, name)


def download(entry, object_name, generation):
    target = MODEL / entry['name']
    temporary = target.with_name(target.name + '.part')
    pinned = BUCKET.blob(object_name, generation=generation)
    started = time.monotonic()
    with temporary.open('xb') as stream:
        writer = TransferWriter(stream, entry)
        pinned.download_to_file(writer, if_generation_match=generation,
                                checksum='crc32c', timeout=120)
        actual = writer.digest.hexdigest()
    expected = entry.get('sha256') or entry['git_blob_sha1']
    if temporary.stat().st_size != entry['size_bytes'] or actual != expected:
        raise RuntimeError('Downloaded file identity differs: ' + entry['name'])
    temporary.rename(target)
    return {'entry': entry, 'generation': generation, 'object': object_name,
            'status': 'verified', 'seconds': time.monotonic() - started}


def persist(path, value):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


receipts_file = ROOT / 'model-download-receipts.json'
receipts = json.loads(receipts_file.read_text()) if receipts_file.exists() else []
pending = []
for entry in MANIFEST['files']:
    target = MODEL / entry['name']
    if target.exists():
        if not identity(target, entry):
            raise RuntimeError('Existing local file differs: ' + str(target))
        emit('existing_verified', name=entry['name'])
    else:
        temporary = target.with_name(target.name + '.part')
        if temporary.exists():
            raise RuntimeError('Partial file requires inspection: ' + str(temporary))
        pending.append(entry)

# Written blocks already reduce filesystem free space. Reserve the remaining
# allocation once, with headroom for concurrent writes and accounting delays.
active = {}
deadline = time.monotonic() + 4 * 60 * 60
with ThreadPoolExecutor(max_workers=SLOTS) as pool:
    while pending or active:
        if time.monotonic() > deadline:
            raise TimeoutError('Checkpoint transfer exceeded four hours')
        changed = False
        for future in list(active):
            if not future.done():
                continue
            entry = active.pop(future)
            receipt = future.result()
            receipts = [r for r in receipts if r['entry']['name'] != entry['name']]
            receipts.append(receipt)
            persist(receipts_file, receipts)
            emit('download_verified', name=entry['name'], seconds=receipt['seconds'])
            changed = True
        for entry in pending[:]:
            if len(active) >= SLOTS:
                break
            reserved = 0
            for item in active.values():
                partial = MODEL / (item['name'] + '.part')
                try:
                    allocated = partial.stat().st_blocks * 512
                except FileNotFoundError:
                    try:
                        allocated = (MODEL / item['name']).stat().st_blocks * 512
                    except FileNotFoundError:
                        allocated = 0
                reserved += max(0, item['size_bytes'] - allocated)
            if shutil.disk_usage(ROOT).free < reserved + entry['size_bytes'] + HEADROOM:
                continue
            blob = BUCKET.blob(PREFIX + entry['name'])
            try:
                blob.reload(timeout=30)
            except NotFound:
                continue
            if blob.size != entry['size_bytes']:
                continue
            generation = int(blob.generation)
            emit('download_start', name=entry['name'], bytes=blob.size,
                 generation=generation, active=len(active) + 1,
                 reservation_bytes=reserved + entry['size_bytes'])
            future = pool.submit(download, entry, blob.name, generation)
            active[future] = entry
            pending.remove(entry)
            changed = True
        if not changed:
            time.sleep(3)
# Existing files were hashed above; every newly fetched file passed CRC32C,
# manifest byte length and SHA verification before its receipt was persisted.
if any(not (MODEL / entry['name']).exists() for entry in MANIFEST['files']):
    raise RuntimeError('Manifest incomplete')
persist(ROOT / 'model-ready.json', MANIFEST)
emit('complete', model_id=MANIFEST['model_id'], revision=MANIFEST['revision'],
     files=len(MANIFEST['files']))

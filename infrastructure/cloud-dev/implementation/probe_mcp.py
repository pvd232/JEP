#!/usr/bin/python3
"""Exercise the real stdio transport with fresh server processes."""
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading

config = Path(os.environ.get('CLOUD_DEV_CONFIG', '/etc/cloud-dev/profile.json'))
profile = json.loads(config.read_text())
server = subprocess.Popen([str(Path(profile['paths']['install_root']) / 'bin/cloud-mcp')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
messages = queue.Queue()


def read():
    for line in server.stdout:
        try:
            messages.put(json.loads(line))
        except ValueError:
            pass


threading.Thread(target=read, daemon=True).start()


def call(identifier, method, params):
    server.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': identifier, 'method': method, 'params': params}) + '\n')
    server.stdin.flush()
    while True:
        message = messages.get(timeout=60)
        if message.get('id') == identifier:
            if 'error' in message:
                raise RuntimeError(message['error'])
            return message['result']


try:
    initialized = call(1, 'initialize', {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'cloud-dev-acceptance', 'version': '1.0'}})
    assert profile['target']['vm_name'] in initialized['instructions']
    server.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n')
    server.stdin.flush()
    tools = call(2, 'tools/list', {})['tools']
    names = [tool['name'] for tool in tools]
    for name in ['start_process', 'read_file', 'write_file']:
        assert name in names, names
    disposable = Path(profile['paths']['state_root']) / 'receipts/mcp-roundtrip.txt'
    write = call(3, 'tools/call', {'name': 'write_file', 'arguments': {'path': str(disposable), 'content': 'cloud-dev MCP roundtrip verified\n', 'mode': 'rewrite'}})
    assert not write.get('isError'), write
    read_result = call(4, 'tools/call', {'name': 'read_file', 'arguments': {'path': str(disposable)}})
    assert not read_result.get('isError'), read_result
    assert 'cloud-dev MCP roundtrip verified' in json.dumps(read_result)
    process = call(5, 'tools/call', {'name': 'start_process', 'arguments': {'command': 'hostname; id -un; pwd', 'timeout_ms': 1000}})
    assert not process.get('isError'), process
    result = {'initialize': 'passed', 'tool_count': len(tools), 'write_read_roundtrip': 'passed', 'identity': process, 'server_info': initialized.get('serverInfo'), 'routing_instructions': initialized['instructions'][:900]}
    print(json.dumps(result, indent=2))
finally:
    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()

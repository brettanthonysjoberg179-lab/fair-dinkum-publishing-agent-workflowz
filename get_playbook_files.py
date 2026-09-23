#!/usr/bin/env python3
"""Pull AU AI Compliance Playbook outlines from Google Drive and assemble manuscript."""
import json, subprocess, os

COMPOSIO = '/home/brettanthonysjoberg179/.local/bin/composio'

def execute(slug, params):
    cmd = [COMPOSIO, 'execute', slug, '-d', json.dumps(params)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        if 'outputFilePath' in data:
            with open(data['outputFilePath']) as f:
                return json.load(f)
        return data
    return None

# Get files in AU AI Compliance Playbook/02_Assets
r = execute('GOOGLEDRIVE_LIST_CHILDREN_V2', {'folderId': '12VM9Srn4FO-tP9aWVmjsxkjcAA2teCso', 'fields': 'id,name,mimeType'})
files = r['data'].get('files', [])
print(f'Files in 02_Assets: {len(files)}')
for f in files:
    print(f'  {f["name"][:60]} | {f["mimeType"][:25]} | {f["id"][:15]}')

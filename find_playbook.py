#!/usr/bin/env python3
"""Find all files related to AU AI Compliance Playbook."""
import json, subprocess

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

# Get all files
all_files = []
page_token = None
while True:
    params = {'pageSize': 200, 'fields': 'id,name,mimeType,parents'}
    if page_token:
        params['pageToken'] = page_token
    r = execute('GOOGLEDRIVE_LIST_FILES', params)
    if not r:
        break
    data = r.get('data', r)
    files = data.get('files', [])
    all_files.extend(files)
    next_token = data.get('nextPageToken')
    if not next_token:
        break
    page_token = next_token

# Find files with AU AI in name or with AU AI folder as parent
au_ai_keywords = ['AU AI Compliance', 'Privacy Act', 'MUBWL', 'MUBWGMBO', 'MUBW98ES', 'MUBW5IN2', 'MUBVXA87']
au_ai_files = []
for f in all_files:
    name = f.get('name', '')
    if any(kw in name for kw in au_ai_keywords):
        au_ai_files.append(f)

print(f'AU AI Compliance Playbook related files: {len(au_ai_files)}')
for f in au_ai_files:
    print(f'  {f["name"][:60]} | {f["id"][:15]}... | parents: {len(f.get("parents", []))}')

#!/usr/bin/env python3
"""Download content from AU AI Compliance Playbook Google Docs."""
import json, subprocess, os

COMPOSIO = '/home/brettanthonysjoberg179/.local/bin/composio'

def execute(slug, params):
    cmd = [COMPOSIO, 'execute', slug, '-d', json.dumps(params)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        if 'outputFilePath' in data:
            with open(data['outputFilePath']) as f:
                return json.load(f)
        return data
    return None

out_dir = '/home/brettanthonysjoberg179/fair-dinkum-publishing-agent-workflowz/outputs/au-ai-compliance-playbook'
os.makedirs(out_dir, exist_ok=True)

# Download the AU AI Compliance Playbook outline as plain text
fid = '1Tul2FGifi-FFLRCcZ7WPBc-8HfZ6cC7yrJxbzf_NWx4'
r = execute('GOOGLEDRIVE_DOWNLOAD_FILE', {
    'fileId': fid,
    'mime_type': 'text/plain'
})

print('Response structure:')
print(json.dumps(r, indent=2)[:2000] if r else 'None')

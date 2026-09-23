#!/usr/bin/env python3
"""Download all AU AI Compliance Playbook content from Google Drive."""
import json, subprocess, os, urllib.request

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

# All outline documents to download
outlines = [
    ('1Tul2FGifi-FFLRCcZ7WPBc-8HfZ6cC7yrJxbzf_NWx4', 'AU AI Compliance Playbook'),
    ('1JFYw7XJ26CxBZemyA1hyUqcL3eIXelSaZF73XdbtChc', 'AU AI Compliance Playbook v2'),
    ('1WbXmx9LRo5wbZbs9B1PVvAtAybWtmpdZzpbiJU0oWcg', 'AU AI Compliance Playbook v3'),
    ('1mcJ1Vp2IFSjwRHfV1MpoAhY7XNzArWP2f2LIeOD9P54', 'AU AI Compliance Playbook v4'),
    ('1KCCRLLiftjzlx6QBxqm1Q9rP3viUk64_DYI0DdlDDX0', 'AU AI Compliance Playbook v5'),
    ('1V91DydnmxNcaQRCw0nNi3v0p7uIgGqRYgUkacpDOLPE', 'AU AI Compliance Playbook v6'),
    ('14-kP9g0Q3ARo7B1DmUUrgHqFM4-fXTLWP4O_W3hXAu0', 'AU AI Compliance Playbook v7'),
]

for fid, label in outlines:
    print(f'\nDownloading: {label}...')
    r = execute('GOOGLEDRIVE_DOWNLOAD_FILE', {
        'fileId': fid,
        'mime_type': 'text/plain'
    })
    
    if r and r.get('successful'):
        data = r.get('data', {})
        download_info = data.get('downloaded_file_content', {})
        s3_url = download_info.get('s3url', '')
        
        if s3_url:
            try:
                req = urllib.request.Request(s3_url)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    content = resp.read().decode('utf-8')
                    safe_name = label.replace(' ', '_').replace('/', '_')[:40]
                    outfile = f'{out_dir}/{safe_name}.txt'
                    with open(outfile, 'w') as f:
                        f.write(content)
                    print(f'  Saved: {outfile} ({len(content)} chars)')
            except Exception as e:
                print(f'  Download failed: {e}')
        else:
            print(f'  No download URL found')
    else:
        print(f'  Failed: {r}')

print('\n=== ALL DOWNLOADS COMPLETE ===')

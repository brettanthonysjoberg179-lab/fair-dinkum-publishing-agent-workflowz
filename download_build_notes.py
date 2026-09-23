#!/usr/bin/env python3
"""Download build-notes.txt files — they likely contain the actual manuscript content."""
import json, subprocess, os, urllib.request

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

out_dir = '/home/brettanthonysjoberg179/fair-dinkum-publishing-agent-workflowz/outputs/au-ai-compliance-playbook'
os.makedirs(out_dir, exist_ok=True)

# Build notes file IDs (from earlier audit)
build_notes_ids = [
    '1TL8KaRg2Rf6FWcgfaOrGh75WpWO1cfgV',  # FDP-FDP-MUBWL871-build-notes.txt
    '1CBiFYhNrlFboMWzfG2YdPUv6iwsGpTCv',  # FDP-FDP-MUBWGMBO-build-notes.txt
    '1jsFxDiwsQy1zUUw1NRpMjg0PRemMx1yo',  # FDP-FDP-MUBW98ES-build-notes.txt
    '1vXwqSx2dofd39LgWxPe26G8vOZy6yO6u',  # FDP-FDP-MUBW5IN2-build-notes.txt
    '1ScQTEExPzsl46yR_u8LjXVMIfd_GcFPg',  # FDP-FDP-MUBVXA87-build-notes.txt
    '1nPWE0J5LA_UnNYKIJIUeBlPazsm6aBUx',  # FDP-FDP-MUBVUKCA-build-notes.txt
    '1Fo3toZbIOjKVg8Qxj3LuEquL7vsUDheP',  # FDP-FDP-MUBVR2V7-build-notes.txt
    '1kqOlxP5aX3bkyTZVQNJrtbNhUh8t0Aon',  # FDP-FDP-MUBVHTRD-build-notes.txt
    '14y-_uYJ5FQ2dV28BJ4J8YL93Vs5eYt9t',  # FDP-FDP-MUBVHIV1-build-notes.txt
    '1NRmbJ8ZZ-A09w750VKi9gt35WIDOr13R',  # FDP-FDP-MUBVH2FI-build-notes.txt
    '1xVwFBV3zGNQFtO1Tr1L2lAdvtD0ht42G',  # FDP-FDP-MUAYSDRK-build-notes.txt
    '19fAZo0MFwWcmlgdGAqq_yAYuPxWivarj',  # FDP-FDP-MUAY5U64-build-notes.txt
    '1AZXGvVRN6sleQ_mHprubHYDZimNo6Xb8',  # FDP-FDP-MUAXLETF-build-notes.txt
    '16qVkAjap-kq28T94hI8GeBkjj6oRM5nf',  # FDP-FDP-MUAX4VVY-build-notes.txt
]

for fid in build_notes_ids:
    print(f'\nDownloading build-notes: {fid[:12]}...')
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
                    name = data.get('name', f'build_notes_{fid[:8]}')
                    safe_name = name.replace(' ', '_').replace('/', '_').replace(':', '')[:50]
                    outfile = f'{out_dir}/{safe_name}.txt'
                    with open(outfile, 'w') as f:
                        f.write(content)
                    print(f'  Saved: {outfile} ({len(content)} chars)')
            except Exception as e:
                print(f'  Failed: {e}')
        else:
            print(f'  No URL')
    else:
        print(f'  Failed request')

print('\n=== BUILD NOTES DOWNLOADED ===')

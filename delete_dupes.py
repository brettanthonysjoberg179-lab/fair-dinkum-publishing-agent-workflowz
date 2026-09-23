#!/usr/bin/env python3
"""Delete duplicate files from My Drive root level."""
import json
import subprocess

COMPOSIO = "/home/brettanthonysjoberg179/.local/bin/composio"

def execute(slug, params):
    # Pass JSON as stdin to avoid shell quoting issues
    input_data = json.dumps(params)
    cmd = [COMPOSIO, "execute", slug, "-d", input_data]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        # Handle case where output is stored in file
        if 'outputFilePath' in data:
            try:
                with open(data['outputFilePath']) as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading output file: {e}")
                return None
        return data
    print(f"  STDERR: {result.stderr[:300]}")
    return None

# Get all files with their parents
all_files = []
page_token = None
page = 0
while True:
    params = {"pageSize": 100, "fields": "id,name,mimeType,parents", "q": "trashed=false"}
    if page_token:
        params["pageToken"] = page_token
    
    r = execute("GOOGLEDRIVE_LIST_FILES", params)
    if not r:
        print("Failed to list files")
        exit(1)
    
    # Extract files from response
    if 'data' in r:
        data = r['data']
    elif 'files' in r:
        data = r
    else:
        print(f"Unexpected response format: {list(r.keys())}")
        exit(1)
    
    files = data.get('files', [])
    all_files.extend(files)
    page += 1
    print(f"Page {page}: {len(files)} files (total: {len(all_files)})")
    
    next_token = data.get('nextPageToken')
    if not next_token or len(all_files) >= 500:
        break
    page_token = next_token

files = all_files
print(f"Total files: {len(files)}")

# Group by name
by_name = {}
for f in files:
    name = f['name']
    if name not in by_name:
        by_name[name] = []
    by_name[name].append(f)

# Identify duplicates
dupes = {}
for name, items in by_name.items():
    if len(items) > 1:
        dupes[name] = items

print(f"Found {len(dupes)} names with duplicates")
for name, items in dupes.items():
    print(f"  {name}: {len(items)} copies")

# Delete files that have fewer parents (loose root copies)
deleted = 0
for name, items in dupes.items():
    # Keep the file with the most parents (likely the organized one)
    items.sort(key=lambda x: len(x.get('parents', [])), reverse=True)
    to_delete = items[1:]
    
    for f in to_delete:
        # Only delete if it's not a folder
        if f.get('mimeType') == 'application/vnd.google-apps.folder':
            continue
        print(f"Deleting: {name} (ID: {f['id'][:12]}...)")
        r = execute("GOOGLEDRIVE_DELETE_FILE", {"fileId": f['id']})
        if r and r.get('successful'):
            print(f"  OK")
            deleted += 1
        else:
            print(f"  FAILED: {r}")

print(f"\n=== DELETED {deleted} duplicate files ===")

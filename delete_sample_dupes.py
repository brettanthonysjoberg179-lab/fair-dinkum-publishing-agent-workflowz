#!/usr/bin/env python3
"""Delete remaining duplicate 03-sample.pdf files."""
import json
import subprocess

COMPOSIO = "/home/brettanthonysjoberg179/.local/bin/composio"

def execute(slug, params):
    input_data = json.dumps(params)
    cmd = [COMPOSIO, "execute", slug, "-d", input_data]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        if 'outputFilePath' in data:
            with open(data['outputFilePath']) as f:
                return json.load(f)
        return data
    print(f"STDERR: {result.stderr[:200]}")
    return None

# Find 03-sample.pdf files
r = execute("GOOGLEDRIVE_FIND_FILE", {"q": "name='03-sample.pdf' and trashed=false"})
files = r['data']['files']
print(f"Found {len(files)} copies of 03-sample.pdf")

# Keep first, delete rest
for f in files[1:]:
    print(f"Deleting: {f['id']}")
    execute("GOOGLEDRIVE_DELETE_FILE", {"fileId": f['id']})

print("Done")

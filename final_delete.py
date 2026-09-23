#!/usr/bin/env python3
"""Delete remaining duplicate files."""
import json
import subprocess

COMPOSIO = "/home/brettanthonysjoberg179/.local/bin/composio"

def execute(slug, params):
    input_data = json.dumps(params)
    cmd = [COMPOSIO, "execute", slug, "-d", input_data]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        if 'outputFilePath' in data:
            try:
                with open(data['outputFilePath']) as f:
                    return json.load(f)
            except:
                return None
        return data
    print(f"  STDERR: {result.stderr[:300]}")
    return None

# Remaining duplicates to delete (from previous run analysis)
to_delete = [
    # 01-gumroad-package.zip duplicates (keep 1mUDlzPS5GGgBb_A40kV2ziAIXmP2XZZi)
    "1UP42ciAG515P8ItYDj9QDyZkGcmst8aZ",
    "1V0nBoa2dmNZZjlK-v-eQI1EJxlyVoz5m",
    "1HE1T1tdAfSgLGrRl2xMNKT6Gb1T6F98R",
    "10tsoa2hV69rW5HftIApMFGYuB4NjGELn",
    "1ynrMNEsgC5JozQSCfgkmALmdFqfjlxEa",
    # 03-sample.pdf duplicate (keep 1c6YEq7dlf6RDk1Ck6oXfxxNM2pE6bMOp)
    "19qKhXJCIWJKGw_Wi2b0H8sAZIqeGsSMm",  # this is the zip version
    # Aussie Agent Workflowz outline duplicate
    "1mwUS8C_ziFG2R2ra6k5KslSx2MZuqdwez8gp70tXJpo",
]

deleted = 0
for fid in to_delete:
    print(f"Deleting: {fid[:12]}...")
    r = execute("GOOGLEDRIVE_DELETE_FILE", {"fileId": fid})
    if r and r.get('successful'):
        print(f"  OK")
        deleted += 1
    else:
        print(f"  FAILED: {r}")

print(f"\n=== DELETED {deleted} files ===")

# Verify remaining files
print("\nRemaining files in root:")
r = execute("GOOGLEDRIVE_LIST_FILES", {"pageSize": 100, "fields": "id,name,mimeType,parents", "q": "trashed=false"})
if r:
    files = r.get('data', r).get('files', [])
    for f in files:
        print(f"  {f['name'][:60]}")

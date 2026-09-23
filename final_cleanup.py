#!/usr/bin/env python3
"""Final cleanup: move remaining loose files to _TO_REVIEW folder."""
import json
import subprocess

COMPOSIO = "/home/brettanthonysjoberg179/.local/bin/composio"
FD_ROOT = "15NdCCsLDHbkv4-gMAWUxmculVSjmJVb-"

def execute(slug, params):
    cmd = [COMPOSIO, "execute", f'"{slug}"', "-d", json.dumps(params)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode == 0 and result.stdout.strip():
        return json.loads(result.stdout)
    print(f"  Failed: {result.stdout[:200]}")
    return None

# Create _TO_REVIEW folder
print("Creating _TO_REVIEW folder...")
r = execute("GOOGLEDRIVE_CREATE_FOLDER", {"name": "_TO_REVIEW", "parentId": FD_ROOT})
if r and r.get("successful"):
    review_id = r["data"]["id"]
    print(f"  Created: {review_id}")
else:
    print("  Failed to create folder")
    exit(1)

# List current root-level files
print("\nListing current root files...")
r = execute("GOOGLEDRIVE_LIST_CHILDREN_V2", {"folderId": FD_ROOT, "fields": "id,name,mimeType"})
if not r or not r.get("successful"):
    print("  Failed to list files")
    exit(1)

files = r["data"].get("files", [])
print(f"  Found {len(files)} items in Fair Dinkum Publishing root")

# Move non-folder, non-original files to _TO_REVIEW
# Keep: 01_Products, 02_Marketing_Collateral, 03_Brand_Assets, _TO_REVIEW
keep_names = ["01_Products", "02_Marketing_Collateral", "03_Brand_Assets", "_TO_REVIEW"]
moved = 0
for f in files:
    if f["name"] in keep_names:
        continue
    if f.get("mimeType") == "application/vnd.google-apps.folder":
        continue
    # Move to review
    r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": f["id"], "id": review_id, "supportsAllDrives": True})
    if r and r.get("successful"):
        print(f"  Moved to review: {f['name'][:50]}")
        moved += 1

print(f"\n=== MOVED {moved} files to _TO_REVIEW ===")
print("Files remaining in root:")
for f in files:
    if f["name"] not in keep_names:
        print(f"  {f['name'][:60]}")

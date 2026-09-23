#!/usr/bin/env python3
"""Google Drive cleanup script using Composio CLI."""
import json
import subprocess

COMPOSIO = "/home/brettanthonysjoberg179/.local/bin/composio"

def execute(slug, params):
    cmd = [COMPOSIO, "execute", f'"{slug}"', "-d", json.dumps(params)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode == 0 and result.stdout.strip():
        return json.loads(result.stdout)
    print(f"  Failed: {result.stdout[:200]}")
    return None

FD_ROOT = "15NdCCsLDHbkv4-gMAWUxmculVSjmJVb-"
MARKETING = "1gATkssRxKGUI-so79OISIv87j1EaWdhf"

# 1. Move marketing files to 02_Marketing_Collateral
print("Moving marketing files...")
r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": "1mxLaHXGFmLpKaWztE9UgZ_cnMawdIi1i", "id": MARKETING, "supportsAllDrives": True})
if r and r.get("successful"):
    print("  Moved: 100 AI Prompts.pdf")

r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": "1YgA90v6NXHxj_AssS_BIzwdmjYcT8aij5q_NDoje7OY", "id": MARKETING, "supportsAllDrives": True})
if r and r.get("successful"):
    print("  Moved: Business Plan")

# 2. Move QA/README to root FDP
print("Moving loose files...")
r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": "1LeLcY5cekt73dO2V0BYdh2FHlHKpwmE8", "id": FD_ROOT, "supportsAllDrives": True})
if r and r.get("successful"):
    print("  Moved: CUSTOMER_DELIVERY_PACKAGE_README.md")

r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": "16sLU38k1zEvY88MkJk1Hxr_XRDVASpu7", "id": FD_ROOT, "supportsAllDrives": True})
if r and r.get("successful"):
    print("  Moved: LAUNCH_QA_RECORD_001.md")

# 3. Move the 03-sample.pdf.zip to marketing
r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": "19qKhXJCIWJKGw_Wi2b0H8sAZIqeGsSMm", "id": MARKETING, "supportsAllDrives": True})
if r and r.get("successful"):
    print("  Moved: 03-sample.pdf.zip")

print("\n=== MOVES COMPLETE ===")
print("Remaining root files should now be:")
print("  - Fair Dinkum Publishing/ (root folder)")
print("  - 03-sample.pdf (1 original)")
print("  - 02-ebook.pdf (1 original)")
print("  - 01-gumroad-package.zip (1 original)")
print("  - FDP-FDP-* folders")
print("  - Draft chapters")

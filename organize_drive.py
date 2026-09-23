#!/usr/bin/env python3
"""Organize FDP folders and draft chapters into product structure."""
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

# Product folder IDs
AU_AI_COMP = "1bLHR3EP_bSGTe8X19R6XJoIzbeA9cYkB"
SOLOPRENEUR = "1brBG5KNehuvR7yy_dEmNCIITeLDHyBBv"
AUSSIE_AGENT = "1n_vgoN2q1cjB3kTASYON6Ubs79GfzIdX"
GRAFFITI = "1ijR3Eztcpx3Jvc6EzymB0o8M4Zcdr3hC"
SKATEBOARDING = "1MKSIWkwpbcC1qunv-GHKJvjGPXw1A3ND"

# FDP folders that contain "AU AI Compliance Playbook" outlines
# These should go to AU_AI_Compliance_Playbook/02_Assets/
au_ai_folders = [
    "1Y86T0BUeIk9IrL72K56Ls0PsMauX084q",  # FDP-FDP-MUBWL871
    "1ARHUxaC3J80zwkT3OyWCDK2EPXoNUT0z",  # FDP-FDP-MUBWGMBO
    "1jEb7bPWFOAa3UsC_ontK3HbM6ygEDFBo",  # FDP-FDP-MUBW98ES
    "1yPguMCmkHbIP1fi8WfFf-jixSZUlDydw",  # FDP-FDP-MUBW5IN2
    "1PAlI6Z9pliiCq5ibVphVznU0GI0xBBC8",  # FDP-FDP-MUBVXA87
    "1zQNQD6iKbmlRTJnj4-ODqlPl3TDvZMK3",  # FDP-FDP-MUBVUKCA
    "1dKDXPMxytw8z-9uETbcU3y2G-rfVPVgj",  # FDP-FDP-MUBVR2V7
    "1zKDldCRvxaQICAmiZ5QBpwU5TVxrupat",  # FDP-FDP-MUBVDKB5
    "1vUcImvOLmU999n3d65O2EONd0ph3BqK9",  # FDP-FDP-MUBVD0YH
    "1oh1khUZkDmJwjr8l4u_saopSks1lzQeQ",  # FDP-FDP-MUBVC0GK
    "1a3dKeRlVsAyz5h3jP8ZbZZyYz9t23x7Q",  # FDP-FDP-MUBVBGF8
    "13D4d9tPpPhIn8UEfDphXbXpzusUhATk3",  # FDP-FDP-MUBVATAZ
    "1VA4bmBPavfp8v7HjD3faPCfuvrPwIiwE",  # FDP-FDP-MUBVA2O9
]

print("Moving AU AI Compliance Playbook folders to 02_Assets...")
for fid in au_ai_folders:
    r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": fid, "id": f"{AU_AI_COMP}/02_Assets", "supportsAllDrives": True})
    if r and r.get("successful"):
        print(f"  Moved: {fid[:12]}...")

# Move AU AI outlines to 02_Assets
au_ai_outlines = [
    "1Tul2FGifi-FFLRCcZ7WPBc-8HfZ6cC7yrJxbzf_NWx4",
    "1JFYw7XJ26CxBZemyA1hyUqcL3eIXelSaZF73XdbtChc",
    "1WbXmx9LRo5wbZbs9B1PVvAtAybWtmpdZzpbiJU0oWcg",
    "1mcJ1Vp2IFSjwRHfV1MpoAhY7XNzArWP2f2LIeOD9P54",
    "1KCCRLLiftjzlx6QBxqm1Q9rP3viUk64_DYI0DdlDDX0",
    "1V91DydnmxNcaQRCw0nNi3v0p7uIgGqRYgUkacpDOLPE",
    "14-kP9g0Q3ARo7B1DmUUrgHqFM4-fXTLWP4O_W3hXAu0",
    "1FOUsqnyZpTni3DcCL-EeUVxUdn9G1_aMtF7ZWFjmFEg",
    "1sNdj0--ZDhFLGW4yypfhwZMRdIW-bDZ0gerpx1OzfD4",
    "1VYYcg8mxjT0v4zea6TKzU5R4z5yx9x7fFBgqpFJTNOo",
    "17JzfZyBzn_upaYiDeTnqUo5D1RR8QLdawgmejk-EMe4",
    "1KLfC_L17lyYXIiorLKOQUF-Z3AOc7zsQ9pjE_MzQE3A",
    "11J2kZFDo3obcwKHWDnupsGDerNiNmwjCFKSyhJ5rLvI",
]

print("\nMoving AU AI outlines to 02_Assets...")
for fid in au_ai_outlines:
    r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": fid, "id": f"{AU_AI_COMP}/02_Assets", "supportsAllDrives": True})
    if r and r.get("successful"):
        print(f"  Moved outline: {fid[:12]}...")

# Move draft chapters to Aussie_Agent_Workflowz/01_Drafts/
draft_chapters = [
    "1juudDcwTfZO6sUEyOIBY0sger8bNYVzXTEVh9mOBrq0",  # Draft: Table of Contents
    "1DVsKkkay0O3nwmbdbaHBXw9Pk1FX209rAQxqz1RZA-0",  # Draft: Copyright Page
    "1Qfo3rwApZqBEpp9MCtQ7On10ihXLn0Uh9k6d8I6rA5g",  # Draft: Chapter 2
    "13XpYffcxdA7D5d0Fl2yfCyt0KLOF9TfDJQantoGaoHM",  # Draft: Chapter 1
    "1CnH8y2LiYndhxLxM75dF5sCuklVAxR6M6OfqFB6ognk",  # Draft: Conclusion
    "1gH1REoThqNSix-N5ZPzU_smQTZTi8FpYc_7w3kx-6Ls",  # Draft: Chapter 11
    "1x2-jjf_NUd6ITpc0eWVH1fIzGRISy9KqsKXf4VlSBlA",  # Draft: Chapter 10
    "19kdOz_MZ4R3H9sEbxdUpyJ8jgQIaO3D_mIsGd72IrIg",  # Draft: Chapter 9
    "14ag2DpZugIR24Oe1zZgEIHCL_tkTm0CBZX8FeXHFsTA",  # Draft: Chapter 8
    "1WCcizOKtFCrQeypUdewIsb733YJXZdZNbHDmHrKZ46Y",  # Draft: Chapter 7
    "1bef1QnxHswBcaG0UK8K_cIXag4QWrzGuo6W9aHhR320",  # Draft: Chapter 6
    "1Oeu_J38Ds3X2tpxvfs7WcmfhE2FOolQ0wDPfOlKRtfI",  # Draft: Chapter 5
    "13SBQ6khxjgxkZ3c0tOkMEtsrxqbjcEJyWkKsaEWJlJk",  # Draft: Chapter 4
    "1RWuEs3RFUkTnxDweHnUjoSOZ9bvH1yo1s3LsH8QKMDw",  # Draft: Chapter 3
]

print("\nMoving draft chapters to Aussie_Agent_Workflowz/01_Drafts...")
for fid in draft_chapters:
    r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": fid, "id": f"{AUSSIE_AGENT}/01_Drafts", "supportsAllDrives": True})
    if r and r.get("successful"):
        print(f"  Moved draft: {fid[:12]}...")

# Move outlines and other docs to Aussie_Agent_Workflowz/02_Assets/
aussie_assets = [
    "1fNM5uak336-OWddkvA4ZeNQ3edAY2hpmKBaeYMsQfNc",  # Agentic Workflow Automation - SEO Optimized Outline
    "192vJRC62ZOevnvRwe_rQdfPL8fN5_4sMW9Q4BVRlxwk",  # Ebook Outline - Building Agentic Automated Workflows
    "1X0C-rWPXbuRRcRfs0EGGZOrBRrjf5K9UWsJ-VjppUTI",  # Ebook Chapter - Refined Manually
    "1N8CSYdGC7SAq-Fc4g7ogs9Xxc4tZA5OzfdMQ6UGDaRk",  # Ebook Draft - Research Data
    "13Z7xDdI2W6egLHTz9gnffsCwTmOfXISLGUjkKYUxOn4",  # [FDP outline] Aussie Agent Workflowz
    "1mwUS8C_ziFG2R2ra6k5KslSx2MZuqdwez8gp70tXJpo",  # [FDP outline] Aussie Agent Workflowz (dup)
]

print("\nMoving outlines to Aussie_Agent_Workflowz/02_Assets...")
for fid in aussie_assets:
    r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": fid, "id": f"{AUSSIE_AGENT}/02_Assets", "supportsAllDrives": True})
    if r and r.get("successful"):
        print(f"  Moved asset: {fid[:12]}...")

# Move Solopreneur OS outline to Solopreneur_OS/02_Assets/
print("\nMoving Solopreneur OS outline...")
r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": "1vmvJNvMaIW3XCkhEp11_ZlMNjk4fewDuN_3TuPMJXjI", "id": f"{SOLOPRENEUR}/02_Assets", "supportsAllDrives": True})
if r and r.get("successful"):
    print("  Moved Solopreneur OS outline")

# Move Skateboarding outline to The_History_of_Skateboarding/02_Assets/
print("\nMoving Skateboarding outline...")
r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": "1oPjSktVhzkke3WllCdXNnfPd4memJkWq6_s77ttawI0", "id": f"{SKATEBOARDING}/02_Assets", "supportsAllDrives": True})
if r and r.get("successful"):
    print("  Moved Skateboarding outline")

# Move Graffiti outline to The_History_of_Graffiti/02_Assets/
print("\nMoving Graffiti outline...")
r = execute("GOOGLEDRIVE_ADD_PARENT", {"fileId": "120QyBnVk-gYbz0etuJDSwP-f83NbsiMGO6BggjKELb4", "id": f"{GRAFFITI}/02_Assets", "supportsAllDrives": True})
if r and r.get("successful"):
    print("  Moved Graffiti outline")

print("\n=== ORGANIZATION COMPLETE ===")

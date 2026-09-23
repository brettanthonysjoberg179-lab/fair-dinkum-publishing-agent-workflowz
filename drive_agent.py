#!/usr/bin/env python3
"""Google Drive Monitor Agent — scans for new files, detects duplicates, sends notifications."""
import os
import json
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

COMPOSIO = "/home/brettanthonysjoberg179/.local/bin/composio"

def load_env():
    """Load environment variables from .file."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def execute_composio(slug, params):
    """Execute a Composio tool via CLI."""
    import subprocess
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
    return None

def send_email(subject, body):
    """Send notification email via Gmail."""
    gmail_user = os.getenv("NOTIFICATION_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not gmail_user or not gmail_password:
        print("Email credentials not configured, skipping notification")
        return
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = gmail_user
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, [gmail_user], msg.as_string())
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Email failed: {e}")

def scan_drive():
    """Scan Drive for loose files and duplicates."""
    print(f"\n{'='*60}")
    print(f"Drive Scan — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Get all files
    all_files = []
    page_token = None
    while True:
        params = {"pageSize": 100, "fields": "id,name,mimeType,modifiedTime,parents"}
        if page_token:
            params["pageToken"] = page_token
        
        r = execute_composio("GOOGLEDRIVE_LIST_FILES", params)
        if not r:
            print("Failed to list files")
            break
        
        data = r.get('data', r)
        files = data.get('files', [])
        all_files.extend(files)
        
        next_token = data.get('nextPageToken')
        if not next_token:
            break
        page_token = next_token
    
    print(f"Total files scanned: {len(all_files)}")
    
    # Find loose files in root (My Drive root level)
    root_id = "root"
    loose_files = [f for f in all_files if root_id in f.get('parents', []) 
                   and f.get('mimeType') != 'application/vnd.google-apps.folder']
    
    # Find duplicates
    by_name = {}
    for f in all_files:
        name = f['name']
        if name not in by_name:
            by_name[name] = []
        by_name[name].append(f)
    
    dupes = {name: items for name, items in by_name.items() if len(items) > 1}
    
    # Report
    report_lines = []
    report_lines.append(f"Drive Scan Report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Total files: {len(all_files)}")
    report_lines.append(f"Loose files in root: {len(loose_files)}")
    report_lines.append(f"Duplicate names: {len(dupes)}")
    
    if loose_files:
        report_lines.append("\n--- Loose Files (need organization) ---")
        for f in loose_files[:20]:
            report_lines.append(f"  {f['name'][:60]} ({f['mimeType'][:30]})")
        if len(loose_files) > 20:
            report_lines.append(f"  ... and {len(loose_files) - 20} more")
    
    if dupes:
        report_lines.append("\n--- Duplicates Found ---")
        for name, items in list(dupes.items())[:10]:
            report_lines.append(f"  {name}: {len(items)} copies")
        if len(dupes) > 10:
            report_lines.append(f"  ... and {len(dupes) - 10} more")
    
    report = "\n".join(report_lines)
    print(report)
    
    # Send notification if issues found
    if loose_files or dupes:
        send_email(
            f"⚠️ Drive Scan: {len(loose_files)} loose files, {len(dupes)} duplicates",
            report
        )
    else:
        print("Drive is clean — no issues found")
    
    return report

if __name__ == "__main__":
    load_env()
    scan_drive()

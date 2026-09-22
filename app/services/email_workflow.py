#!/usr/bin/env python3
"""
Email workflow service for Fair Dinkum Publishing.

Uses Himalaya CLI for IMAP/SMTP to:
1. Watch inbox for approval replies
2. Send approval request emails
3. Parse incoming commands (APPROVE, REJECT, CHANGES)
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Email commands that trigger workflow actions
COMMAND_PATTERNS = {
    "APPROVE": re.compile(r"(?:^|\s)APPROVE\s+(FDP-[A-Z0-9]+)", re.IGNORECASE),
    "REJECT": re.compile(r"(?:^|\s)REJECT\s+(FDP-[A-Z0-9]+)", re.IGNORECASE),
    "STATUS": re.compile(r"(?:^|\s)STATUS\s+(FDP-[A-Z0-9]+)", re.IGNORECASE),
    "PUBLISH": re.compile(r"(?:^|\s)PUBLISH\s+(?:NEW\s+)?(.+)", re.IGNORECASE),
}


class EmailCommand:
    """Parsed email command."""
    def __init__(self, action: str, target: str, raw_email: dict):
        self.action = action
        self.target = target
        self.raw_email = raw_email
        self.sender = raw_email.get("from", "")
        self.subject = raw_email.get("subject", "")
        self.date = raw_email.get("date", "")
        self.body = raw_email.get("body", "")
        self.message_id = raw_email.get("id", "")

    def __repr__(self):
        return f"EmailCommand({self.action}, {self.target}, from={self.sender})"


class EmailWorkflowService:
    """Manages email-based workflow for publishing approvals."""

    def __init__(self, account: str = "brett",
                 inbox_folder: str = "INBOX",
                 processed_folder: str = "Archive"):
        self.account = account
        self.inbox_folder = inbox_folder
        self.processed_folder = processed_folder

    def _run_himalaya(self, *args, input_text: str = None) -> str:
        """Run a himalaya command and return output."""
        cmd = ["himalaya", "--account", self.account, "--output", "json"] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                input=input_text,
                timeout=30,
            )
            if result.returncode != 0:
                logger.warning("Himalaya command failed: %s", result.stderr.strip())
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error("Himalaya command timed out")
            return ""
        except FileNotFoundError:
            logger.error("Himalaya not found. Install from https://github.com/pimalaya/himalaya")
            return ""

    def check_for_commands(self, since_hours: int = 24) -> list[EmailCommand]:
        """Check inbox for workflow commands."""
        commands = []

        # List recent unread emails
        output = self._run_himalaya(
            "envelope", "list",
            "--folder", self.inbox_folder,
            "--page-size", "20",
        )

        if not output.strip():
            return commands

        try:
            emails = json.loads(output)
        except json.JSONDecodeError:
            logger.warning("Failed to parse envelope list output")
            return commands

        for env in emails:
            if env.get("seen", False):
                continue

            msg_id = env.get("id")
            if not msg_id:
                continue

            # Read the full message
            msg_output = self._run_himalaya(
                "message", "read", str(msg_id),
                "--folder", self.inbox_folder,
            )

            if not msg_output.strip():
                continue

            # Parse the message (himalaya outputs headers + body)
            raw_email = self._parse_message(msg_output, env)
            cmd = self._parse_command(raw_email)
            if cmd:
                commands.append(cmd)
                # Mark as seen
                self._run_himalaya(
                    "flag", "add", str(msg_id),
                    "--folder", self.inbox_folder,
                    "--flag", "seen",
                )

        return commands

    def _parse_message(self, raw_output: str, envelope: dict) -> dict:
        """Parse himalaya message read output into structured dict."""
        email_data = {
            "id": envelope.get("id", ""),
            "from": envelope.get("from", ""),
            "subject": envelope.get("subject", ""),
            "date": envelope.get("date", ""),
            "body": raw_output,
        }

        # Try to extract body after headers
        if "\n\n" in raw_output:
            email_data["body"] = raw_output.split("\n\n", 1)[1]

        return email_data

    def _parse_command(self, raw_email: dict) -> Optional[EmailCommand]:
        """Parse an email for workflow commands."""
        text = f"{raw_email.get('subject', '')}\n{raw_email.get('body', '')}"

        for action, pattern in COMMAND_PATTERNS.items():
            match = pattern.search(text)
            if match:
                return EmailCommand(
                    action=action,
                    target=match.group(1).strip(),
                    raw_email=raw_email,
                )

        return None

    def send_approval_request(self, to: str, project_id: str, title: str,
                               gate: str, checklist: list[str],
                               evaluation_score: float = None,
                               review_links: dict = None) -> bool:
        """Send a GATE approval request email."""
        subject = f"[FDP {gate}] {project_id}: {title}"

        body_lines = [
            f"GATE Approval Request: {gate}",
            f"Project: {project_id}",
            f"Title: {title}",
            "",
        ]

        if evaluation_score is not None:
            body_lines.append(f"Quality Score: {evaluation_score:.0f}/100")
            body_lines.append("")

        body_lines.append("Checklist:")
        for item in checklist:
            body_lines.append(f"  [ ] {item}")

        if review_links:
            body_lines.append("")
            body_lines.append("Review Links:")
            for name, url in review_links.items():
                body_lines.append(f"  - {name}: {url}")

        body_lines.extend([
            "",
            "Reply with one of:",
            f"  APPROVE {project_id}  — proceed to next stage",
            f"  REJECT {project_id}   — halt and log",
            f"  STATUS {project_id}   — get current status",
            "",
            "Or add changes as: CHANGES: <your instructions>",
        ])

        body = "\n".join(body_lines)

        return self._send_email(to, subject, body)

    def send_status_update(self, to: str, project_id: str, status: str,
                           details: dict = None) -> bool:
        """Send project status update."""
        subject = f"[FDP STATUS] {project_id}: {status}"
        body_lines = [
            f"Project: {project_id}",
            f"Status: {status}",
            f"Updated: {datetime.now(timezone.utc).isoformat()}",
        ]
        if details:
            body_lines.append("")
            body_lines.append("Details:")
            for k, v in details.items():
                body_lines.append(f"  {k}: {v}")

        body = "\n".join(body_lines)
        return self._send_email(to, subject, body)

    def send_notification(self, to: str, subject: str, body: str) -> bool:
        """Send a notification email."""
        return self._send_email(to, f"[FDP] {subject}", body)

    def _send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email via Himalaya."""
        msg = f"To: {to}\nSubject: {subject}\n\n{body}\n"
        output = self._run_himalaya("template", "send", input_text=msg)
        success = "error" not in output.lower()
        if success:
            logger.info("Email sent: %s to %s", subject, to)
        else:
            logger.error("Failed to send email: %s", output)
        return success


class ApprovalGate:
    """Manages the human-in-the-loop approval state machine."""

    def __init__(self, state_dir: str = "./data/approvals"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def get_approval_state(self, project_id: str) -> dict:
        """Get current approval state for a project."""
        state_file = self.state_dir / f"{project_id}.json"
        if state_file.exists():
            return json.loads(state_file.read_text())
        return {
            "project_id": project_id,
            "gate1_status": "pending",  # pending, requested, approved, rejected
            "gate2_status": "pending",
            "gate1_requested_at": None,
            "gate1_decided_at": None,
            "gate1_decision_by": None,
            "history": [],
        }

    def save_approval_state(self, state: dict):
        """Persist approval state."""
        state_file = self.state_dir / f"{state['project_id']}.json"
        state_file.write_text(json.dumps(state, indent=2))

    def request_gate1(self, project_id: str) -> dict:
        """Mark GATE-1 as requested."""
        state = self.get_approval_state(project_id)
        state["gate1_status"] = "requested"
        state["gate1_requested_at"] = datetime.now(timezone.utc).isoformat()
        state["history"].append({
            "event": "gate1_requested",
            "timestamp": state["gate1_requested_at"],
        })
        self.save_approval_state(state)
        return state

    def approve_gate1(self, project_id: str, decided_by: str) -> dict:
        """Approve GATE-1."""
        state = self.get_approval_state(project_id)
        state["gate1_status"] = "approved"
        state["gate1_decided_at"] = datetime.now(timezone.utc).isoformat()
        state["gate1_decision_by"] = decided_by
        state["history"].append({
            "event": "gate1_approved",
            "timestamp": state["gate1_decided_at"],
            "by": decided_by,
        })
        self.save_approval_state(state)
        return state

    def reject_gate1(self, project_id: str, decided_by: str, reason: str = "") -> dict:
        """Reject GATE-1."""
        state = self.get_approval_state(project_id)
        state["gate1_status"] = "rejected"
        state["gate1_decided_at"] = datetime.now(timezone.utc).isoformat()
        state["gate1_decision_by"] = decided_by
        state["history"].append({
            "event": "gate1_rejected",
            "timestamp": state["gate1_decided_at"],
            "by": decided_by,
            "reason": reason,
        })
        self.save_approval_state(state)
        return state

    def request_gate2(self, project_id: str) -> dict:
        """Mark GATE-2 as requested."""
        state = self.get_approval_state(project_id)
        state["gate2_status"] = "requested"
        state["history"].append({
            "event": "gate2_requested",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.save_approval_state(state)
        return state

    def approve_gate2(self, project_id: str, decided_by: str) -> dict:
        """Approve GATE-2."""
        state = self.get_approval_state(project_id)
        state["gate2_status"] = "approved"
        state["history"].append({
            "event": "gate2_approved",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "by": decided_by,
        })
        self.save_approval_state(state)
        return state

    def is_gate1_approved(self, project_id: str) -> bool:
        """Check if GATE-1 is approved."""
        state = self.get_approval_state(project_id)
        return state["gate1_status"] == "approved"

    def is_gate2_approved(self, project_id: str) -> bool:
        """Check if GATE-2 is approved."""
        state = self.get_approval_state(project_id)
        return state["gate2_status"] == "approved"


# ---------------------------------------------------------------------------
# High-level orchestrator for email-driven publishing
# ---------------------------------------------------------------------------

class EmailDrivenPublisher:
    """Orchestrates publishing workflow triggered by email commands."""

    def __init__(self, email_service: EmailWorkflowService,
                 approval_gate: ApprovalGate,
                 default_recipient: str = "brettanthonysjoberg179@gmail.com"):
        self.email = email_service
        self.gate = approval_gate
        self.recipient = default_recipient

    def process_incoming_commands(self) -> list[dict]:
        """Check email for commands and process them."""
        commands = self.email.check_for_commands()
        results = []

        for cmd in commands:
            result = self._handle_command(cmd)
            results.append(result)

        return results

    def _handle_command(self, cmd: EmailCommand) -> dict:
        """Handle a single email command."""
        if cmd.action == "APPROVE":
            return self._handle_approve(cmd)
        elif cmd.action == "REJECT":
            return self._handle_reject(cmd)
        elif cmd.action == "STATUS":
            return self._handle_status(cmd)
        elif cmd.action == "PUBLISH":
            return self._handle_publish(cmd)
        return {"status": "unknown_command", "command": cmd.action}

    def _handle_approve(self, cmd: EmailCommand) -> dict:
        """Handle APPROVE command."""
        project_id = cmd.target

        # Determine which gate to approve based on current state
        state = self.gate.get_approval_state(project_id)

        if state["gate1_status"] == "requested":
            self.gate.approve_gate1(project_id, cmd.sender)
            self.email.send_status_update(
                self.recipient, project_id,
                "GATE-1 APPROVED — proceeding to publish",
            )
            return {"status": "gate1_approved", "project_id": project_id}

        elif state["gate2_status"] == "requested":
            self.gate.approve_gate2(project_id, cmd.sender)
            self.email.send_status_update(
                self.recipient, project_id,
                "GATE-2 APPROVED — proceeding to market",
            )
            return {"status": "gate2_approved", "project_id": project_id}

        else:
            return {"status": "no_pending_gate", "project_id": project_id}

    def _handle_reject(self, cmd: EmailCommand) -> dict:
        """Handle REJECT command."""
        project_id = cmd.target
        reason = cmd.body.replace(f"REJECT {project_id}", "").strip()

        state = self.gate.get_approval_state(project_id)

        if state["gate1_status"] == "requested":
            self.gate.reject_gate1(project_id, cmd.sender, reason)
        elif state["gate2_status"] == "requested":
            # For gate 2, just log and notify
            pass

        self.email.send_status_update(
            self.recipient, project_id,
            f"REJECTED — halted. Reason: {reason or 'none given'}",
        )
        return {"status": "rejected", "project_id": project_id, "reason": reason}

    def _handle_status(self, cmd: EmailCommand) -> dict:
        """Handle STATUS command."""
        project_id = cmd.target
        state = self.gate.get_approval_state(project_id)

        self.email.send_status_update(
            self.recipient, project_id,
            f"Current state: {state.get('gate1_status', 'unknown')}",
            details=state,
        )
        return {"status": "sent", "project_id": project_id}

    def _handle_publish(self, cmd: EmailCommand) -> dict:
        """Handle PUBLISH NEW command."""
        # This would trigger the full pipeline
        return {"status": "publish_triggered", "target": cmd.target}


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)

    email_svc = EmailWorkflowService()
    gate = ApprovalGate()
    publisher = EmailDrivenPublisher(email_svc, gate)

    # Check for commands
    print("Checking for email commands...")
    results = publisher.process_incoming_commands()
    print(f"Processed {len(results)} commands: {results}")

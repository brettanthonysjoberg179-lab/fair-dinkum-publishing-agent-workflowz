#!/bin/bash
cd /home/brettanthonysjoberg179/fair-dinkum-publishing-agent-workflowz
export $(xargs < .env)
/usr/bin/python3 drive_agent.py >> agent_log.log 2>&1

"""Composio integration for agent tooling and skills."""

from typing import Any, Dict, List, Optional
from functools import lru_cache
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Standardized tool execution result."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class ComposioToolkit:
    """Composio toolkit for agent skills and tooling."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Composio client and available tools."""
        self.api_key = api_key
        # Available Composio apps/integrations
        self._available_apps = {
            'google_drive': 'GOOGLEDRIVE',
            'gmail': 'GMAIL',
            'stripe': 'STRIPE',
            'slack': 'SLACK',
            'github': 'GITHUB',
            'serpapi': 'SERPAPI',
            'anthropic': 'ANTHROPIC',
            'openai': 'OPENAI',
            'notion': 'NOTION',
            'jira': 'JIRA',
            'trello': 'TRELLO',
            'asana': 'ASANA',
            'hubspot': 'HUBSPOT',
            'zapier': 'ZAPIER',
            'send_grid': 'SENDGRID',
            'mailchimp': 'MAILCHIMP',
            'figma': 'FIGMA',
            'canva': 'CANVA',
            'airtable': 'AIRTABLE',
            'monday': 'MONDAY',
        }

    def get_available_tools(self, app_name: str) -> List[str]:
        """Get all available actions for a specific app."""
        if app_name not in self._available_apps:
            return []
        
        # This would call Composio API in production
        # For now, return common actions
        return self._get_actions_for_app(app_name)

    def _get_actions_for_app(self, app_name: str) -> List[str]:
        """Get actions for specific apps."""
        actions_map = {
            'google_drive': [
                'UPLOAD_FILE', 'GET_FILE', 'CREATE_FOLDER', 
                'LIST_FILES', 'DELETE_FILE', 'SHARE_FILE'
            ],
            'gmail': [
                'SEND_MESSAGE', 'GET_MESSAGE', 'CREATE_DRAFT',
                'SEND_REPLY', 'MARK_AS_READ', 'ARCHIVE'
            ],
            'stripe': [
                'CREATE_PRODUCT', 'CREATE_PAYMENT_LINK', 'GET_ACCOUNT',
                'LIST_PRODUCTS', 'CREATE_INVOICE', 'REFUND'
            ],
            'slack': [
                'SEND_MESSAGE', 'POST_MESSAGE', 'CREATE_CHANNEL',
                'UPDATE_MESSAGE', 'DELETE_MESSAGE', 'UPLOAD_FILE'
            ],
            'github': [
                'CREATE_ISSUE', 'CREATE_COMMIT', 'CREATE_PR',
                'LIST_ISSUES', 'UPDATE_ISSUE', 'CLOSE_ISSUE'
            ],
            'serpapi': [
                'SEARCH', 'GET_ORGANIC_RESULTS', 'GET_RELATED_SEARCHES'
            ],
            'notion': [
                'CREATE_PAGE', 'UPDATE_DATABASE_ITEM', 'CREATE_DATABASE',
                'GET_PAGE', 'UPDATE_PAGE'
            ],
            'hubspot': [
                'CREATE_CONTACT', 'CREATE_DEAL', 'GET_CONTACT',
                'UPDATE_CONTACT', 'CREATE_TASK'
            ],
        }
        return actions_map.get(app_name, [])

    async def execute_tool(
        self,
        app_name: str,
        action: str,
        params: Dict[str, Any],
        entity_id: Optional[str] = None
    ) -> ToolResult:
        """Execute a Composio tool action."""
        try:
            if app_name not in self._available_apps:
                return ToolResult(
                    success=False,
                    error=f"App '{app_name}' not found in Composio toolkit"
                )
            
            # In production, this would call Composio API
            # For now, we simulate the execution
            result = await self._simulate_tool_execution(app_name, action, params)
            
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    async def _simulate_tool_execution(
        self,
        app_name: str,
        action: str,
        params: Dict[str, Any]
    ) -> ToolResult:
        """Simulate tool execution for demo purposes."""
        # In production, replace with actual Composio API calls
        return ToolResult(
            success=True,
            data={
                'message': f'Simulated execution of {app_name}.{action}',
                'params': params
            }
        )


class AgentSkillRegistry:
    """Registry of predefined skills for agents."""
    
    # Web & Research Skills
    WEB_SEARCH = {
        'name': 'web_search',
        'app': 'serpapi',
        'action': 'SEARCH',
        'description': 'Search the web for information',
        'required_params': ['q'],
        'optional_params': ['num', 'start']
    }
    
    # Google Drive Skills
    GOOGLE_DRIVE_UPLOAD = {
        'name': 'upload_to_drive',
        'app': 'google_drive',
        'action': 'UPLOAD_FILE',
        'description': 'Upload file to Google Drive',
        'required_params': ['file_path', 'filename'],
        'optional_params': ['folder_id', 'mime_type']
    }
    
    GOOGLE_DRIVE_READ = {
        'name': 'read_from_drive',
        'app': 'google_drive',
        'action': 'GET_FILE',
        'description': 'Read file from Google Drive',
        'required_params': ['file_id'],
        'optional_params': []
    }
    
    GOOGLE_DRIVE_CREATE_FOLDER = {
        'name': 'create_folder',
        'app': 'google_drive',
        'action': 'CREATE_FOLDER',
        'description': 'Create folder in Google Drive',
        'required_params': ['name'],
        'optional_params': ['parent_id']
    }
    
    GOOGLE_DRIVE_LIST = {
        'name': 'list_drive_files',
        'app': 'google_drive',
        'action': 'LIST_FILES',
        'description': 'List files in Google Drive',
        'required_params': [],
        'optional_params': ['folder_id', 'query']
    }
    
    # Gmail Skills
    GMAIL_SEND = {
        'name': 'send_email',
        'app': 'gmail',
        'action': 'SEND_MESSAGE',
        'description': 'Send email via Gmail',
        'required_params': ['to', 'subject', 'body'],
        'optional_params': ['cc', 'bcc', 'attachments']
    }
    
    GMAIL_CREATE_DRAFT = {
        'name': 'create_draft_email',
        'app': 'gmail',
        'action': 'CREATE_DRAFT',
        'description': 'Create draft email in Gmail',
        'required_params': ['to', 'subject', 'body'],
        'optional_params': ['cc', 'bcc']
    }
    
    # Stripe Skills
    STRIPE_CREATE_PRODUCT = {
        'name': 'create_stripe_product',
        'app': 'stripe',
        'action': 'CREATE_PRODUCT',
        'description': 'Create product in Stripe',
        'required_params': ['name'],
        'optional_params': ['description', 'type', 'active']
    }
    
    STRIPE_CREATE_PAYMENT_LINK = {
        'name': 'create_payment_link',
        'app': 'stripe',
        'action': 'CREATE_PAYMENT_LINK',
        'description': 'Create Stripe payment link',
        'required_params': ['line_items'],
        'optional_params': ['metadata', 'customer_email']
    }
    
    STRIPE_GET_STATS = {
        'name': 'get_stripe_stats',
        'app': 'stripe',
        'action': 'GET_ACCOUNT',
        'description': 'Get Stripe account statistics',
        'required_params': [],
        'optional_params': []
    }
    
    # Slack Skills
    SLACK_SEND_MESSAGE = {
        'name': 'send_slack_message',
        'app': 'slack',
        'action': 'SEND_MESSAGE',
        'description': 'Send message to Slack channel',
        'required_params': ['channel', 'text'],
        'optional_params': ['blocks', 'attachments']
    }
    
    SLACK_POST_THREAD = {
        'name': 'post_to_thread',
        'app': 'slack',
        'action': 'POST_MESSAGE',
        'description': 'Post message to Slack thread',
        'required_params': ['channel', 'text'],
        'optional_params': ['thread_ts']
    }
    
    SLACK_UPLOAD_FILE = {
        'name': 'upload_slack_file',
        'app': 'slack',
        'action': 'UPLOAD_FILE',
        'description': 'Upload file to Slack',
        'required_params': ['channels', 'file_path'],
        'optional_params': ['title', 'initial_comment']
    }
    
    # GitHub Skills
    GITHUB_CREATE_ISSUE = {
        'name': 'create_github_issue',
        'app': 'github',
        'action': 'CREATE_ISSUE',
        'description': 'Create GitHub issue',
        'required_params': ['owner', 'repo', 'title'],
        'optional_params': ['body', 'labels', 'assignees']
    }
    
    GITHUB_CREATE_COMMIT = {
        'name': 'create_commit',
        'app': 'github',
        'action': 'CREATE_COMMIT',
        'description': 'Create commit in GitHub',
        'required_params': ['owner', 'repo', 'message', 'files'],
        'optional_params': ['branch']
    }
    
    GITHUB_CREATE_PR = {
        'name': 'create_pull_request',
        'app': 'github',
        'action': 'CREATE_PR',
        'description': 'Create pull request in GitHub',
        'required_params': ['owner', 'repo', 'head', 'base', 'title'],
        'optional_params': ['body', 'reviewers']
    }
    
    # Notion Skills
    NOTION_CREATE_PAGE = {
        'name': 'create_notion_page',
        'app': 'notion',
        'action': 'CREATE_PAGE',
        'description': 'Create page in Notion',
        'required_params': ['parent_id', 'properties'],
        'optional_params': ['icon', 'cover']
    }
    
    NOTION_UPDATE_DATABASE = {
        'name': 'update_notion_db',
        'app': 'notion',
        'action': 'UPDATE_DATABASE_ITEM',
        'description': 'Update Notion database',
        'required_params': ['page_id', 'properties'],
        'optional_params': []
    }
    
    # HubSpot Skills
    HUBSPOT_CREATE_CONTACT = {
        'name': 'create_contact',
        'app': 'hubspot',
        'action': 'CREATE_CONTACT',
        'description': 'Create contact in HubSpot',
        'required_params': ['email'],
        'optional_params': ['firstname', 'lastname', 'phone']
    }
    
    HUBSPOT_CREATE_DEAL = {
        'name': 'create_deal',
        'app': 'hubspot',
        'action': 'CREATE_DEAL',
        'description': 'Create deal in HubSpot',
        'required_params': ['dealname', 'dealstage'],
        'optional_params': ['amount', 'probability', 'closedate']
    }
    
    HUBSPOT_UPDATE_CONTACT = {
        'name': 'update_contact',
        'app': 'hubspot',
        'action': 'UPDATE_CONTACT',
        'description': 'Update contact in HubSpot',
        'required_params': ['contact_id', 'properties'],
        'optional_params': []
    }
    
    # Figma Skills
    FIGMA_CREATE_FILE = {
        'name': 'create_figma_file',
        'app': 'figma',
        'action': 'CREATE_FILE',
        'description': 'Create file in Figma',
        'required_params': ['name', 'team_id'],
        'optional_params': []
    }
    
    # Canva Skills
    CANVA_CREATE_DESIGN = {
        'name': 'create_canva_design',
        'app': 'canva',
        'action': 'CREATE_DESIGN',
        'description': 'Create design in Canva',
        'required_params': ['template_type'],
        'optional_params': ['width', 'height']
    }
    
    # Airtable Skills
    AIRTABLE_CREATE_RECORD = {
        'name': 'create_airtable_record',
        'app': 'airtable',
        'action': 'CREATE_RECORD',
        'description': 'Create record in Airtable',
        'required_params': ['base_id', 'table_name', 'fields'],
        'optional_params': []
    }
    
    @classmethod
    def get_skill(cls, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get skill definition by name."""
        return getattr(cls, skill_name.upper(), None)
    
    @classmethod
    def get_all_skills(cls) -> Dict[str, Dict[str, Any]]:
        """Get all available skills."""
        skills = {}
        for attr_name in dir(cls):
            if attr_name.isupper() and not attr_name.startswith('_'):
                attr = getattr(cls, attr_name)
                if isinstance(attr, dict):
                    skills[attr.get('name')] = attr
        return skills
    
    @classmethod
    def list_skills_by_app(cls, app_name: str) -> List[Dict[str, Any]]:
        """Get all skills for a specific app."""
        all_skills = cls.get_all_skills()
        return [skill for skill in all_skills.values() if skill.get('app') == app_name]

"""
Agent Communication System - Chat and Message Board
Agents can send messages, request help, discuss issues, and share results
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict


class MessageBoard:
    """
    Shared message board where all agents can post and read messages.
    Like a corporate Slack/Teams channel.
    """
    
    def __init__(self):
        self.channels: Dict[str, List[Dict]] = defaultdict(list)
        self.messages: Dict[str, Dict] = {}
        self.message_counter = 0
    
    def create_channel(self, channel_name: str, description: str = "") -> Dict:
        """Create a new communication channel"""
        self.channels[channel_name] = []
        return {
            "channel": channel_name,
            "description": description,
            "status": "created"
        }
    
    def post_message(self, channel: str, sender_id: str, sender_name: str,
                     content: str, message_type: str = "text",
                     subject: str = None, reply_to: str = None) -> Dict:
        """Post a message to a channel"""
        self.message_counter += 1
        message_id = str(self.message_counter)
        
        message = {
            "id": message_id,
            "channel": channel,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "content": content,
            "message_type": message_type,
            "subject": subject,
            "reply_to": reply_to,
            "created_at": datetime.utcnow().isoformat(),
            "replies": []
        }
        
        self.messages[message_id] = message
        self.channels[channel].append(message)
        
        return message
    
    def reply_to_message(self, message_id: str, sender_id: str, sender_name: str,
                         content: str, message_type: str = "text") -> Dict:
        """Reply to an existing message"""
        if message_id not in self.messages:
            return {"error": "Message not found"}
        
        self.message_counter += 1
        reply_id = str(self.message_counter)
        
        reply = {
            "id": reply_id,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "content": content,
            "message_type": message_type,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.messages[message_id]["replies"].append(reply)
        return reply
    
    def get_channel_messages(self, channel: str, limit: int = 50) -> List[Dict]:
        """Get messages from a channel"""
        messages = self.channels.get(channel, [])
        return messages[-limit:]
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get a specific message"""
        return self.messages.get(message_id)
    
    def search_messages(self, channel: str, query: str) -> List[Dict]:
        """Search messages in a channel"""
        messages = self.channels.get(channel, [])
        return [m for m in messages if query.lower() in m["content"].lower()]
    
    def get_all_channels(self) -> List[str]:
        """List all channels"""
        return list(self.channels.keys())


class AgentChat:
    """
    Direct messaging between agents.
    Like private DMs in a corporate environment.
    """
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
    
    def _get_conversation_key(self, agent1_id: str, agent2_id: str) -> str:
        """Create a unique key for a conversation between two agents"""
        ids = sorted([agent1_id, agent2_id])
        return f"{ids[0]}:{ids[1]}"
    
    def send_message(self, from_id: str, from_name: str, to_id: str, to_name: str,
                     content: str, message_type: str = "text") -> Dict:
        """Send a direct message between agents"""
        key = self._get_conversation_key(from_id, to_id)
        
        message = {
            "from_id": from_id,
            "from_name": from_name,
            "to_id": to_id,
            "to_name": to_name,
            "content": content,
            "message_type": message_type,
            "created_at": datetime.utcnow().isoformat()
        }
        
        if key not in self.conversations:
            self.conversations[key] = []
        
        self.conversations[key].append(message)
        return message
    
    def get_conversation(self, agent1_id: str, agent2_id: str, 
                         limit: int = 50) -> List[Dict]:
        """Get conversation history between two agents"""
        key = self._get_conversation_key(agent1_id, agent2_id)
        messages = self.conversations.get(key, [])
        return messages[-limit:]
    
    def get_all_conversations_for_agent(self, agent_id: str) -> Dict[str, List[Dict]]:
        """Get all conversations for a specific agent"""
        result = {}
        for key, messages in self.conversations.items():
            if agent_id in key:
                result[key] = messages
        return result


class IssueTracker:
    """
    Centralized issue and error tracking system.
    Agents can report issues, discuss them, and track resolution.
    """
    
    def __init__(self):
        self.issues: Dict[str, Dict] = {}
        self.issue_counter = 0
    
    def create_issue(self, title: str, description: str, reported_by: str,
                     reported_by_name: str, severity: str = "medium",
                     department: str = None) -> Dict:
        """Create a new issue"""
        self.issue_counter += 1
        issue_id = f"ISSUE-{self.issue_counter:04d}"
        
        issue = {
            "id": issue_id,
            "title": title,
            "description": description,
            "reported_by": reported_by,
            "reported_by_name": reported_by_name,
            "severity": severity,
            "department": department,
            "status": "open",  # open, investigating, resolved, closed
            "assigned_to": None,
            "comments": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.issues[issue_id] = self.issues
        self.issues[issue_id] = issue
        return issue
    
    def add_comment(self, issue_id: str, agent_id: str, agent_name: str,
                    content: str) -> Dict:
        """Add a comment to an issue for discussion"""
        if issue_id not in self.issues:
            return {"error": "Issue not found"}
        
        comment = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.issues[issue_id]["comments"].append(comment)
        self.issues[issue_id]["updated_at"] = datetime.utcnow().isoformat()
        return comment
    
    def update_issue_status(self, issue_id: str, status: str, 
                            assigned_to: str = None) -> Dict:
        """Update issue status"""
        if issue_id not in self.issues:
            return {"error": "Issue not found"}
        
        self.issues[issue_id]["status"] = status
        if assigned_to:
            self.issues[issue_id]["assigned_to"] = assigned_to
        self.issues[issue_id]["updated_at"] = datetime.utcnow().isoformat()
        
        return self.issues[issue_id]
    
    def get_issue(self, issue_id: str) -> Optional[Dict]:
        """Get an issue"""
        return self.issues.get(issue_id)
    
    def get_all_issues(self, status: str = None, department: str = None) -> List[Dict]:
        """Get all issues, optionally filtered"""
        issues = list(self.issues.values())
        
        if status:
            issues = [i for i in issues if i["status"] == status]
        if department:
            issues = [i for i in issues if i.get("department") == department]
        
        return issues
    
    def get_open_issues(self) -> List[Dict]:
        """Get all open issues"""
        return self.get_all_issues(status="open")
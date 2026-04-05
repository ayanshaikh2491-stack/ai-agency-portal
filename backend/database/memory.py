"""
Agent Memory System - Persistent memory for all agents
Stores context, learnings, skills, and conversation history
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os


class MemoryStore:
    """
    In-memory store with file persistence.
    All agent memories are saved to disk for persistence across restarts.
    """
    
    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = storage_path
        self.memories: Dict[str, Dict[str, Any]] = {}
        self._ensure_storage()
        self._load_all()
    
    def _ensure_storage(self):
        """Create storage directory if it doesn't exist"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _get_file_path(self, agent_id: str) -> str:
        return os.path.join(self.storage_path, f"{agent_id}.json")
    
    def _load_all(self):
        """Load all memories from disk"""
        if not os.path.exists(self.storage_path):
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                agent_id = filename[:-5]
                try:
                    with open(os.path.join(self.storage_path, filename), "r") as f:
                        self.memories[agent_id] = json.load(f)
                except (json.JSONDecodeError, IOError):
                    self.memories[agent_id] = {}
    
    def _save(self, agent_id: str):
        """Save memories to disk"""
        file_path = self._get_file_path(agent_id)
        with open(file_path, "w") as f:
            json.dump(self.memories.get(agent_id, {}), f, indent=2)
    
    def store(self, agent_id: str, key: str, value: Any, 
              memory_type: str = "context", importance: int = 1) -> Dict:
        """Store a memory for an agent"""
        if agent_id not in self.memories:
            self.memories[agent_id] = {}
        
        self.memories[agent_id][key] = {
            "value": value,
            "type": memory_type,
            "importance": importance,
            "created_at": datetime.utcnow().isoformat(),
            "accessed_at": datetime.utcnow().isoformat(),
            "access_count": 0
        }
        
        self._save(agent_id)
        return self.memories[agent_id][key]
    
    def recall(self, agent_id: str, key: str) -> Optional[Any]:
        """Recall a specific memory"""
        if agent_id not in self.memories:
            return None
        
        memory = self.memories[agent_id].get(key)
        if memory:
            memory["accessed_at"] = datetime.utcnow().isoformat()
            memory["access_count"] = memory.get("access_count", 0) + 1
            self._save(agent_id)
            return memory.get("value")
        
        return None
    
    def search(self, agent_id: str, query: str = None, 
               memory_type: str = None, min_importance: int = 0) -> List[Dict]:
        """Search through an agent's memories"""
        if agent_id not in self.memories:
            return []
        
        results = []
        for key, memory in self.memories[agent_id].items():
            # Filter by type
            if memory_type and memory.get("type") != memory_type:
                continue
            
            # Filter by importance
            if memory.get("importance", 0) < min_importance:
                continue
            
            # Filter by query
            if query:
                query_lower = query.lower()
                if query_lower not in key.lower() and query_lower not in str(memory.get("value", "")).lower():
                    continue
            
            results.append({
                "key": key,
                **memory
            })
        
        # Sort by importance and access count
        results.sort(key=lambda x: (x.get("importance", 0), x.get("access_count", 0)), reverse=True)
        return results
    
    def delete(self, agent_id: str, key: str) -> bool:
        """Delete a memory"""
        if agent_id in self.memories and key in self.memories[agent_id]:
            del self.memories[agent_id][key]
            self._save(agent_id)
            return True
        return False
    
    def clear(self, agent_id: str) -> int:
        """Clear all memories for an agent"""
        if agent_id in self.memories:
            count = len(self.memories[agent_id])
            self.memories[agent_id] = {}
            self._save(agent_id)
            return count
        return 0
    
    def get_stats(self, agent_id: str) -> Dict:
        """Get memory statistics for an agent"""
        if agent_id not in self.memories:
            return {"total": 0}
        
        memories = self.memories[agent_id]
        types = {}
        for key, memory in memories.items():
            mem_type = memory.get("type", "unknown")
            types[mem_type] = types.get(mem_type, 0) + 1
        
        return {
            "total": len(memories),
            "by_type": types,
            "avg_importance": sum(m.get("importance", 0) for m in memories.values()) / max(len(memories), 1)
        }


class SharedKnowledge:
    """
    Shared knowledge base accessible by all agents.
    Like a company wiki or knowledge base.
    """
    
    def __init__(self, storage_path: str = "data/knowledge"):
        self.storage_path = storage_path
        self.knowledge: Dict[str, Dict] = {}
        self._ensure_storage()
        self._load()
    
    def _ensure_storage(self):
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _get_file_path(self) -> str:
        return os.path.join(self.storage_path, "knowledge.json")
    
    def _load(self):
        file_path = self._get_file_path()
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    self.knowledge = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.knowledge = {}
    
    def _save(self):
        file_path = self._get_file_path()
        with open(file_path, "w") as f:
            json.dump(self.knowledge, f, indent=2)
    
    def add(self, key: str, content: Any, category: str = "general",
            tags: List[str] = None, created_by: str = None) -> Dict:
        """Add knowledge entry"""
        entry = {
            "content": content,
            "category": category,
            "tags": tags or [],
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "views": 0
        }
        
        self.knowledge[key] = entry
        self._save()
        return entry
    
    def get(self, key: str) -> Optional[Dict]:
        """Get a knowledge entry"""
        entry = self.knowledge.get(key)
        if entry:
            entry["views"] = entry.get("views", 0) + 1
            self._save()
        return entry
    
    def search(self, query: str = None, category: str = None, 
               tags: List[str] = None) -> List[Dict]:
        """Search knowledge base"""
        results = []
        for key, entry in self.knowledge.items():
            if category and entry.get("category") != category:
                continue
            
            if tags:
                entry_tags = entry.get("tags", [])
                if not any(t in entry_tags for t in tags):
                    continue
            
            if query:
                query_lower = query.lower()
                if query_lower not in key.lower() and query_lower not in str(entry.get("content", "")).lower():
                    continue
            
            results.append({"key": key, **entry})
        
        return results
    
    def update(self, key: str, content: Any) -> Optional[Dict]:
        """Update a knowledge entry"""
        if key not in self.knowledge:
            return None
        
        self.knowledge[key]["content"] = content
        self.knowledge[key]["updated_at"] = datetime.utcnow().isoformat()
        self._save()
        return self.knowledge[key]
    
    def delete(self, key: str) -> bool:
        """Delete a knowledge entry"""
        if key in self.knowledge:
            del self.knowledge[key]
            self._save()
            return True
        return False
    
    def get_all_categories(self) -> List[str]:
        """Get all categories"""
        return list(set(e.get("category", "unknown") for e in self.knowledge.values()))
"""
Memory Layer - State Management and Data Persistence
===================================================

This layer handles:
- Session state management
- User data storage and retrieval
- Conversation history tracking
- Memory operations and validation
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from models import UserProfile, ConversationEntry, SessionState

class MemoryLayer:
    """
    Memory Layer manages all state, user data, and conversation history
    Provides persistent storage and retrieval capabilities
    """
    
    def __init__(self):
        self.session_state = SessionState()
        self.user_profile = UserProfile()
        self.conversation_history: List[ConversationEntry] = []
        
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current complete memory state"""
        return {
            "current_stage": self.session_state.current_stage,
            "name": self.user_profile.name,
            "birth_date": self.user_profile.date_of_birth,  # Use correct field name
            "favorite_city": self.user_profile.favorite_city,
            "delivery_preference": self.user_profile.delivery_preference,
            "research_data": self.session_state.research_data,
            "workflow_completed": self.session_state.workflow_completed,
            "last_action": self.session_state.last_action,
            "error_count": self.session_state.error_count
        }
    
    def update_user_info(self, field: str, value: str) -> Dict[str, Any]:
        """
        Update user profile information
        
        Args:
            field: Field to update (name, birth_date, favorite_city, delivery_preference)
            value: New value for the field
            
        Returns:
            Result with success status and next prompt if applicable
        """
        try:
            if field == "name":
                self.user_profile.name = value
                self.session_state.fields_collected += 1
                return {
                    "success": True,
                    "message": f"✅ Stored name: {value}",
                    "next_prompt": f"Thanks {value}! What's your birth date? Please use DD/MM format (e.g., 15/08).",
                    "fields_collected": self.session_state.fields_collected,
                    "continue_conversation": True
                }
                
            elif field == "birth_date":
                self.user_profile.date_of_birth = value  # Use correct field name
                self.session_state.fields_collected += 1
                return {
                    "success": True,
                    "message": f"✅ Stored birth_date: {value}",
                    "next_prompt": f"Perfect {self.user_profile.name}! What's your favorite city?",
                    "fields_collected": self.session_state.fields_collected,
                    "continue_conversation": True
                }
                
            elif field == "favorite_city":
                self.user_profile.favorite_city = value
                self.session_state.fields_collected += 1
                
                # Return success - stage transition will be handled by Action layer
                return {
                    "success": True,
                    "message": f"✅ Stored favorite_city: {value}",
                    "fields_collected": self.session_state.fields_collected,
                    "continue_conversation": True,
                    "info_complete": self.is_user_info_complete()
                }
                    
            elif field == "delivery_preference":
                # Set delivery preference on user profile
                self.user_profile.delivery_preference = value
                return {
                    "success": True,
                    "message": f"✅ Delivery preference set to: {value}",
                    "ready_for_delivery": True
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Unknown field: {field}",
                    "message": "Invalid field specified"
                }
                
        except Exception as e:
            self.session_state.error_count += 1
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update {field}: {e}"
            }
    
    def store_user_info_bulk(self, user_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Store multiple user info fields at once
        
        Args:
            user_data: Dictionary with user information
            
        Returns:
            Result with success status
        """
        try:
            if "name" in user_data:
                self.user_profile.name = user_data["name"]
                self.session_state.fields_collected += 1
                
            if "birth_date" in user_data:
                self.user_profile.date_of_birth = user_data["birth_date"]  # Use correct field name
                self.session_state.fields_collected += 1
                
            if "favorite_city" in user_data:
                self.user_profile.favorite_city = user_data["favorite_city"]
                self.session_state.fields_collected += 1
            
            # Check completion and transition if ready
            if self.is_user_info_complete() and self.session_state.current_stage == "USER_INFO_COLLECTION":
                self.session_state.current_stage = "HISTORICAL_RESEARCH"
                return {
                    "success": True,
                    "message": "All user information stored successfully!",
                    "stage_transition": "HISTORICAL_RESEARCH",
                    "auto_continue": True,
                    "fields_collected": self.session_state.fields_collected
                }
            
            return {
                "success": True,
                "message": "User information updated successfully",
                "fields_collected": self.session_state.fields_collected
            }
            
        except Exception as e:
            self.session_state.error_count += 1
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to store user data: {e}"
            }
    
    def store_research_data(self, research_type: str, data: Any) -> Dict[str, Any]:
        """
        Store research results
        
        Args:
            research_type: Type of research (historical_events, city_info)
            data: Research results to store
            
        Returns:
            Result with success status
        """
        try:
            if not self.session_state.research_data:
                self.session_state.research_data = {}
            
            self.session_state.research_data[research_type] = data
            
            # Check if research is complete
            has_events = "historical_events" in self.session_state.research_data
            has_city = "city_info" in self.session_state.research_data
            
            if has_events and has_city:
                self.session_state.current_stage = "PRESENTATION"
                return {
                    "success": True,
                    "message": f"Research data stored: {research_type}",
                    "research_complete": True,
                    "stage_transition": "PRESENTATION",
                    "auto_present": True
                }
            
            return {
                "success": True,
                "message": f"Research data stored: {research_type}",
                "research_complete": False
            }
            
        except Exception as e:
            self.session_state.error_count += 1
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to store research data: {e}"
            }
    
    def get_research_data(self) -> Dict[str, Any]:
        """Get stored research data"""
        return self.session_state.research_data or {}
    
    def add_conversation_entry(self, user_input: str, assistant_response: str, metadata: Optional[Dict] = None):
        """
        Add entry to conversation history
        
        Args:
            user_input: User's message
            assistant_response: Assistant's response
            metadata: Additional metadata about the interaction
        """
        # Add user input entry
        user_entry = ConversationEntry(
            timestamp=datetime.now(),
            entry_type="user_input",
            content=user_input,
            metadata=metadata or {}
        )
        self.conversation_history.append(user_entry)
        
        # Add assistant response entry
        assistant_entry = ConversationEntry(
            timestamp=datetime.now(),
            entry_type="llm_response",
            content=assistant_response,
            metadata=metadata or {}
        )
        self.conversation_history.append(assistant_entry)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history as list of dictionaries"""
        return [
            {
                "timestamp": entry.timestamp.isoformat(),
                "entry_type": entry.entry_type,
                "content": entry.content,
                "metadata": entry.metadata
            }
            for entry in self.conversation_history
        ]
    
    def is_user_info_complete(self) -> bool:
        """Check if all required user information is collected"""
        return all([
            self.user_profile.name,
            self.user_profile.date_of_birth,  # Use correct field name
            self.user_profile.favorite_city
        ])
    
    def get_user_profile_dict(self) -> Dict[str, Any]:
        """Get user profile as dictionary"""
        return {
            "name": self.user_profile.name,
            "birth_date": self.user_profile.date_of_birth,  # Use correct field name
            "favorite_city": self.user_profile.favorite_city,
            "delivery_preference": self.user_profile.delivery_preference
        }
    
    def transition_stage(self, new_stage: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Transition to a new workflow stage
        
        Args:
            new_stage: New stage to transition to
            context: Optional context about the transition
            
        Returns:
            Result with transition information
        """
        try:
            old_stage = self.session_state.current_stage
            self.session_state.current_stage = new_stage
            self.session_state.last_action = f"stage_transition_{new_stage}"
            
            return {
                "success": True,
                "old_stage": old_stage,
                "new_stage": new_stage,
                "context": context,
                "message": f"Stage transition: {old_stage} → {new_stage}"
            }
            
        except Exception as e:
            self.session_state.error_count += 1
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to transition to {new_stage}: {e}"
            }
    
    def validate_user_data(self) -> Dict[str, Any]:
        """
        Validate current user data for completeness and format
        
        Returns:
            Validation results with any issues found
        """
        issues = []
        
        if not self.user_profile.name:
            issues.append("Name is missing")
        elif len(self.user_profile.name.strip()) < 2:
            issues.append("Name is too short")
            
        if not self.user_profile.date_of_birth:  # Use correct field name
            issues.append("Birth date is missing")
        # Could add date format validation here
            
        if not self.user_profile.favorite_city:
            issues.append("Favorite city is missing")
        elif len(self.user_profile.favorite_city.strip()) < 2:
            issues.append("City name is too short")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Validation passed" if len(issues) == 0 else f"Validation failed: {', '.join(issues)}"
        }
    
    def reset_session(self):
        """Reset the current session state"""
        self.session_state = SessionState()
        self.user_profile = UserProfile()
        self.conversation_history = []
    
    def get_memory_summary(self) -> str:
        """Get a formatted summary of the current memory state"""
        state = self.get_current_state()
        return f"""Memory State Summary:
- Stage: {state['current_stage']}
- User: {state['name'] or 'Not provided'}
- Birth Date: {state['birth_date'] or 'Not provided'}
- City: {state['favorite_city'] or 'Not provided'}
- Delivery: {state['delivery_preference'] or 'Not selected'}
- Fields Collected: {self.session_state.fields_collected}/3
- Research Complete: {'Yes' if state['research_data'] else 'No'}
- Conversation Entries: {len(self.conversation_history)}
- Errors: {state['error_count']}"""

    def export_session_data(self) -> Dict[str, Any]:
        """Export complete session data for persistence or analysis"""
        return {
            "session_state": {
                "current_stage": self.session_state.current_stage,
                "fields_collected": self.session_state.fields_collected,
                "research_data": self.session_state.research_data,
                "workflow_completed": self.session_state.workflow_completed,
                "last_action": self.session_state.last_action,
                "error_count": self.session_state.error_count,
                "created_at": self.session_state.created_at.isoformat() if self.session_state.created_at else None
            },
            "user_profile": self.get_user_profile_dict(),
            "conversation_history": self.get_conversation_history(),
            "export_timestamp": datetime.now().isoformat()
        }
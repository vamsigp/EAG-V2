"""
Decision-Making Layer - Workflow Orchestration and Action Routing
================================================================

This layer handles:
- Workflow orchestration and stage management
- Action routing and decision logic
- Input validation and error handling
- Loop detection and prevention
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import re

class DecisionMakingLayer:
    """
    Decision-Making Layer orchestrates the workflow and routes actions
    Manages stage transitions, validates inputs, and prevents loops
    """
    
    def __init__(self):
        self.last_actions = []  # Track recent actions for loop detection
        self.max_loop_detection = 3  # Maximum repeated actions before intervention
        self.stage_flow = {
            "USER_INFO_COLLECTION": "HISTORICAL_RESEARCH",
            "HISTORICAL_RESEARCH": "PRESENTATION", 
            "PRESENTATION": "DELIVERY_EXECUTION",
            "DELIVERY_EXECUTION": "COMPLETED"
        }
    
    def process_perception_result(self, perception_result: Dict[str, Any], memory_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the result from Perception layer and decide next action
        
        Args:
            perception_result: Result from Perception layer
            memory_state: Current memory state
            
        Returns:
            Decision with action routing and instructions
        """
        if perception_result.get("error"):
            return self._handle_perception_error(perception_result, memory_state)
        
        # Extract action from perception result
        action = perception_result.get("action", {})
        current_stage = memory_state.get("current_stage", "USER_INFO_COLLECTION")
        
        # Validate action structure
        validation_result = self._validate_action(action, current_stage)
        if not validation_result["valid"]:
            return validation_result
        
        # Check for loops
        loop_check = self._detect_loops(action, current_stage)
        if loop_check["loop_detected"]:
            return self._handle_loop(loop_check, memory_state)
        
        # Route action based on type
        if "FUNCTION_CALL" in action:
            return self._route_function_call(action["FUNCTION_CALL"], memory_state)
        elif "USER_RESPONSE" in action:
            return self._route_user_response(action["USER_RESPONSE"], memory_state)
        else:
            return {
                "success": False,
                "error": "Invalid action format",
                "message": "Action must contain FUNCTION_CALL or USER_RESPONSE",
                "fallback_action": "continue_conversation"
            }
    
    def _validate_action(self, action: Dict[str, Any], current_stage: str) -> Dict[str, Any]:
        """Validate action structure and stage appropriateness"""
        
        if not action:
            return {
                "valid": False,
                "error": "Empty action",
                "message": "No action provided by Perception layer"
            }
        
        # Validate action type
        if "FUNCTION_CALL" not in action and "USER_RESPONSE" not in action:
            return {
                "valid": False,
                "error": "Invalid action type",
                "message": "Action must contain FUNCTION_CALL or USER_RESPONSE"
            }
        
        # Validate FUNCTION_CALL structure
        if "FUNCTION_CALL" in action:
            func_call = action["FUNCTION_CALL"]
            
            if "tool_name" not in func_call:
                return {
                    "valid": False,
                    "error": "Missing tool_name in FUNCTION_CALL",
                    "message": "FUNCTION_CALL must specify tool_name"
                }
            
            # Validate tool name
            valid_tools = ["gather_user_info", "research_historical_events", "research_city_info", "generate_pdf", "send_email"]
            if func_call["tool_name"] not in valid_tools:
                return {
                    "valid": False,
                    "error": f"Invalid tool name: {func_call['tool_name']}",
                    "message": f"Valid tools: {', '.join(valid_tools)}"
                }
            
            # Stage-specific validation
            stage_validation = self._validate_stage_tool_compatibility(current_stage, func_call["tool_name"])
            if not stage_validation["valid"]:
                return stage_validation
        
        # Validate USER_RESPONSE structure  
        if "USER_RESPONSE" in action:
            user_resp = action["USER_RESPONSE"]
            
            if "message" not in user_resp:
                return {
                    "valid": False,
                    "error": "Missing message in USER_RESPONSE",
                    "message": "USER_RESPONSE must contain message"
                }
        
        return {"valid": True}
    
    def _validate_stage_tool_compatibility(self, stage: str, tool_name: str) -> Dict[str, Any]:
        """Validate if tool is appropriate for current stage"""
        
        stage_tools = {
            "USER_INFO_COLLECTION": ["gather_user_info"],
            "HISTORICAL_RESEARCH": ["research_historical_events", "research_city_info"],
            "PRESENTATION": ["generate_pdf", "send_email"],
            "DELIVERY_EXECUTION": ["generate_pdf", "send_email"]
        }
        
        if stage not in stage_tools:
            return {
                "valid": True,  # Allow unknown stages to proceed
                "warning": f"Unknown stage: {stage}"
            }
        
        if tool_name not in stage_tools[stage]:
            # Special case: allow gather_user_info in HISTORICAL_RESEARCH if we just transitioned
            # This handles the case where LLM generated gather_user_info but stage changed mid-request
            if tool_name == "gather_user_info" and stage == "HISTORICAL_RESEARCH":
                return {
                    "valid": True,
                    "warning": f"gather_user_info called in {stage} stage - will redirect to research",
                    "redirect_needed": True
                }
            
            return {
                "valid": False,
                "error": f"Tool '{tool_name}' not appropriate for stage '{stage}'",
                "message": f"Valid tools for {stage}: {', '.join(stage_tools[stage])}"
            }
        
        return {"valid": True}
    
    def _detect_loops(self, action: Dict[str, Any], current_stage: str) -> Dict[str, Any]:
        """Detect if we're in a conversation loop"""
        
        # Create action signature for comparison
        action_signature = self._create_action_signature(action, current_stage)
        
        # Add to recent actions
        self.last_actions.append({
            "signature": action_signature,
            "timestamp": datetime.now(),
            "stage": current_stage
        })
        
        # Keep only recent actions (last 10)
        self.last_actions = self.last_actions[-10:]
        
        # Count occurrences of this action
        recent_count = sum(1 for a in self.last_actions if a["signature"] == action_signature)
        
        if recent_count >= self.max_loop_detection:
            return {
                "loop_detected": True,
                "action_signature": action_signature,
                "repeat_count": recent_count,
                "stage": current_stage
            }
        
        return {"loop_detected": False}
    
    def _create_action_signature(self, action: Dict[str, Any], stage: str) -> str:
        """Create a signature for action comparison"""
        if "FUNCTION_CALL" in action:
            tool_name = action["FUNCTION_CALL"].get("tool_name", "unknown")
            
            # For gather_user_info, include the field being collected to avoid false loop detection
            if tool_name == "gather_user_info":
                arguments = action["FUNCTION_CALL"].get("arguments", {})
                # Determine which field is being collected
                if "name" in arguments:
                    return f"{stage}_{tool_name}_name"
                elif "birth_date" in arguments:
                    return f"{stage}_{tool_name}_birth_date"
                elif "favorite_city" in arguments:
                    return f"{stage}_{tool_name}_favorite_city"
                elif "field" in arguments:
                    field = arguments["field"]
                    return f"{stage}_{tool_name}_{field}"
            
            return f"{stage}_{tool_name}"
        elif "USER_RESPONSE" in action:
            expecting = action["USER_RESPONSE"].get("expecting", "unknown")
            return f"{stage}_user_response_{expecting}"
        else:
            return f"{stage}_unknown_action"
    
    def _handle_loop(self, loop_info: Dict[str, Any], memory_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle detected conversation loop"""
        
        stage = loop_info["stage"]
        signature = loop_info["action_signature"] 
        
        # Generate appropriate loop-breaking response based on stage
        if stage == "USER_INFO_COLLECTION":
            return {
                "success": True,
                "action_type": "loop_recovery",
                "route_to": "action_layer",
                "action": {
                    "type": "user_response",
                    "message": "I notice we're having trouble collecting your information. Let me help you step by step. Please just tell me your name first.",
                    "reset_stage": True
                }
            }
        elif stage == "HISTORICAL_RESEARCH":
            return {
                "success": True,
                "action_type": "loop_recovery", 
                "route_to": "action_layer",
                "action": {
                    "type": "auto_research",
                    "message": "Let me automatically proceed with researching historical events for you.",
                    "force_research": True
                }
            }
        elif stage == "PRESENTATION":
            return {
                "success": True,
                "action_type": "loop_recovery",
                "route_to": "action_layer", 
                "action": {
                    "type": "user_response",
                    "message": "I have your historical research ready! Would you like me to create a PDF report or send it via email? Please type 'pdf' or 'email'.",
                    "force_choice": True
                }
            }
        else:
            return {
                "success": True,
                "action_type": "loop_recovery",
                "route_to": "action_layer",
                "action": {
                    "type": "user_response",
                    "message": "I seem to be stuck. Let me help you continue. What would you like me to do next?",
                    "reset_conversation": True
                }
            }
    
    def _route_function_call(self, function_call: Dict[str, Any], memory_state: Dict[str, Any]) -> Dict[str, Any]:
        """Route function call to appropriate handler"""
        
        tool_name = function_call["tool_name"]
        arguments = function_call.get("arguments", {})
        current_stage = memory_state.get("current_stage", "USER_INFO_COLLECTION")
        
        # Add decision-making context
        routing_decision = {
            "success": True,
            "action_type": "function_call",
            "route_to": "action_layer",
            "tool_name": tool_name,
            "arguments": arguments,
            "current_stage": current_stage,
            "metadata": {
                "routed_at": datetime.now().isoformat(),
                "reasoning_type": function_call.get("reasoning_type"),
                "decision_context": self._get_decision_context(tool_name, current_stage, memory_state)
            }
        }
        
        # Add stage-specific instructions
        if tool_name == "gather_user_info":
            # Special case: if we're trying to gather_user_info but already in HISTORICAL_RESEARCH,
            # it means a stage transition just happened and we should redirect to research
            if current_stage == "HISTORICAL_RESEARCH":
                # Check if user info is complete
                if all([memory_state.get("name"), memory_state.get("birth_date"), memory_state.get("favorite_city")]):
                    # Redirect to historical research instead
                    birth_date = memory_state.get("birth_date", "15/08")
                    try:
                        parts = birth_date.split('/')
                        day, month = int(parts[0]), int(parts[1]) if len(parts) >= 2 else (15, 8)
                    except:
                        day, month = 15, 8
                    
                    return {
                        "success": True,
                        "action_type": "function_call",
                        "route_to": "action_layer", 
                        "tool_name": "research_historical_events",
                        "arguments": {"day": day, "month": month},
                        "current_stage": current_stage,
                        "stage_redirect": True,
                        "original_tool": "gather_user_info",
                        "redirect_reason": "Stage transition detected - proceeding to research"
                    }
            
            routing_decision["post_action"] = "check_info_completeness"
            
        elif tool_name == "research_historical_events":
            routing_decision["post_action"] = "store_research_results"
            routing_decision["follow_up"] = "research_city_info"
            
        elif tool_name == "research_city_info":
            routing_decision["post_action"] = "prepare_presentation"
            
        elif tool_name in ["generate_pdf", "send_email"]:
            # Enrich arguments with current user data and research results
            research_data = memory_state.get("research_data", {}) or {}
            routing_decision["arguments"].update({
                "user_data": {
                    "name": memory_state.get("name", "User"),
                    "birth_date": memory_state.get("birth_date", "Unknown"),
                    "favorite_city": memory_state.get("favorite_city", "Unknown")
                },
                "historical_events": research_data.get("historical_events", {}),
                "city_info": research_data.get("city_info", {})
            })
            routing_decision["post_action"] = "complete_workflow"
        
        return routing_decision
    
    def _route_user_response(self, user_response: Dict[str, Any], memory_state: Dict[str, Any]) -> Dict[str, Any]:
        """Route user response to appropriate handler"""
        
        message = user_response.get("message", "")
        expecting = user_response.get("expecting", "")
        current_stage = memory_state.get("current_stage", "USER_INFO_COLLECTION")
        
        return {
            "success": True,
            "action_type": "user_response",
            "route_to": "action_layer", 
            "message": message,
            "expecting": expecting,
            "current_stage": current_stage,
            "metadata": {
                "routed_at": datetime.now().isoformat(),
                "reasoning_type": user_response.get("reasoning_type"),
                "decision_context": self._get_decision_context("user_response", current_stage, memory_state)
            }
        }
    
    def _get_decision_context(self, action_type: str, stage: str, memory_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate decision context for actions"""
        
        return {
            "action_type": action_type,
            "stage": stage,
            "user_info_complete": all([
                memory_state.get("name"),
                memory_state.get("birth_date"),
                memory_state.get("favorite_city")
            ]),
            "research_available": bool(memory_state.get("research_data")),
            "next_expected_stage": self.stage_flow.get(stage),
            "decision_timestamp": datetime.now().isoformat()
        }
    
    def should_transition_stage(self, current_stage: str, action_result: Dict[str, Any], memory_state: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Determine if workflow should transition to next stage
        
        Returns:
            (should_transition: bool, next_stage: Optional[str])
        """
        
        # Check for explicit stage transition in result
        if action_result.get("stage_transition"):
            return True, action_result["stage_transition"]
        
        # Logic-based stage transitions
        if current_stage == "USER_INFO_COLLECTION":
            # Only transition on explicit stage_transition from action result
            # The gather_user_info tool will handle the transition when appropriate
            pass
                
        elif current_stage == "HISTORICAL_RESEARCH":
            # Transition when research is complete
            research_data = memory_state.get("research_data", {}) or {}
            if research_data and "historical_events" in research_data and "city_info" in research_data:
                return True, "PRESENTATION"
                
        elif current_stage == "PRESENTATION":
            # Transition when delivery method is chosen
            if action_result.get("delivery_started") or memory_state.get("delivery_preference"):
                return True, "DELIVERY_EXECUTION"
                
        elif current_stage == "DELIVERY_EXECUTION":
            # Transition when delivery is complete
            if action_result.get("delivery_complete"):
                return True, "COMPLETED"
        
        return False, None
    
    def _handle_perception_error(self, perception_result: Dict[str, Any], memory_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors from Perception layer"""
        
        error_message = perception_result.get("message", "Unknown perception error")
        current_stage = memory_state.get("current_stage", "USER_INFO_COLLECTION")
        
        # Generate appropriate fallback based on stage
        fallback_message = self._generate_error_fallback(current_stage, memory_state)
        
        return {
            "success": True,  # We handled the error
            "action_type": "error_recovery",
            "route_to": "action_layer",
            "original_error": error_message,
            "action": {
                "type": "user_response",
                "message": fallback_message,
                "is_error_recovery": True
            }
        }
    
    def _generate_error_fallback(self, stage: str, memory_state: Dict[str, Any]) -> str:
        """Generate appropriate fallback message for errors"""
        
        if stage == "USER_INFO_COLLECTION":
            if not memory_state.get("name"):
                return "I had trouble processing that. Could you please tell me your name?"
            elif not memory_state.get("birth_date"):
                return "I didn't quite catch that. What's your birth date? Please use format like 15/08 or 15 August."
            elif not memory_state.get("favorite_city"):
                return "Sorry, I missed that. What's your favorite city?"
            else:
                return "I have all your information. Let me proceed with the research."
                
        elif stage == "HISTORICAL_RESEARCH":
            return "I'm working on researching historical events for you. Please wait a moment."
            
        elif stage == "PRESENTATION":
            return "I have your research ready! Would you like a PDF report or email delivery? Please type 'pdf' or 'email'."
            
        else:
            return "I encountered an issue. Could you please let me know how you'd like to proceed?"
    
    def get_decision_summary(self) -> Dict[str, Any]:
        """Get summary of recent decision-making activity"""
        
        return {
            "recent_actions": len(self.last_actions),
            "loop_detection_active": True,
            "max_loop_threshold": self.max_loop_detection,
            "stage_flow_defined": list(self.stage_flow.keys()),
            "last_action_signatures": [a["signature"] for a in self.last_actions[-3:]]
        }
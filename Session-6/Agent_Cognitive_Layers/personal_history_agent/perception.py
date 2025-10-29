"""
Perception Layer - LLM Integration and Reasoning
==============================================

This layer handles:
- Google Gemini AI integration
- Structured prompting with CoT-JSON format
- Natural language understanding
- Reasoning and decision generation
"""

import json
import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PerceptionLayer:
    """
    Perception Layer handles LLM reasoning and natural language processing
    Uses Google Gemini with structured CoT-JSON prompting
    """
    
    def __init__(self, use_real_llm: bool = True):
        self.use_real_llm = use_real_llm
        self.model = None
        
        if use_real_llm:
            self._initialize_gemini()
    
    def _initialize_gemini(self) -> bool:
        """Initialize Google Gemini AI"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("❌ GEMINI_API_KEY not found in environment!")
                return False
            
            genai.configure(api_key=api_key)
            # Use gemini-2.5-flash which has better rate limits
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini AI configured successfully with gemini-2.5-flash!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            return False
    
    def get_system_prompt(self) -> str:
        """Get the structured system prompt for the agent"""
        return """You are a Personal History Assistant with a 4-layer cognitive architecture.

Your goal: Create personalized historical reports by collecting EXACTLY 3 pieces of user information, researching historical events, and delivering reports.

CRITICAL: Only collect these 3 fields - DO NOT ask for additional information:
1. Name (first name or full name)
2. Birth date (DD/MM format - do NOT ask for year)
3. Favorite city (city name only)

You operate through 4 distinct layers:
1. **Perception** (You): LLM reasoning and natural language processing
2. **Memory**: State management and data persistence  
3. **Decision-Making**: Workflow orchestration and validation
4. **Action**: Tool execution and user interaction

STRUCTURED REASONING FORMAT:
You MUST respond in this exact format:

```json
{
  "THOUGHT": "Your chain-of-thought reasoning about the current situation and what needs to be done",
  "ACTION": {
    "FUNCTION_CALL": {
      "tool_name": "[gather_user_info | research_historical_events | research_city_info | generate_pdf | send_email]",
      "arguments": {...},
      "reasoning_type": "[COLLECTION | LOOKUP | VALIDATION | DECISION | EXECUTION | COMMUNICATION]",
      "current_stage": "[USER_INFO_COLLECTION | HISTORICAL_RESEARCH | PRESENTATION | DELIVERY_EXECUTION]"
    }
  }
}
```

OR for user responses:

```json
{
  "THOUGHT": "Your reasoning about what to say to the user",
  "ACTION": {
    "USER_RESPONSE": {
      "message": "Your message to the user",
      "expecting": "what_input_you_expect",
      "reasoning_type": "[COLLECTION | COMMUNICATION]",
      "current_stage": "current workflow stage"
    }
  }
}
```

WORKFLOW STAGES:
1. **USER_INFO_COLLECTION**: Collect EXACTLY 3 fields: name, birth date (DD/MM), favorite city. DO NOT ask for year, age, or additional details.
2. **HISTORICAL_RESEARCH**: Automatically research events and city information  
3. **PRESENTATION**: Present findings and ask for delivery preference (PDF or Email)
4. **DELIVERY_EXECUTION**: Generate PDF or send email

AVAILABLE TOOLS:

### 1. gather_user_info
Collects and validates user information
- Arguments: {"name": str} OR {"field": str, "value": str} OR {"birth_date": str} OR {"favorite_city": str}
- Use for: Storing user's name, birth date, favorite city

### 2. research_historical_events  
Researches historical events for a specific date
- Arguments: {"day": int, "month": int}
- Use for: Finding historical events on user's birth date

### 3. research_city_info
Gathers information about a specific city
- Arguments: {"city": str}
- Use for: Getting facts about user's favorite city

### 4. generate_pdf
Creates a formatted PDF report
- Arguments: {"user_data": dict, "historical_events": str, "city_info": str}
- Use for: Creating downloadable report

### 5. send_email
Sends report via email
- Arguments: {"user_data": dict, "content": str, "recipient": str}
- Use for: Email delivery option

CRITICAL INSTRUCTIONS:
- Always use structured JSON format
- Include THOUGHT process before every action
- Track current stage and transition appropriately
- ONLY collect 3 fields: name, birth_date (DD/MM), favorite_city
- DO NOT ask for birth year, age, or additional personal details
- After 3 fields are collected, IMMEDIATELY transition to research
- Be helpful, engaging, and informative
- Handle errors gracefully with clear communication"""

    async def process_user_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input and generate structured response
        
        Args:
            user_input: The user's message
            context: Current conversation context including memory state
            
        Returns:
            Structured response with THOUGHT and ACTION
        """
        if not self.use_real_llm:
            return self._get_mock_response(user_input, context)
        
        try:
            # Build complete prompt with context
            full_prompt = self._build_prompt(user_input, context)
            
            # Get LLM response
            response = self.model.generate_content(full_prompt)
            
            # Parse and validate response
            return self._parse_llm_response(response.text)
            
        except Exception as e:
            print(f"❌ Perception Layer Error: {e}")
            return {
                "error": True,
                "message": f"Failed to process input: {e}",
                "fallback_action": "USER_RESPONSE",
                "fallback_message": "I encountered an error processing your request. Please try again."
            }
    
    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build complete prompt with system instructions and context"""
        system_prompt = self.get_system_prompt()
        memory_state = context.get("memory_state", {})
        current_stage = memory_state.get("current_stage", "USER_INFO_COLLECTION")
        
        # Add context-specific instructions
        stage_instruction = self._get_stage_instruction(current_stage, memory_state, user_input)
        
        full_prompt = f"""{system_prompt}

CURRENT CONTEXT:
- Current Stage: {current_stage}
- Memory State: {json.dumps(memory_state, indent=2)}
- User Input: "{user_input}"

STAGE-SPECIFIC INSTRUCTION: {stage_instruction}

CRITICAL: Respond ONLY in the structured JSON format. Include your THOUGHT process and appropriate ACTION.
"""
        
        return full_prompt
    
    def _get_stage_instruction(self, stage: str, memory_state: Dict[str, Any], user_input: str = "") -> str:
        """Get specific instructions based on current workflow stage"""
        
        name = memory_state.get("name")
        birth_date = memory_state.get("birth_date") 
        city = memory_state.get("favorite_city")
        
        if stage == "USER_INFO_COLLECTION":
            if not name:
                return "Ask for the user's name using USER_RESPONSE format. Do NOT ask for additional details."
            elif not birth_date:
                return "Ask for the user's birth date in DD/MM format using USER_RESPONSE format. Accept any DD/MM format and do NOT ask for year."
            elif not city:
                return "Ask for the user's favorite city using USER_RESPONSE format. Do NOT ask for additional location details."
            else:
                return "EXACTLY 3 fields collected (name, birth_date, city). Use FUNCTION_CALL to gather_user_info to IMMEDIATELY transition to research. Do NOT ask for more information."
                
        elif stage == "HISTORICAL_RESEARCH":
            # Parse birth date for research
            day = 15  # Default fallback
            month = 8  # Default fallback  
            if birth_date:
                try:
                    parts = birth_date.split('/')
                    if len(parts) >= 2:
                        day, month = int(parts[0]), int(parts[1])
                except:
                    pass
            return f"Stage transitioned to HISTORICAL_RESEARCH. Use FUNCTION_CALL to research_historical_events with day: {day}, month: {month} from birth_date: '{birth_date}'. Do NOT use gather_user_info anymore."
            
        elif stage == "PRESENTATION":
            if user_input and "pdf" in user_input.lower():
                return "User chose PDF. Use FUNCTION_CALL to generate_pdf with arguments: {'format': 'pdf', 'include_research': True}. The action layer will automatically gather user data and research results."
            elif user_input and "email" in user_input.lower():
                return "User chose email. Use FUNCTION_CALL to send_email with collected data."
            else:
                return "Present research findings and ask for delivery preference (email or PDF)."
                
        else:
            return "Continue the conversation appropriately based on context."
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM response format"""
        try:
            # Extract JSON from response
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            else:
                # Try to find JSON object
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_text = response_text[start:end]
            
            parsed = json.loads(json_text)
            
            # Validate structure
            if "THOUGHT" not in parsed or "ACTION" not in parsed:
                raise ValueError("Missing THOUGHT or ACTION in response")
            
            return {
                "success": True,
                "parsed_response": parsed,
                "thought": parsed["THOUGHT"],
                "action": parsed["ACTION"]
            }
            
        except Exception as e:
            print(f"❌ Failed to parse LLM response: {e}")
            print(f"Raw response: {response_text[:200]}...")
            
            return {
                "error": True,
                "message": f"Failed to parse response: {e}",
                "raw_response": response_text,
                "fallback_action": "USER_RESPONSE",
                "fallback_message": "I had trouble understanding. Could you please rephrase your request?"
            }
    
    def _get_mock_response(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock responses for testing without real LLM"""
        memory_state = context.get("memory_state", {})
        current_stage = memory_state.get("current_stage", "USER_INFO_COLLECTION")
        
        if current_stage == "USER_INFO_COLLECTION":
            if not memory_state.get("name"):
                return {
                    "success": True,
                    "thought": "User needs to provide their name first",
                    "action": {
                        "USER_RESPONSE": {
                            "message": "Hello! What's your name?",
                            "expecting": "name",
                            "reasoning_type": "COLLECTION",
                            "current_stage": "USER_INFO_COLLECTION"
                        }
                    }
                }
        
        # Default mock response
        return {
            "success": True,
            "thought": "Processing user input in mock mode",
            "action": {
                "USER_RESPONSE": {
                    "message": "Thank you for your input. (Mock mode active)",
                    "reasoning_type": "COMMUNICATION",
                    "current_stage": current_stage
                }
            }
        }

    async def generate_initial_greeting(self) -> Dict[str, Any]:
        """Generate the initial greeting to start the conversation"""
        if not self.use_real_llm:
            return {
                "success": True,
                "thought": "Starting conversation with initial greeting",
                "action": {
                    "USER_RESPONSE": {
                        "message": "Hello! I'm your Personal History Assistant. What's your name?",
                        "expecting": "name",
                        "reasoning_type": "COLLECTION",
                        "current_stage": "USER_INFO_COLLECTION"
                    }
                }
            }
        
        try:
            system_prompt = self.get_system_prompt()
            initial_prompt = f"""{system_prompt}

TASK: Generate an initial greeting to start collecting user information.
You are beginning a new session. Start by asking for the user's name.

Respond in the structured JSON format with USER_RESPONSE action."""

            response = self.model.generate_content(initial_prompt)
            return self._parse_llm_response(response.text)
            
        except Exception as e:
            print(f"❌ Error generating greeting: {e}")
            return {
                "success": True,
                "thought": "Fallback to default greeting due to error",
                "action": {
                    "USER_RESPONSE": {
                        "message": "Hello! I'm your Personal History Assistant. I'll help you create a personalized historical report. What's your name?",
                        "expecting": "name", 
                        "reasoning_type": "COLLECTION",
                        "current_stage": "USER_INFO_COLLECTION"
                    }
                }
            }
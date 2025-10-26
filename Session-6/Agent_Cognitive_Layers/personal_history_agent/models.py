"""
Pydantic Models for Personal History Agent

All input and output structures using Pydantic for type validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS AND TYPES
# ============================================================================

class ReasoningType(str, Enum):
    """Types of reasoning the agent can perform"""
    COLLECTION = "COLLECTION"
    LOOKUP = "LOOKUP" 
    VALIDATION = "VALIDATION"
    DECISION = "DECISION"
    EXECUTION = "EXECUTION"
    COMMUNICATION = "COMMUNICATION"


class ActionType(str, Enum):
    """Types of actions the agent can take"""
    USER_INTERACTION = "user_interaction"
    FUNCTION_CALL = "function_call"
    PRESENT_INFO = "present_info"
    USER_CHOICE = "user_choice"
    FINAL_ANSWER = "final_answer"
    ERROR = "error"


class WorkflowStage(str, Enum):
    """Workflow stages for the agent"""
    USER_INFO_COLLECTION = "USER_INFO_COLLECTION"
    HISTORICAL_RESEARCH = "HISTORICAL_RESEARCH"
    PRESENTATION = "PRESENTATION"
    DELIVERY_EXECUTION = "DELIVERY_EXECUTION"


class DeliveryMethod(str, Enum):
    """Available delivery methods"""
    EMAIL = "email"
    PDF = "pdf"


# ============================================================================
# USER DATA MODELS
# ============================================================================

class UserProfile(BaseModel):
    """User profile data with validation"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    date_of_birth: Optional[str] = Field(None, pattern=r"^\d{1,2}/\d{1,2}$")
    favorite_city: Optional[str] = Field(None, min_length=2, max_length=100)
    birth_day: Optional[int] = Field(None, ge=1, le=31)
    birth_month: Optional[int] = Field(None, ge=1, le=12)
    delivery_preference: Optional[str] = Field(None)
    
    @validator('date_of_birth')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            parts = v.split('/')
            if len(parts) != 2:
                raise ValueError("Date must be in DD/MM format")
            day, month = int(parts[0]), int(parts[1])
            if not (1 <= day <= 31) or not (1 <= month <= 12):
                raise ValueError("Invalid day or month")
            return v
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid date format: {e}")
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([self.name, self.date_of_birth, self.favorite_city])
    
    def parse_birth_date(self) -> bool:
        """Parse date_of_birth into day and month integers"""
        if not self.date_of_birth:
            return False
        try:
            parts = self.date_of_birth.split('/')
            self.birth_day = int(parts[0])
            self.birth_month = int(parts[1])
            return True
        except (ValueError, IndexError):
            return False


# ============================================================================
# RESEARCH DATA MODELS
# ============================================================================

class HistoricalEvent(BaseModel):
    """Single historical event"""
    event: str = Field(..., min_length=1)
    year: Optional[str] = None
    category: Optional[Literal["political", "scientific", "cultural", "biographical"]] = None


class HistoricalEventsResponse(BaseModel):
    """Response from historical events research"""
    reasoning: str
    reasoning_type: ReasoningType
    events: List[HistoricalEvent]


class CityInfo(BaseModel):
    """City information structure"""
    attractions: List[str] = Field(default_factory=list)
    annual_events: List[str] = Field(default_factory=list)
    interesting_facts: List[str] = Field(default_factory=list)
    historical_note: Optional[str] = None


class CityInfoResponse(BaseModel):
    """Response from city information research"""
    reasoning: str
    reasoning_type: ReasoningType
    city_info: CityInfo


class ResearchData(BaseModel):
    """Complete research data storage"""
    historical_events: Optional[HistoricalEventsResponse] = None
    city_information: Optional[CityInfoResponse] = None
    formatted_history: Optional[str] = None
    formatted_city_info: Optional[str] = None
    formatted_available: bool = False
    
    def is_complete(self) -> bool:
        """Check if research is complete"""
        return (self.historical_events is not None and 
                self.city_information is not None)


# ============================================================================
# SESSION AND MEMORY MODELS
# ============================================================================

class ConversationEntry(BaseModel):
    """Single conversation entry"""
    timestamp: datetime = Field(default_factory=datetime.now)
    entry_type: Literal["user_input", "llm_response", "tool_result", "system_message"]
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Tool execution result"""
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_name: str
    tool_input: Dict[str, Any]
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class SessionState(BaseModel):
    """Session state tracking"""
    current_stage: WorkflowStage = WorkflowStage.USER_INFO_COLLECTION
    iteration: int = 0
    max_iterations: int = 15
    task_completed: bool = False
    delivery_preference: Optional[DeliveryMethod] = None
    user_info_complete: bool = False
    research_complete: bool = False
    # Add missing fields that memory.py expects
    fields_collected: int = 0
    research_data: Optional[Dict[str, Any]] = None
    workflow_completed: bool = False
    last_action: Optional[str] = None
    error_count: int = 0
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    def can_advance_stage(self, target_stage: WorkflowStage) -> bool:
        """Check if can advance to target stage"""
        stage_order = list(WorkflowStage)
        current_idx = stage_order.index(self.current_stage)
        target_idx = stage_order.index(target_stage)
        return target_idx == current_idx + 1


class MemoryState(BaseModel):
    """Complete memory state"""
    user_profile: UserProfile = Field(default_factory=UserProfile)
    research_data: ResearchData = Field(default_factory=ResearchData)
    session_state: SessionState = Field(default_factory=SessionState)
    conversation_history: List[ConversationEntry] = Field(default_factory=list)
    tool_results: List[ToolResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# LLM ACTION MODELS
# ============================================================================

class UserInteractionAction(BaseModel):
    """User interaction action parameters"""
    type: Literal["user_interaction"] = "user_interaction"
    message: str
    expecting: Literal["name", "date", "city", "choice", "text"] = "text"


class FunctionCallAction(BaseModel):
    """Function call action parameters"""
    type: Literal["function_call"] = "function_call"
    tool_name: str
    tool_input: Dict[str, Any] = Field(default_factory=dict)


class PresentInfoAction(BaseModel):
    """Information presentation action parameters"""
    type: Literal["present_info"] = "present_info"
    data: str
    next_step: str = "continue"


class UserChoiceAction(BaseModel):
    """User choice action parameters"""
    type: Literal["user_choice"] = "user_choice"
    prompt: str
    options: List[str]
    context: str = ""


class FinalAnswerAction(BaseModel):
    """Final answer action parameters"""
    type: Literal["final_answer"] = "final_answer"
    summary: str
    status: str = "completed"


# Union of all action types
ActionUnion = Union[
    UserInteractionAction,
    FunctionCallAction, 
    PresentInfoAction,
    UserChoiceAction,
    FinalAnswerAction
]


class LLMResponse(BaseModel):
    """Structured LLM response"""
    reasoning: str
    reasoning_type: ReasoningType
    action: ActionUnion


# ============================================================================
# DECISION MAKING MODELS
# ============================================================================

class ValidationResult(BaseModel):
    """Input validation result"""
    is_valid: bool
    error_message: Optional[str] = None
    processed_value: Any = None


class DecisionResult(BaseModel):
    """Decision making result"""
    decision_type: ActionType
    validation_required: bool = False
    next_step: str = "continue"
    
    # Optional fields based on decision type
    message: Optional[str] = None
    expecting: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    data: Optional[str] = None
    prompt: Optional[str] = None
    options: Optional[List[str]] = None
    context_info: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# TOOL EXECUTION MODELS
# ============================================================================

class MCPToolInfo(BaseModel):
    """MCP tool information"""
    name: str
    description: str
    parameters: Dict[str, Any]


class ToolExecutionRequest(BaseModel):
    """Tool execution request"""
    tool_name: str
    tool_input: Dict[str, Any]
    timeout: Optional[int] = 30


class ToolExecutionResponse(BaseModel):
    """Tool execution response"""
    success: bool
    tool_name: str
    input: Dict[str, Any]
    output: Any = None
    raw_result: Any = None
    error: Optional[str] = None
    exception_type: Optional[str] = None
    execution_time: Optional[float] = None


class EmailRequest(BaseModel):
    """Email sending request"""
    user_data: UserProfile
    historical_events: str
    city_info: str
    to_email: Optional[str] = None


class PDFRequest(BaseModel):
    """PDF generation request"""
    user_data: UserProfile
    historical_events: str
    city_info: str
    filename: Optional[str] = None


# ============================================================================
# PERCEPTION MODELS
# ============================================================================

class PerceptionRequest(BaseModel):
    """Request to perception layer"""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    temperature: float = Field(0.3, ge=0.0, le=2.0)


class PerceptionResponse(BaseModel):
    """Response from perception layer"""
    success: bool
    response: Optional[LLMResponse] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None
    json_error: Optional[str] = None


class HistoricalResearchRequest(BaseModel):
    """Historical research request"""
    day: int = Field(..., ge=1, le=31)
    month: int = Field(..., ge=1, le=12)


class CityResearchRequest(BaseModel):
    """City research request"""  
    city_name: str = Field(..., min_length=2, max_length=100)


# ============================================================================
# CONTEXT AND CONFIGURATION MODELS
# ============================================================================

class AgentConfig(BaseModel):
    """Agent configuration"""
    gemini_api_key: str
    max_iterations: int = 15
    temperature: float = 0.3
    log_level: str = "INFO"
    timeout: int = 30


class SessionContext(BaseModel):
    """Complete session context"""
    current_stage: WorkflowStage
    iteration: int
    user_data: Dict[str, Any]
    research_data: Dict[str, Any] 
    delivery_preference: Optional[str]
    conversation_summary: str
    tools_available: List[str] = Field(default_factory=list)


# ============================================================================
# ERROR MODELS
# ============================================================================

class AgentError(BaseModel):
    """Agent error information"""
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    recoverable: bool = True


class ValidationError(AgentError):
    """Input validation error"""
    error_type: str = "validation_error"
    field_name: Optional[str] = None
    invalid_value: Any = None
# Personal History Agent

A sophisticated 4-layer cognitive agent that collects user personal information, researches historical events, and delivers personalized reports via PDF. Built with structured LLM prompting using Google Gemini AI.

## Overview

The Personal History Agent implements a clean 4-layer cognitive architecture that successfully demonstrates structured AI reasoning, automatic research, and report generation:

1. **Perception Layer**: Google Gemini AI with structured Chain-of-Thought JSON prompting for natural language understanding and reasoning
2. **Memory Layer**: Session state management, user profile storage, and research data persistence
3. **Decision-Making Layer**: Intelligent workflow orchestration with stage transitions and loop detection
4. **Action Layer**: Tool execution for research, PDF generation, and user interaction

## Features

- ✅ **Smart User Information Collection**: Collects exactly 3 fields (name, birth date DD/MM, favorite city) with natural conversation flow
- ✅ **Automatic Historical Research**: Researches real historical events for user's birth date with detailed facts about significant events
- ✅ **Rich City Information**: Gathers fascinating facts about user's favorite city including landmarks, culture, and history
- ✅ **Professional PDF Generation**: Creates formatted PDF reports with personalized content saved to ~/Downloads
- ✅ **Seamless User Experience**: Natural conversation flow with automatic stage progression and intelligent responses
- ✅ **Advanced Loop Detection**: Prevents infinite loops with argument-aware detection for multi-step data collection
- ✅ **Structured LLM Reasoning**: Uses THOUGHT + ACTION format with detailed Chain-of-Thought reasoning for reliability
- ✅ **Stage-Based Workflow**: Clean progression through USER_INFO_COLLECTION → HISTORICAL_RESEARCH → PRESENTATION → DELIVERY_EXECUTION

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Perception     │    │  Memory         │    │ Decision-Making │    │  Action         │
│  (LLM Layer)    │────│  (State Mgmt)   │────│  (Workflow)     │────│  (Execution)    │
│                 │    │                 │    │                 │    │                 │
│ • Gemini AI     │    │ • User Profile  │    │ • Input Valid.  │    │ • MCP Tools     │
│ • Research      │    │ • Session State │    │ • Stage Transi. │    │ • Email/PDF     │
│ • Reasoning     │    │ • Conversation  │    │ • Action Route  │    │ • User I/O      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set API key**: `echo 'GEMINI_API_KEY=your_key_here' > .env`
3. **Run**: `python main.py`

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### 1. Environment Setup

```bash
# Clone or download the project
cd personal_history_agent

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project directory:

```bash
# Create .env file with your API key
echo 'GEMINI_API_KEY=your_actual_gemini_api_key_here' > .env
```

**Required Configuration:**
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

**How to get Gemini API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Click "Get API Key"
3. Create or select a project
4. Copy your API key to the `.env` file

## Usage

### Running the Agent

```bash
# Make sure you're in the project directory with your virtual environment activated
python main.py

# Or run a quick test
python main.py --test
```

### Interaction Flow

1. **Welcome & Introduction**: Agent greets and explains the process
2. **Information Collection**: 
   - Enter your full name
   - Enter date of birth (any format - will be processed automatically)
   - Enter your favorite city
3. **Automatic Research Phase**: Agent automatically researches historical events and city information
4. **Presentation**: View your personalized report with historical events and city facts
5. **Delivery Choice**: Choose PDF generation (saves to ~/Downloads)
6. **Completion**: Receive confirmation of your personalized history report

### Example Session

```
🚀 Starting Personal History Agent...

✅ Gemini AI configured successfully with gemini-2.0-flash!
🎯 4-LAYER COGNITIVE ARCHITECTURE INITIALIZED
============================================================
✅ Perception Layer: LLM reasoning and processing
✅ Memory Layer: State management and persistence
✅ Decision-Making Layer: Workflow orchestration
✅ Action Layer: Tool execution and interaction
============================================================

🤖 Agent: Hello! I'm your Personal History Assistant. To create your personalized historical report, I need some information. First, what is your name?

You: Marie

🤖 Agent: Thanks Marie! What's your birth date? Please use DD/MM format (e.g., 15/08).

You: 14/07

🤖 Agent: Perfect! What's your favorite city?

You: Paris

🔄 Stage Transition: USER_INFO_COLLECTION → HISTORICAL_RESEARCH
🔄 Triggering immediate research after stage transition...
🔄 Automatically proceeding with historical research...
📅 Researching historical events for 14/7...
🏙️ Researching information about Paris...

🤖 Agent: 🔍 RESEARCH COMPLETED! 🔍

📅 HISTORICAL EVENTS FOR 14/07:
• Bastille Day - French National Day (1789): On July 14, 1789, French revolutionaries stormed the Bastille fortress in Paris, marking the beginning of the French Revolution. This event symbolizes the fight for liberty, equality, and fraternity.
• French Revolution Impact: The storming of the Bastille became a powerful symbol of the people's uprising against tyranny and oppression. It led to the abolition of feudalism and the Declaration of the Rights of Man and of the Citizen.
• Gerald Ford's Birth (1913): The 38th President of the United States was born on this day. He became president following Nixon's resignation and is known for his attempts to heal the nation after the Watergate scandal.

🏙️ FASCINATING FACTS ABOUT PARIS:
• Paris, the 'City of Light' and capital of France, is renowned for its art, culture, and romance. Founded as Lutetia by the Gauls, it became Paris in the 4th century and has been France's capital since the 10th century.
• Home to world-famous landmarks including the Eiffel Tower (324m tall, built in 1889), the Louvre Museum (world's largest art museum), Notre-Dame Cathedral, and the Arc de Triomphe along the Champs-Élysées.
• Paris is a global center for art, fashion, gastronomy, and culture. The city houses masterpieces by Picasso, Monet, and da Vinci, has influenced world fashion for centuries, and is known for its café culture and haute cuisine.

🎯 PERSONALIZED CONNECTIONS:
• How historical events relate to your birth date
• Why Paris is special in historical context
• Unique insights about your preferences

📋 Would you like me to send this information via EMAIL or save it as a PDF file?
Type 'email' or 'pdf' to choose your delivery method.

You: pdf

✅ PDF generated successfully! Saved to: /Users/username/Downloads/PersonalHistory_Marie_Report.pdf

📊 SESSION SUMMARY:
Duration: 0:00:11.477445
Interactions: 4  
Final Stage: DELIVERY_EXECUTION
Research Complete: Yes
PDF Generated: PersonalHistory_Marie_Report.pdf
• Why Paris is special in historical context
• Unique insights about your preferences

📋 Would you like me to send this information via EMAIL or save it as a PDF file?
Type 'email' or 'pdf' to choose your delivery method.

You: pdf

✅ Function Result: {
  "success": true,
  "filename": "PersonalHistory_John Smith_Report.pdf",
  "location": "/Users/username/Downloads/PersonalHistory_John Smith_Report.pdf",
  "message": "PDF generated successfully!"
}

You: quit

👋 Goodbye!
```

## Project Structure

```
personal_history_agent/
├── main.py                    # Main orchestrator coordinating all 4 layers
├── perception.py              # Perception Layer - LLM reasoning and processing
├── memory.py                  # Memory Layer - State management and persistence
├── decision_making.py         # Decision-Making Layer - Workflow orchestration
├── action.py                  # Action Layer - Tool execution and interaction
├── models.py                  # Pydantic data models for type validation
├── requirements.txt           # Python dependencies  
├── .env                      # Your API key configuration (create this)
├── final_prompt.md           # Complete structured prompt for submission
├── __init__.py               # Python package initialization
└── README.md                 # This documentation
```

## 4-Layer Cognitive Architecture

### Layer 1: Perception (perception.py)
- **Google Gemini AI Integration**: Uses gemini-2.0-flash for reasoning
- **Structured CoT-JSON Prompting**: THOUGHT + ACTION format
- **Natural Language Processing**: Understands user input and generates responses
- **Context-Aware Reasoning**: Adapts responses based on current workflow stage

### Layer 2: Memory (memory.py)  
- **Session State Management**: Tracks current workflow stage and progress
- **User Data Storage**: Stores name, birth date, favorite city, preferences
- **Conversation History**: Maintains complete interaction log
- **Data Validation**: Ensures completeness and format correctness

### Layer 3: Decision-Making (decision_making.py)
- **Workflow Orchestration**: Routes actions between layers
- **Stage Transition Logic**: Automatic progression through workflow stages  
- **Loop Detection**: Prevents infinite conversation loops
- **Error Recovery**: Handles failures with appropriate fallbacks

### Layer 4: Action (action.py)
- **Tool Execution**: Executes MCP functions and external operations
- **PDF Generation**: Creates formatted reports using ReportLab
- **User Interaction**: Handles input/output and user interface
- **File Operations**: Manages file creation and storage

## Technical Architecture

The agent uses a **modular 4-layer approach** with:

- **Inter-Layer Communication**: Clean APIs between all layers
- **Structured Data Flow**: User Input → Perception → Decision-Making → Action → Memory
- **CoT-JSON Format**: Chain-of-Thought reasoning with structured JSON responses
- **Stage-Based Workflow**: Automatic progression through collection → research → presentation → delivery
- **Loop Detection**: Prevents infinite loops and conversation deadlocks
- **Auto-Flow Management**: Seamless transitions without user confusion

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Ensure your `.env` file exists and contains `GEMINI_API_KEY=your_key`
   - Verify the API key is valid at [Google AI Studio](https://makersuite.google.com/)

2. **PDF creation fails**
   - Ensure `reportlab` is installed: `pip install reportlab`
   - Check that you have write permissions in ~/Downloads
   - Verify the ~/Downloads directory exists

3. **Agent gets stuck in conversation**
   - The system has built-in loop detection - just wait a moment
   - Try typing 'quit' to exit and restart
   - Check console output for any error messages

4. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're in the correct directory
   - Verify Python version compatibility (3.8+)

### Debugging

- Monitor console output for detailed execution logs
- Check `🧠 LLM Response:` sections to see reasoning process
- Use Python debugging: `python -m pdb personal_history_agent.py`
- For API issues, verify your Gemini API key and quotas

## Customization

### Modifying System Prompts

Edit the `get_system_prompt()` method in `personal_history_agent.py` to customize:
- Agent personality and behavior
- Research instructions
- Output formatting
- Reasoning framework

### Adding New MCP Tools

Extend the `call_mcp_function()` method to add new tools:

```python
elif tool_name == "your_custom_tool":
    # Add your custom tool logic here
    return {"success": True, "data": "your_result"}
```

### Customizing PDF Output

Modify the PDF generation section in the `generate_pdf` tool to:
- Change PDF formatting and styling
- Add new sections or data fields
- Customize file naming conventions
- Modify save location

### Adding New Research Sources

Extend the research functions to integrate additional APIs or data sources:

```python
# In the research_historical_events function
async def enhanced_research(self, date_info):
    # Add calls to additional APIs
    # Process and combine data from multiple sources
    return enhanced_results
```

## License

This project is open source. See LICENSE file for details.

## Key Files

- **`main.py`** - Main orchestrator that coordinates all 4 layers
- **`perception.py`** - LLM integration with Google Gemini and structured prompting
- **`memory.py`** - State management, user data storage, and conversation history  
- **`decision_making.py`** - Workflow orchestration, validation, and loop detection
- **`action.py`** - Tool execution, PDF generation, and user interaction
- **`final_prompt.md`** - Complete structured prompt for submission
- **`models.py`** - Pydantic data models for type validation

## Technical Achievements

### Stage Transition Management
- ✅ **Proper Stage Flow**: Fixed timing issues where stage transitions happened prematurely
- ✅ **Action-Driven Transitions**: Stage transitions now properly triggered by action layer results
- ✅ **Auto-Continue Logic**: Seamless progression from data collection to research to presentation

### Loop Detection Intelligence  
- ✅ **Argument-Aware Detection**: Enhanced loop detection considers function arguments, not just tool names
- ✅ **Multi-Field Collection**: Properly handles repeated `gather_user_info` calls for different fields
- ✅ **False Positive Prevention**: No longer incorrectly flags normal workflow progression as loops

### Memory Management
- ✅ **Layer Separation**: Removed inappropriate stage transitions from memory layer
- ✅ **Data Persistence**: Proper storage and retrieval of research data for PDF generation
- ✅ **State Consistency**: Clean state management across all workflow stages

### Research Quality
- ✅ **Rich Historical Data**: Real historical events with detailed descriptions and context
- ✅ **City Information**: Comprehensive facts about landmarks, culture, and history
- ✅ **Personalized Content**: Meaningful connections between user data and historical information

## Support

For issues and questions:

1. **Check the troubleshooting section** above for common issues
2. **Monitor console output** for detailed execution information and stage transitions
3. **Verify API credentials** are correct in `.env` file
4. **Ensure dependencies installed** with `pip install -r requirements.txt`
5. **Check PDF permissions** that ~/Downloads is writable

## Version History

- **v2.0** (Current): Integrated 4-layer architecture with structured LLM prompting
- **v1.0** (Legacy): Modular layer-based implementation

## Development

### Key Components

- **Structured Prompting**: Uses CoT-JSON format with THOUGHT + ACTION patterns
- **MCP Integration**: Built-in Model Context Protocol functions 
- **Stage Management**: Automatic progression through workflow stages
- **Loop Prevention**: Detects and handles conversation loops
- **PDF Generation**: ReportLab integration for formatted reports

### Testing

```bash
# Run the main application to test
python main.py

# Test with sample inputs
# Name: RaghuRam
# Birth Date: 15/08  
# City: Bengaluru
# Choice: pdf
```

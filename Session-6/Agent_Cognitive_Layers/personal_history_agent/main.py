"""
Main Orchestrator - 4-Layer Cognitive Architecture Coordinator
============================================================

This is the main entry point that coordinates all 4 layers:
1. Perception Layer (LLM) - Natural language processing and reasoning
2. Memory Layer - State management and data persistence
3. Decision-Making Layer - Workflow orchestration and routing
4. Action Layer - Tool execution and user interaction

The orchestrator manages the flow between layers and handles the overall workflow.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Import all 4 layers
from perception import PerceptionLayer
from memory import MemoryLayer
from decision_making import DecisionMakingLayer
from action import ActionLayer

class PersonalHistoryAgent:
    """
    Main orchestrator for the 4-layer Personal History Agent
    Coordinates Perception, Memory, Decision-Making, and Action layers
    """
    
    def __init__(self, use_real_llm: bool = True):
        # Initialize all 4 layers
        self.perception = PerceptionLayer(use_real_llm=use_real_llm)
        self.memory = MemoryLayer()
        self.decision_making = DecisionMakingLayer()
        self.action = ActionLayer()
        
        # Orchestrator state
        self.session_active = False
        self.total_interactions = 0
        self.start_time = None
        
        print("🎯 4-LAYER COGNITIVE ARCHITECTURE INITIALIZED")
        print("=" * 60)
        print("✅ Perception Layer: LLM reasoning and processing")
        print("✅ Memory Layer: State management and persistence")
        print("✅ Decision-Making Layer: Workflow orchestration")
        print("✅ Action Layer: Tool execution and interaction")
        print("=" * 60)
    
    async def start_session(self):
        """Start a new agent session"""
        
        self.session_active = True
        self.start_time = datetime.now()
        self.total_interactions = 0
        
        print("🚀 Starting Personal History Agent Session...")
        print("📋 Goal: Collect user info → Research history → Generate report")
        print()
        
        try:
            # Generate initial greeting through Perception layer
            initial_response = await self.perception.generate_initial_greeting()
            
            if initial_response.get("success"):
                # Process through Decision-Making layer
                decision = self.decision_making.process_perception_result(
                    initial_response, 
                    self.memory.get_current_state()
                )
                
                # Execute through Action layer
                action_result = await self.action.execute_action(decision)
                
                if action_result.get("display_to_user"):
                    print(f"🤖 Agent: {action_result['message']}")
                
                # Start main conversation loop
                await self._conversation_loop()
            else:
                print("❌ Failed to initialize session")
                print(f"Error: {initial_response.get('message', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Session ended by user.")
        except Exception as e:
            print(f"\n❌ Session error: {e}")
        finally:
            self._end_session()
    
    async def _conversation_loop(self):
        """Main conversation loop coordinating all 4 layers"""
        
        while self.session_active:
            try:
                # Get user input
                user_input_raw = input("\nYou: ")
                if user_input_raw is None:
                    print("👋 Session ended.")
                    break
                    
                user_input = user_input_raw.strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'stop']:
                    print("👋 Goodbye!")
                    break
                
                self.total_interactions += 1
                
                # LAYER 1: PERCEPTION - Process user input with LLM
                print("🧠 Processing through Perception Layer...")
                current_memory = self.memory.get_current_state()
                context = {
                    "memory_state": current_memory,
                    "user_input": user_input,
                    "interaction_count": self.total_interactions
                }
                
                perception_result = await self.perception.process_user_input(user_input, context)
                
                if perception_result.get("error"):
                    print(f"⚠️ Perception Layer Issue: {perception_result.get('message')}")
                
                # LAYER 2: MEMORY - Update based on perception results
                print("💾 Updating Memory Layer...")
                await self._update_memory_from_perception(perception_result, user_input)
                
                # LAYER 3: DECISION-MAKING - Route and validate actions
                print("🎯 Processing through Decision-Making Layer...")
                current_memory = self.memory.get_current_state()  # Get updated state
                decision_result = self.decision_making.process_perception_result(perception_result, current_memory)
                
                if not decision_result.get("success"):
                    print(f"⚠️ Decision-Making Issue: {decision_result.get('message')}")
                    continue
                
                # LAYER 4: ACTION - Execute the decided action
                print("⚡ Executing through Action Layer...")
                action_result = await self.action.execute_action(decision_result)
                
                # Update memory with action results
                await self._update_memory_from_action(action_result, decision_result)
                
                # Handle stage transitions
                await self._handle_stage_transitions(action_result)
                
                # Check for immediate auto-continue (stage transitions that require immediate research)
                if action_result.get("auto_continue") and action_result.get("stage_transition") == "HISTORICAL_RESEARCH":
                    print("🔄 Triggering immediate research after stage transition...")
                    research_triggered = await self._handle_auto_continue(action_result)
                    if research_triggered:
                        continue
                
                # Check for other auto-continue scenarios
                if await self._handle_auto_continue(action_result):
                    continue
                
                # Display results to user
                await self._display_results(action_result, decision_result)
                
                # Add to conversation history
                assistant_response = action_result.get("message", "Action completed")
                self.memory.add_conversation_entry(user_input, assistant_response, {
                    "perception_success": perception_result.get("success"),
                    "decision_type": decision_result.get("action_type"),
                    "action_success": action_result.get("success")
                })
                
            except KeyboardInterrupt:
                print("\n👋 Session interrupted by user.")
                break
            except Exception as e:
                print(f"❌ Conversation loop error: {e}")
                # Try to continue gracefully
                continue
    
    async def _update_memory_from_perception(self, perception_result: Dict[str, Any], user_input: str):
        """Update memory based on perception layer results"""
        
        if not perception_result.get("success"):
            return
        
        action = perception_result.get("action", {})
        
        # Handle function calls that indicate data collection
        if "FUNCTION_CALL" in action:
            func_call = action["FUNCTION_CALL"]
            if func_call.get("tool_name") == "gather_user_info":
                arguments = func_call.get("arguments", {})
                
                # Update memory with user info
                for field in ["name", "birth_date", "favorite_city"]:
                    if field in arguments:
                        self.memory.update_user_info(field, arguments[field])
                
                if "field" in arguments and "value" in arguments:
                    self.memory.update_user_info(arguments["field"], arguments["value"])
    
    async def _update_memory_from_action(self, action_result: Dict[str, Any], decision_result: Dict[str, Any]):
        """Update memory based on action layer results"""
        
        # Store research data
        if action_result.get("research_type"):
            research_type = action_result["research_type"]
            self.memory.store_research_data(research_type, action_result)
        
        # Update user info from successful field storage
        if action_result.get("field_stored"):
            field = action_result["field_stored"]
            value = action_result["value"]
            self.memory.update_user_info(field, value)
        
        # Handle delivery preferences
        if decision_result.get("action_type") == "function_call":
            tool_name = decision_result.get("tool_name")
            if tool_name in ["generate_pdf", "send_email"]:
                delivery_method = "pdf" if tool_name == "generate_pdf" else "email"
                self.memory.update_user_info("delivery_preference", delivery_method)
    
    async def _handle_stage_transitions(self, action_result: Dict[str, Any]):
        """Handle automatic stage transitions"""
        
        current_stage = self.memory.get_current_state()["current_stage"]
        memory_state = self.memory.get_current_state()
        
        # Check if stage transition is needed
        should_transition, next_stage = self.decision_making.should_transition_stage(
            current_stage, action_result, memory_state
        )
        
        if should_transition and next_stage:
            print(f"🔄 Stage Transition: {current_stage} → {next_stage}")
            self.memory.transition_stage(next_stage, f"Auto-transition from {current_stage}")
    
    async def _display_results(self, action_result: Dict[str, Any], decision_result: Dict[str, Any]):
        """Display appropriate results to the user"""
        
        if action_result.get("display_to_user"):
            message = action_result.get("message", "")
            
            # Add special formatting for different action types
            action_type = action_result.get("action_type", "")
            
            if action_type == "loop_recovery":
                print(f"🔄 {message}")
            elif action_type == "error_recovery":
                print(f"⚠️ {message}")
            elif action_result.get("is_recovery"):
                print(f"🛠️ {message}")
            else:
                print(f"🤖 Agent: {message}")
    
    async def _handle_auto_continue(self, action_result: Dict[str, Any]) -> bool:
        """Handle scenarios where the agent should auto-continue without user input"""
        
        current_stage = self.memory.get_current_state()["current_stage"]
        
        # Check if this action result indicates we should auto-continue
        if action_result.get("auto_continue") or action_result.get("stage_transition") == "HISTORICAL_RESEARCH":
            current_stage = "HISTORICAL_RESEARCH"  # Override current stage since transition is happening
        
        # Auto-continue for research stage
        research_data = self.memory.get_research_data() or {}
        
        if (current_stage == "HISTORICAL_RESEARCH" and 
            not research_data.get("historical_events")):
            
            print("🔄 Automatically proceeding with historical research...")
            
            # Get user's birth date for research
            current_state = self.memory.get_current_state()
            birth_date = current_state.get("birth_date", "") if current_state else ""
            day, month = self._parse_birth_date(birth_date)
            
            print(f"📅 Researching historical events for {day}/{month}...")
            
            # Execute research
            research_args = {"day": day, "month": month}
            research_result = await self.action._handle_research_historical_events(research_args, current_stage)
            
            # Store research results
            self.memory.store_research_data("historical_events", research_result)
            
            # Auto-continue with city research
            current_state = self.memory.get_current_state()
            city = current_state.get("favorite_city", "") if current_state else ""
            if city:
                print(f"🏙️ Researching information about {city}...")
                city_result = await self.action._handle_research_city_info({"city": city}, current_stage)
                self.memory.store_research_data("city_info", city_result)
            
            # Present results
            research_data = self.memory.get_research_data()
            user_data = self.memory.get_user_profile_dict()
            presentation = self.action.format_presentation(research_data, user_data)
            print(f"🤖 Agent: {presentation}")
            
            # Transition to presentation stage
            self.memory.transition_stage("PRESENTATION", "Research completed, presenting results")
            
            return True
        
        return False
    
    def _parse_birth_date(self, birth_date: str) -> tuple:
        """Parse birth date to extract day and month"""
        
        parse_result = self.action.parse_date_input(birth_date)
        
        if parse_result.get("valid"):
            return parse_result["day"], parse_result["month"]
        else:
            # Default fallback
            return 15, 6
    
    def _end_session(self):
        """Clean up and end the session"""
        
        self.session_active = False
        end_time = datetime.now()
        
        if self.start_time:
            duration = end_time - self.start_time
            print(f"\n📊 SESSION SUMMARY:")
            print(f"Duration: {duration}")
            print(f"Interactions: {self.total_interactions}")
            print(f"Final Stage: {self.memory.get_current_state()['current_stage']}")
            
            # Display memory summary
            print(f"\n{self.memory.get_memory_summary()}")
            
            # Display execution summary
            action_summary = self.action.get_execution_summary()
            print(f"\n🔧 Action Layer: {action_summary['total_executions']} tools executed")
            
            if action_summary.get("last_pdf_generated"):
                print(f"📄 PDF Generated: {action_summary['last_pdf_generated']}")
    
    async def quick_test(self, test_data: Optional[Dict] = None):
        """Run a quick test with predefined data"""
        
        test_data = test_data or {
            "name": "Test User",
            "birth_date": "15/08/1990",
            "favorite_city": "London",
            "delivery": "pdf"
        }
        
        print("🧪 Running Quick Test...")
        
        # Simulate user interactions - might need more responses depending on LLM behavior
        interactions = [
            test_data["name"],
            test_data["birth_date"],
            test_data["favorite_city"],
            test_data["delivery"],
            "quit"  # Ensure we can exit gracefully
        ]
        
        # Mock the input for testing
        import sys
        from io import StringIO
        
        original_input = input
        
        def mock_input(prompt):
            if hasattr(mock_input, 'responses') and mock_input.responses:
                response = mock_input.responses.pop(0)
                print(f"{prompt}{response}")
                return response
            # End the session gracefully when no more responses
            return "quit"
        
        mock_input.responses = interactions.copy()
        
        try:
            # Replace input temporarily
            import builtins
            builtins.input = mock_input
            
            # Start session
            await self.start_session()
            
        finally:
            # Restore original input
            builtins.input = original_input

async def main():
    """Main entry point"""
    
    print("📋 Make sure to set your GEMINI_API_KEY in .env file!")
    print("🚀 Starting Personal History Agent...\n")
    
    # Initialize and start the agent
    agent = PersonalHistoryAgent(use_real_llm=True)
    
    # Check if we should run a quick test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        await agent.quick_test()
    else:
        await agent.start_session()

if __name__ == "__main__":
    asyncio.run(main())
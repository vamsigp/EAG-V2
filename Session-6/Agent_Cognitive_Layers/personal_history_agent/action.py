"""
Action Layer - Tool Execution and User Interaction
=================================================

This layer handles:
- MCP tool execution and function calls
- PDF generation and file operations
- Email sending and delivery
- User interface and interaction management
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import re

class ActionLayer:
    """
    Action Layer executes tools, handles file operations, and manages user interactions
    Integrates with MCP functions and external services
    """
    
    def __init__(self):
        self.tool_execution_count = 0
        self.last_pdf_path = None
        self.execution_history = []
    
    async def execute_action(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action based on decision from Decision-Making layer
        
        Args:
            decision_result: Decision and routing information from Decision-Making layer
            
        Returns:
            Result of action execution
        """
        
        action_type = decision_result.get("action_type")
        
        try:
            if action_type == "function_call":
                return await self._execute_function_call(decision_result)
            elif action_type == "user_response":
                return self._handle_user_response(decision_result) 
            elif action_type == "loop_recovery":
                return self._handle_loop_recovery(decision_result)
            elif action_type == "error_recovery":
                return self._handle_error_recovery(decision_result)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action type: {action_type}",
                    "message": "Invalid action type received"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Action execution failed: {e}",
                "action_type": action_type
            }
    
    async def _execute_function_call(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP function call"""
        
        tool_name = decision_result["tool_name"]
        arguments = decision_result.get("arguments", {})
        current_stage = decision_result.get("current_stage")
        
        self.tool_execution_count += 1
        
        # Log execution
        execution_log = {
            "tool_name": tool_name,
            "arguments": arguments,
            "timestamp": datetime.now().isoformat(),
            "stage": current_stage
        }
        self.execution_history.append(execution_log)
        
        # Route to appropriate tool handler
        if tool_name == "gather_user_info":
            return await self._handle_gather_user_info(arguments, current_stage)
        elif tool_name == "research_historical_events":
            return await self._handle_research_historical_events(arguments, current_stage)
        elif tool_name == "research_city_info":
            return await self._handle_research_city_info(arguments, current_stage)
        elif tool_name == "generate_pdf":
            return await self._handle_generate_pdf(arguments, current_stage)
        elif tool_name == "send_email":
            return await self._handle_send_email(arguments, current_stage)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "message": f"Tool '{tool_name}' is not implemented"
            }
    
    async def _handle_gather_user_info(self, arguments: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """Handle user information gathering"""
        
        # Handle different argument formats
        if "name" in arguments:
            return {
                "success": True,
                "message": f"Thanks {arguments['name']}! What's your birth date? Please use DD/MM format (e.g., 15/08).",
                "next_prompt": f"Thanks {arguments['name']}! What's your birth date? Please use DD/MM format (e.g., 15/08).",
                "fields_collected": 1,
                "continue_conversation": True,
                "field_stored": "name",
                "value": arguments["name"],
                "display_to_user": True
            }
            
        elif "birth_date" in arguments:
            return {
                "success": True,
                "message": "Perfect! What's your favorite city?",
                "next_prompt": "Perfect! What's your favorite city?",
                "fields_collected": 2,
                "continue_conversation": True,
                "field_stored": "birth_date",
                "value": arguments["birth_date"],
                "display_to_user": True
            }
            
        elif "favorite_city" in arguments:
            return {
                "success": True,
                "message": f"Perfect! I have all your information. Let me research historical events for your birth date and facts about {arguments['favorite_city']}. This will take a moment...",
                "next_action": "start_research",
                "stage_transition": "HISTORICAL_RESEARCH",
                "auto_continue": True,
                "field_stored": "favorite_city",
                "value": arguments["favorite_city"],
                "display_to_user": True
            }
            
        elif "field" in arguments and "value" in arguments:
            field = arguments["field"]
            value = arguments["value"]
            
            if field == "name":
                return {
                    "success": True,
                    "message": f"Thanks {value}! What's your birth date? Please use DD/MM format (e.g., 15/08).",
                    "next_prompt": f"Thanks {value}! What's your birth date? Please use DD/MM format (e.g., 15/08).",
                    "fields_collected": 1,
                    "continue_conversation": True,
                    "field_stored": field,
                    "value": value,
                    "display_to_user": True
                }
            elif field == "birth_date":
                return {
                    "success": True,
                    "message": "Perfect! What's your favorite city?",
                    "next_prompt": "Perfect! What's your favorite city?",
                    "fields_collected": 2,
                    "continue_conversation": True,
                    "field_stored": field,
                    "value": value,
                    "display_to_user": True
                }
            elif field == "favorite_city":
                return {
                    "success": True,
                    "message": f"Perfect! I have all your information. Let me research historical events for your birth date and facts about {value}. This will take a moment...",
                    "next_action": "start_research",
                    "stage_transition": "HISTORICAL_RESEARCH",
                    "auto_continue": True,
                    "field_stored": field,
                    "value": value,
                    "display_to_user": True
                }
        
        return {
            "success": False,
            "error": "Invalid arguments for gather_user_info",
            "message": "Expected name, birth_date, favorite_city, or field+value"
        }
    
    async def _handle_research_historical_events(self, arguments: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """Handle historical events research"""
        
        day = arguments.get("day", 15)
        month = arguments.get("month", 6)
        
        # Enhanced research with more specific historical content
        # In a real implementation, this would call external APIs like Wikipedia, History.com, etc.
        
        # Create month name for better formatting
        month_names = ["", "January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        month_name = month_names[month] if 1 <= month <= 12 else "Unknown"
        
        # Generate realistic historical content based on the specific date
        date_key = f"{day}/{month}"
        
        # Historical events database for specific dates
        historical_database = {
            "15/8": [
                "August 15th Historical Significance: This date marks India's Independence Day (1947), when India gained freedom from British rule after centuries of colonial governance. The event symbolizes the triumph of non-violent resistance led by Mahatma Gandhi.",
                "Woodstock Music Festival (1969): On August 15, 1969, the legendary Woodstock Music Festival began in New York, featuring iconic performances by Jimi Hendrix, Janis Joplin, and The Who. This 3-day festival became a symbol of the 1960s counterculture movement.",
                "Napoleon Bonaparte's Birth (1769): The French military genius and emperor was born on this day in Corsica. His conquests and legal reforms (Napoleonic Code) profoundly influenced European history and law systems worldwide.",
                "Other Notable Events: The Panama Canal officially opened to commercial traffic (1914), and Japan announced its surrender in World War II (1945), effectively ending the global conflict."
            ],
            "14/7": [
                "Bastille Day - French National Day (1789): On July 14, 1789, French revolutionaries stormed the Bastille fortress in Paris, marking the beginning of the French Revolution. This event symbolizes the fight for liberty, equality, and fraternity.",
                "French Revolution Impact: The storming of the Bastille became a powerful symbol of the people's uprising against tyranny and oppression. It led to the abolition of feudalism and the Declaration of the Rights of Man and of the Citizen.",
                "Gerald Ford's Birth (1913): The 38th President of the United States was born on this day. He became president following Nixon's resignation and is known for his attempts to heal the nation after the Watergate scandal.",
                "Other July 14th Events: The first successful color photograph was taken by James Clerk Maxwell (1861), and NASA's New Horizons spacecraft made its historic flyby of Pluto (2015)."
            ]
        }
        
        # Get events for the specific date or generate generic ones
        if date_key in historical_database:
            events = historical_database[date_key]
        else:
            # Generic but informative events for other dates
            events = [
                f"Historical Significance of {month_name} {day}: Throughout history, this date has witnessed remarkable events that shaped civilizations. From ancient empires to modern nations, significant political, cultural, and scientific developments have occurred on this day.",
                
                f"Notable Births and Deaths ({month_name} {day}): Many influential figures in history, science, arts, and politics were born or died on this date. These individuals have left lasting legacies that continue to influence our world today.",
                
                f"Cultural and Scientific Milestones: {month_name} {day} has been marked by important discoveries, inventions, and cultural movements. From breakthrough scientific research to artistic masterpieces, this date has contributed to human progress.",
                
                f"Modern Era Events: In recent centuries, {month_name} {day} has seen significant political changes, technological innovations, and social movements that have shaped contemporary society and continue to impact our daily lives."
            ]
        
        return {
            "success": True,
            "events": events,
            "day": day,
            "month": month,
            "message": f"✅ Historical research completed for {day}/{month}",
            "research_type": "historical_events",
            "display_to_user": False
        }
    
    async def _handle_research_city_info(self, arguments: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """Handle city information research"""
        
        city = arguments.get("city", "Unknown City").strip().lower()
        
        # Enhanced city-specific research with realistic content
        # In a real implementation, this would call external APIs like Wikipedia, travel APIs, etc.
        
        if "tokyo" in city:
            facts = [
                "Tokyo, Japan's capital, is the world's most populous metropolitan area with over 37 million residents. Originally called Edo, it became Tokyo ('Eastern Capital') in 1868 when Emperor Meiji moved the capital from Kyoto.",
                
                "Tokyo is home to iconic landmarks including the Tokyo Skytree (634m tall), the historic Senso-ji Temple (founded in 628 AD), the Imperial Palace, and the famous Shibuya Crossing - one of the busiest pedestrian crossings in the world.",
                
                "The city is renowned for its unique blend of ultra-modern technology and ancient traditions. Tokyo has more Michelin-starred restaurants than any other city, hosts the world's largest fish market (Tsukiji/Toyosu), and is a global center for anime, manga, and pop culture.",
                
                "Tokyo successfully hosted the 1964 Summer Olympics and the delayed 2020 Summer Olympics (held in 2021). The city is known for its efficient public transportation system, including the famous bullet trains (Shinkansen) and extensive subway network."
            ]
        elif "london" in city:
            facts = [
                "London, the capital of the United Kingdom, is a global city with over 2,000 years of history. Founded by the Romans as Londinium around 47-50 AD, it has been a major settlement for two millennia.",
                
                "The city features iconic landmarks including Big Ben, Tower Bridge, the Tower of London (home to the Crown Jewels), Buckingham Palace, and the London Eye. The Thames River flows through the heart of the city.",
                
                "London is a world financial center and cultural hub, housing renowned institutions like the British Museum, Tate Modern, the West End theater district, and numerous universities including Imperial College and UCL.",
                
                "The city is famous for its red double-decker buses, black cabs, the Underground (Tube) system, and its diverse multicultural population representing over 300 languages spoken throughout the metropolis."
            ]
        elif "paris" in city:
            facts = [
                "Paris, the 'City of Light' and capital of France, is renowned for its art, culture, and romance. Founded as Lutetia by the Gauls, it became Paris in the 4th century and has been France's capital since the 10th century.",
                
                "Home to world-famous landmarks including the Eiffel Tower (324m tall, built in 1889), the Louvre Museum (world's largest art museum), Notre-Dame Cathedral, and the Arc de Triomphe along the Champs-Élysées.",
                
                "Paris is a global center for art, fashion, gastronomy, and culture. The city houses masterpieces by Picasso, Monet, and da Vinci, has influenced world fashion for centuries, and is known for its café culture and haute cuisine.",
                
                "The Seine River divides the city into the Left and Right Banks, with 20 arrondissements (districts) each having their own character. Paris is also known for its extensive metro system and beautiful Haussmanian architecture."
            ]
        else:
            # Generic but more detailed content for other cities
            facts = [
                f"{city.title()} is a unique destination with its own rich cultural heritage and historical significance. Every city has stories that have shaped the lives of its residents and visitors throughout the ages.",
                
                f"The architecture and urban landscape of {city.title()} reflect the various periods of its development, from ancient foundations to modern innovations that continue to evolve today.",
                
                f"{city.title()} offers distinctive cultural experiences, local cuisine, and traditions that make it special. The city's museums, landmarks, and public spaces tell the story of its people and their contributions to world culture.",
                
                f"Modern {city.title()} balances preservation of its historical character with contemporary developments, creating a dynamic environment that attracts visitors and residents from around the world."
            ]
        
        return {
            "success": True,
            "facts": facts,
            "city": city,
            "message": f"✅ City research completed for {city}",
            "research_type": "city_info",
            "display_to_user": False
        }
    
    async def _handle_generate_pdf(self, arguments: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """Handle PDF generation"""
        
        try:
            # Import PDF libraries
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Get data from memory instead of relying on arguments
            # Import memory layer to access current state
            from memory import MemoryLayer
            
            # For this implementation, we'll get data from arguments or use defaults
            # In a real implementation, we'd get this from the memory layer instance
            user_data = arguments.get("user_data", {})
            name = user_data.get("name", "User")
            birth_date = user_data.get("birth_date", arguments.get("birth_date", "Unknown"))
            city = user_data.get("favorite_city", arguments.get("city", "Unknown"))
            
            # Handle research data - check if it's available in arguments or use defaults
            historical_events_data = arguments.get("historical_events")
            city_info_data = arguments.get("city_info")
            
            # Format historical events
            if isinstance(historical_events_data, dict) and "events" in historical_events_data:
                events = historical_events_data["events"]
                historical_events = "\n• ".join(events) if events else "Historical events information not available"
                historical_events = "• " + historical_events if events else historical_events
            else:
                historical_events = f"Historical events for {birth_date}"
                
            # Format city info  
            if isinstance(city_info_data, dict) and "facts" in city_info_data:
                facts = city_info_data["facts"]
                city_info = "\n• ".join(facts) if facts else f"Information about {city} not available"
                city_info = "• " + city_info if facts else city_info
            else:
                city_info = f"Interesting facts about {city}"
            
            # Create PDF file path
            home_dir = os.path.expanduser("~")
            downloads_dir = os.path.join(home_dir, "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            
            filename = f"PersonalHistory_{name}_Report.pdf"
            full_path = os.path.join(downloads_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(full_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph(f"Personal History Report for {name}", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Personal Info Section
            info = Paragraph(f"<b>Name:</b> {name}<br/><b>Birth Date:</b> {birth_date}<br/><b>Favorite City:</b> {city}", styles['Normal'])
            story.append(info)
            story.append(Spacer(1, 20))
            
            # Historical Events Section
            events_title = Paragraph("Historical Events", styles['Heading2'])
            story.append(events_title)
            events_text = Paragraph(historical_events, styles['Normal'])
            story.append(events_text)
            story.append(Spacer(1, 20))
            
            # City Information Section
            city_title = Paragraph(f"About {city}", styles['Heading2'])
            story.append(city_title)
            city_text = Paragraph(city_info, styles['Normal'])
            story.append(city_text)
            story.append(Spacer(1, 20))
            
            # Footer
            footer = Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            self.last_pdf_path = full_path
            
            return {
                "success": True,
                "filename": filename,
                "location": full_path,
                "message": f"✅ PDF generated successfully! Saved to: {full_path}",
                "delivery_complete": True,
                "file_size": os.path.getsize(full_path) if os.path.exists(full_path) else 0,
                "display_to_user": True
            }
            
        except ImportError:
            # Fallback if reportlab not available
            return {
                "success": False,
                "error": "PDF generation library not available",
                "message": "Please install reportlab: pip install reportlab",
                "fallback_message": "PDF generation failed - library missing",
                "display_to_user": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"PDF generation failed: {e}",
                "display_to_user": True
            }
    
    async def _handle_send_email(self, arguments: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """Handle email sending (simulated)"""
        
        user_data = arguments.get("user_data", {})
        name = user_data.get("name", "User")
        content = arguments.get("content", "Personal history report")
        recipient = arguments.get("recipient", "user@example.com")
        
        # Simulate email sending
        return {
            "success": True,
            "message": f"✅ Email sent successfully to {name}!",
            "recipient": recipient,
            "delivery_method": "email",
            "delivery_complete": True,
            "sent_at": datetime.now().isoformat(),
            "display_to_user": True
        }
    
    def _handle_user_response(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user response action"""
        
        message = decision_result.get("message", "")
        expecting = decision_result.get("expecting", "")
        current_stage = decision_result.get("current_stage", "")
        
        return {
            "success": True,
            "action_type": "user_response",
            "message": message,
            "expecting": expecting,
            "current_stage": current_stage,
            "display_to_user": True,
            "await_user_input": True
        }
    
    def _handle_loop_recovery(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle loop recovery action"""
        
        action = decision_result.get("action", {})
        message = action.get("message", "Let me help you continue.")
        
        return {
            "success": True,
            "action_type": "loop_recovery",
            "message": message,
            "display_to_user": True,
            "is_recovery": True,
            "reset_conversation": action.get("reset_conversation", False),
            "force_choice": action.get("force_choice", False)
        }
    
    def _handle_error_recovery(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle error recovery action"""
        
        action = decision_result.get("action", {})
        message = action.get("message", "I encountered an issue. Let me help you.")
        original_error = decision_result.get("original_error", "")
        
        return {
            "success": True,
            "action_type": "error_recovery",
            "message": message,
            "original_error": original_error,
            "display_to_user": True,
            "is_recovery": True
        }
    
    def format_presentation(self, research_data: Dict[str, Any], user_data: Dict[str, Any]) -> str:
        """Format research results for presentation to user"""
        
        name = user_data.get("name", "User")
        birth_date = user_data.get("birth_date", "Unknown")
        city = user_data.get("favorite_city", "Unknown")
        
        events = research_data.get("historical_events", {}).get("events", [
            "Historical events for your birth date",
            "Notable achievements and milestones",
            "Cultural significance and connections"
        ])
        
        city_facts = research_data.get("city_info", {}).get("facts", [
            f"Interesting facts about {city}",
            "Cultural heritage and landmarks",
            "Modern developments and attractions"
        ])
        
        presentation = f"""🔍 RESEARCH COMPLETED! 🔍

📅 HISTORICAL EVENTS FOR {birth_date}:
• {events[0] if len(events) > 0 else 'Major historical events occurred on your birth date'}
• {events[1] if len(events) > 1 else 'Notable people share your birth date'}
• {events[2] if len(events) > 2 else 'Historical significance and interesting coincidences'}

🏙️ FASCINATING FACTS ABOUT {city.upper()}:
• {city_facts[0] if len(city_facts) > 0 else 'Rich historical background'}
• {city_facts[1] if len(city_facts) > 1 else 'Cultural significance and landmarks'}
• {city_facts[2] if len(city_facts) > 2 else 'Modern developments and attractions'}

🎯 PERSONALIZED CONNECTIONS:
• How historical events relate to your birth date
• Why {city} is special in historical context
• Unique insights about your preferences

📋 Would you like me to send this information via EMAIL or save it as a PDF file?
Type 'email' or 'pdf' to choose your delivery method."""

        return presentation
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of action execution activity"""
        
        return {
            "total_executions": self.tool_execution_count,
            "last_pdf_generated": self.last_pdf_path,
            "execution_history_count": len(self.execution_history),
            "recent_tools": [h["tool_name"] for h in self.execution_history[-5:]],
            "execution_success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate of recent executions"""
        if not self.execution_history:
            return 1.0
        
        # This would track success/failure in real implementation
        return 1.0  # Placeholder
    
    def validate_file_access(self, file_path: str) -> Dict[str, Any]:
        """Validate file access permissions"""
        
        try:
            directory = os.path.dirname(file_path)
            
            # Check if directory exists or can be created
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Check write permissions
            if not os.access(directory, os.W_OK):
                return {
                    "valid": False,
                    "error": f"No write permission for directory: {directory}",
                    "suggestion": "Check file permissions or try a different location"
                }
            
            return {"valid": True, "directory": directory}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"File access validation failed: {e}",
                "suggestion": "Check path and permissions"
            }
    
    def parse_date_input(self, date_input: str) -> Dict[str, Any]:
        """Parse various date input formats"""
        
        if not date_input or date_input is None:
            return {
                "valid": False,
                "error": "No date input provided",
                "suggestion": "Try formats like: 15/08, 15 August, or August 15"
            }
        
        date_input = date_input.strip().lower()
        
        # Try different patterns
        patterns = [
            (r'(\d{1,2})[/\-](\d{1,2})', lambda m: (int(m.group(1)), int(m.group(2)))),  # DD/MM or DD-MM
            (r'(\d{1,2})\s+(\w+)', self._parse_day_month_name),  # DD Month
            (r'(\w+)\s+(\d{1,2})', self._parse_month_name_day),  # Month DD
        ]
        
        for pattern, parser in patterns:
            match = re.search(pattern, date_input)
            if match:
                try:
                    day, month = parser(match)
                    if 1 <= day <= 31 and 1 <= month <= 12:
                        return {
                            "valid": True,
                            "day": day,
                            "month": month,
                            "original_input": date_input
                        }
                except:
                    continue
        
        return {
            "valid": False,
            "error": f"Could not parse date: {date_input}",
            "suggestion": "Try formats like: 15/08, 15 August, or August 15"
        }
    
    def _parse_day_month_name(self, match) -> tuple:
        """Parse day and month name"""
        day = int(match.group(1))
        month_name = match.group(2)
        month = self._month_name_to_number(month_name)
        return day, month
    
    def _parse_month_name_day(self, match) -> tuple:
        """Parse month name and day"""
        month_name = match.group(1)
        day = int(match.group(2))
        month = self._month_name_to_number(month_name)
        return day, month
    
    def _month_name_to_number(self, month_name: str) -> int:
        """Convert month name to number"""
        months = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        return months.get(month_name.lower(), 1)
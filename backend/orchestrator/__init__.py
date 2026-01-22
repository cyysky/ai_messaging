"""
Message Orchestrator - Handles incoming messages and coordinates AI agents

This module processes incoming user messages, manages chat history,
and coordinates responses using various agents (report_agent, etc.)

Configure via environment variables:
- LITELLM_BASEURL: The base URL for LiteLLM API
- LITELLM_API_KEY: The API key for authentication
- LITELLM_MODEL: The model to use (e.g., gpt-4, gpt-3.5-turbo-1106)
- CHAT_HISTORY_MAX: Maximum number of chat history entries (default: 50)

Logging: Uses orchestrator_logger from init_logs
        Logs are written to logs/orchestrator.log
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from litellm import completion

# Import orchestrator logger from init_logs
# NOTE: If adding new loggers, define them in init_logs.py following the pattern:
#   orchestrator_logger = setup_logger("orchestrator", "orchestrator.log")
from init_logs import orchestrator_logger

load_dotenv()

# Configuration
BASE_URL = os.environ.get("LITELLM_BASEURL", "")
API_KEY = os.environ.get("LITELLM_API_KEY", "")
MODEL = os.environ.get("LITELLM_MODEL", "gpt-3.5-turbo-1106")
CHAT_HISTORY_MAX = int(os.environ.get("CHAT_HISTORY_MAX", "50"))


class ChatHistory:
    """Manages chat history with max limit, keeping only user and assistant messages."""

    def __init__(self, max_entries: int = 50):
        self.max_entries = max_entries
        self.history: List[Dict[str, str]] = []

    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        self.history.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        self._trim_history()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to history."""
        self.history.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        self._trim_history()

    def add_message(self, role: str, content: str) -> None:
        """Add a message with specified role."""
        if role in ["user", "assistant"]:
            self.history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })
            self._trim_history()

    def _trim_history(self) -> None:
        """Trim history to max entries, keeping most recent."""
        # Filter to only user and assistant messages
        filtered = [m for m in self.history if m["role"] in ["user", "assistant"]]

        # Trim to max entries
        if len(filtered) > self.max_entries:
            self.history = filtered[-self.max_entries:]
        else:
            self.history = filtered

    def get_history(self) -> List[Dict[str, str]]:
        """Get history as list of message dicts (without timestamp for API calls)."""
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.history
        ]

    def clear(self) -> None:
        """Clear all history."""
        self.history = []

    def __len__(self) -> int:
        return len(self.history)

    def __repr__(self) -> str:
        return f"ChatHistory({len(self.history)} messages, max={self.max_entries})"


class Agent:
    """Represents a registered agent with its capabilities."""

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        tools: List[Dict],
        available_functions: Dict[str, Callable],
        chat_func: Callable[[str, list, int], Tuple[str, list]]
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tools = tools
        self.available_functions = available_functions
        self.chat_func = chat_func


class MessageOrchestrator:
    """Orchestrates message handling and AI agent coordination."""

    def __init__(self, max_history: int = None):
        self.agents: Dict[str, Agent] = {}
        self.conversation_histories: Dict[int, ChatHistory] = {}  # user_id -> ChatHistory
        self.max_history = max_history or CHAT_HISTORY_MAX

    def get_history(self, user_id: int) -> ChatHistory:
        """Get or create chat history for a user."""
        if user_id not in self.conversation_histories:
            self.conversation_histories[user_id] = ChatHistory(max_entries=self.max_history)
        return self.conversation_histories[user_id]

    def register_agent(self, agent: Agent) -> None:
        """Register a new agent."""
        self.agents[agent.name] = agent
        orchestrator_logger.info(f"Registered agent: {agent.name}")

    def list_agents(self) -> str:
        """List all registered agents."""
        if not self.agents:
            return "No agents registered."

        result = "Available Agents:\n"
        for name, agent in self.agents.items():
            result += f"  - {name}: {agent.description}\n"
        return result.strip()

    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get all agent capabilities for planning decisions."""
        capabilities = {}
        for name, agent in self.agents.items():
            capabilities[name] = {
                "description": agent.description,
                "tools": [t.get("function", {}).get("name") for t in agent.tools if t.get("function")],
            }
        return capabilities

    def clear_history(self, user_id: int) -> None:
        """Clear chat history for a specific user."""
        if user_id in self.conversation_histories:
            self.conversation_histories[user_id].clear()

    def _should_use_agent(self, user_message: str) -> Optional[str]:
        """Determine if an agent should be used based on message content."""
        message_lower = user_message.lower()

        # Check for report-related keywords
        report_keywords = [
            "report", "my reports", "list reports", "show report",
            "update report", "edit report", "create report", "new report",
            "submit report", "file a report", "make a report",
            "water flow", "broken", "repair", "maintenance", "facilities issue"
        ]
        if any(kw in message_lower for kw in report_keywords):
            if "report_agent" in self.agents:
                return "report_agent"

        return None

    def process_message(self, user_id: int, user_message: str) -> str:
        """Process an incoming message and return the AI response."""
        # Get user's chat history
        chat_history = self.get_history(user_id)

        # Add user message to history
        chat_history.add_user_message(user_message)

        orchestrator_logger.info(f"User {user_id}: {user_message[:100]}... (history_len={len(chat_history)})")

        # Check if any agent should handle this message
        agent_name = self._should_use_agent(user_message)

        if agent_name and agent_name in self.agents:
            agent = self.agents[agent_name]
            orchestrator_logger.info(f"Routing to agent: {agent_name}")

            try:
                # Get history for agent (as list of message dicts)
                history_list = chat_history.get_history()

                # Call the agent's chat function with user_id
                orchestrator_logger.debug(f"Calling agent.chat_func with user_id={user_id}")
                response, new_history = agent.chat_func(
                    user_message,
                    history_list,
                    max_turns=5,
                    user_id=user_id  # Pass user_id to the agent
                )

                # Update chat history with agent's response
                chat_history.add_assistant_message(response)

                return response

            except Exception as e:
                orchestrator_logger.error(f"Agent error in {agent_name}: {e}")
                return f"I apologize, but I encountered an error while processing your request: {str(e)}"

        # Default: handle with general conversational AI
        return self._handle_conversation(user_id, user_message)

    def _handle_conversation(self, user_id: int, user_message: str) -> str:
        """Handle general conversation without specific agents."""
        chat_history = self.get_history(user_id)
        history_list = chat_history.get_history()

        casual_prompt = """You are a helpful AI assistant for a messaging application.
Respond to the user's message in a friendly, helpful way.
Keep your response concise and conversational.
You can help with various tasks including managing reports and general questions.
Plain text only, no special characters or emojis."""

        try:
            messages = [
                {"role": "system", "content": casual_prompt},
            ] + history_list

            response = completion(
                model=MODEL,
                base_url=BASE_URL,
                api_key=API_KEY,
                messages=messages,
            )

            content = response.choices[0].message.content or "I didn't understand that. Can you try again?"

            # Clean content
            content = content.encode('ascii', 'ignore').decode('ascii')

            # Add assistant response to history
            chat_history.add_assistant_message(content)

            return content

        except Exception as e:
            orchestrator_logger.error(f"Conversation error: {e}")
            return "I apologize, but I'm having trouble responding right now. Please try again later."

    def handle_twilio_message(self, user_id: int, message_content: str) -> str:
        """Handle incoming Twilio message - wrapper for process_message."""
        return self.process_message(user_id, message_content)


# Global orchestrator instance
_orchestrator: Optional[MessageOrchestrator] = None


def get_orchestrator() -> MessageOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MessageOrchestrator()
    return _orchestrator


def setup_orchestrator() -> MessageOrchestrator:
    """Setup the orchestrator with default agents."""
    orchestrator = get_orchestrator()

    # Import and register report agent
    try:
        import orchestrator.report_agent as report_agent_module

        # Set available functions directly on the module
        report_agent_module.AVAILABLE_FUNCTIONS = {
            "get_my_reports": report_agent_module.get_my_reports,
            "get_report": report_agent_module.get_report,
            "create_report": report_agent_module.create_report,
            "update_report": report_agent_module.update_report,
        }

        # Create and register agent
        report_agent_instance = Agent(
            name="report_agent",
            description="Report management - list, view, create, and update user reports",
            system_prompt=report_agent_module.SYSTEM_PROMPT,
            tools=report_agent_module.TOOLS,
            available_functions=report_agent_module.AVAILABLE_FUNCTIONS,
            chat_func=report_agent_module.chat,
        )

        orchestrator.register_agent(report_agent_instance)
        orchestrator_logger.info("Report agent registered successfully")

    except Exception as e:
        orchestrator_logger.error(f"Failed to register report agent: {e}")

    return orchestrator


if __name__ == "__main__":
    print("Message Orchestrator - Setup Test")
    print("=" * 50)

    orchestrator = setup_orchestrator()
    print()
    print(orchestrator.list_agents())
"""
Report Agent - Handles report-related queries and operations.

This agent can:
- List user's reports
- Get specific report details
- Create new reports
- Update existing reports (open ones only)

Logging: Uses orchestrator_logger from init_logs
        Logs are written to logs/orchestrator.log
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

from litellm import completion

# Import orchestrator logger for debugging
from init_logs import orchestrator_logger


# =============================================================================
# SYSTEM PROMPT - Defines the agent's behavior and capabilities
# =============================================================================
SYSTEM_PROMPT = """You are a Report Management Assistant for a school facilities management system.

## YOUR PRIMARY JOB
When a user wants to report an issue, your ONLY job is to CREATE A REPORT in the system using the create_report function.

## CRITICAL RULES
1. NEVER draft emails, forms, or suggest other methods
2. NEVER ask the user "would you like me to create a report?" - just CREATE IT
3. After gathering minimum info (location + when noticed), immediately call create_report
4. ALWAYS call create_report, then confirm to user with the report ID

## REPORT CREATION WORKFLOW - FOLLOW EXACTLY
Step 1: When user says "make a report about X" or similar, ask ONE question for missing info
        - Required: Location (building/floor/room)
        - Optional: When noticed (if not provided)
        - Example: "Which building/floor is affected?"

Step 2: When user responds with location and timing, IMMEDIATELY call create_report

Step 3: After calling create_report, tell user:
        "Report created successfully! ID: #[number]
         Title: [title]
         Status: open

         Our team will review and address this issue."

## WRONG BEHAVIOR (Never do this)
- "Here's a draft email you can send..."
- "Would you like me to help you draft a message?"
- "Let me know if you'd like to add more details"

## CORRECT BEHAVIOR (Always do this)
- Ask for missing location/timing (max 1 question)
- Call create_report
- Confirm with report ID

## Example Flow
User: "make a report about smk 1 school water flow too small"
You: "Which building/floor is affected and when did you notice it?"
User: "building 1 since yesterday"
You: [CALLS create_report with title="Water flow issue at Building 1" and content="Water flow at Building 1 has been consistently slow since yesterday."]
You: "Report created successfully! ID: #23"""


# =============================================================================
# TOOLS - Define available functions for the LLM to call
# =============================================================================
# Note: user_id is automatically passed by the orchestrator, don't ask for it
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_my_reports",
            "description": "Get all reports for the current user. Call this when user asks to see their reports.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["open", "in_progress", "resolved"],
                        "description": "Filter reports by status (optional)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_report",
            "description": "Get details of a specific report by ID. Call this when user asks for details of a specific report.",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_id": {
                        "type": "integer",
                        "description": "The report ID to retrieve (number only, e.g., 23)"
                    }
                },
                "required": ["report_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_report",
            "description": "Create a new report in the system. ALWAYS call this when user wants to file a report! After user provides issue details, call this to save the report.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title (max 100 chars) like 'Low water flow at Building 1'"
                    },
                    "content": {
                        "type": "string",
                        "description": "Detailed description including location, when noticed, and severity"
                    }
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_report",
            "description": "Update an existing report's title or content (only for open reports)",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_id": {
                        "type": "integer",
                        "description": "The report ID to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title (optional)"
                    },
                    "content": {
                        "type": "string",
                        "description": "New content (optional)"
                    }
                },
                "required": ["report_id"]
            }
        }
    }
]


# =============================================================================
# AVAILABLE FUNCTIONS - Will be populated by setup_orchestrator()
# =============================================================================
AVAILABLE_FUNCTIONS = {}


# =============================================================================
# CHAT FUNCTION - Main entry point for the agent
# =============================================================================
def chat(
    user_message: str,
    history: List[Dict[str, str]],
    max_turns: int = 5,
    user_id: int = None
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Main chat function for the report agent.

    Args:
        user_message: The user's message
        history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
        max_turns: Maximum number of turns (default 5)
        user_id: The user ID for database operations (required)

    Returns:
        Tuple of (response_text, updated_history)
    """
    import os
    from litellm import completion

    # Validate user_id
    if user_id is None:
        return "Error: User ID is required for report operations. Please try again.", history

    # Get configuration
    BASE_URL = os.environ.get("LITELLM_BASEURL", "")
    API_KEY = os.environ.get("LITELLM_API_KEY", "")
    MODEL = os.environ.get("LITELLM_MODEL", "gpt-3.5-turbo-1106")

    # Build messages array with system prompt, history, and user message
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + history + [
        {"role": "user", "content": user_message}
    ]

    # Add function definitions to system prompt
    function_definitions = "\n".join([
        f"- {tool['function']['name']}: {tool['function']['description']}"
        for tool in TOOLS
    ])
    messages[0]["content"] += f"\n\nAvailable functions:\n{function_definitions}"

    try:
        response = completion(
            model=MODEL,
            base_url=BASE_URL,
            api_key=API_KEY,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = getattr(response_message, "tool_calls", None) or []

        # Handle tool calls if any
        if tool_calls:
            messages.append(response_message)  # Add assistant's tool call message

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments

                # Parse arguments safely
                try:
                    import json
                    args = json.loads(function_args) if isinstance(function_args, str) else function_args
                except:
                    args = {}

                orchestrator_logger.info(f"report_agent calling function: {function_name} with user_id={user_id}, args={args}")

                # Call the function with user_id
                if function_name in AVAILABLE_FUNCTIONS:
                    func = AVAILABLE_FUNCTIONS[function_name]

                    # Pass user_id to all functions
                    result = func(user_id=user_id, **args)

                    orchestrator_logger.info(f"report_agent {function_name} result: {str(result)[:200]}")
                else:
                    result = f"Error: Function {function_name} not available"
                    orchestrator_logger.warning(f"report_agent function not found: {function_name}")

                # Add function result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result
                })

            # Get final response after tool execution
            second_response = completion(
                model=MODEL,
                base_url=BASE_URL,
                api_key=API_KEY,
                messages=messages
            )
            content = second_response.choices[0].message.content or ""
        else:
            content = response_message.content or ""

        # Clean content (remove special characters)
        content = content.encode('ascii', 'ignore').decode('ascii')

        # Update history
        updated_history = history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": content}
        ]

        return content, updated_history

    except Exception as e:
        error_msg = f"Error in report agent: {str(e)}"
        orchestrator_logger.error(error_msg)
        return error_msg, history + [{"role": "user", "content": user_message}, {"role": "assistant", "content": error_msg}]


# =============================================================================
# DATABASE HELPER FUNCTIONS - These are set by setup_orchestrator()
# =============================================================================
def _get_db_session():
    """Get a database session."""
    from db.config import get_db
    return next(get_db())


def get_my_reports(user_id: int, status_filter: str = None):
    """Get all reports for a user."""
    from db.models import Report

    db = _get_db_session()
    try:
        query = db.query(Report).filter(Report.reporter_id == user_id)
        if status_filter:
            query = query.filter(Report.status == status_filter)

        reports = query.order_by(Report.created_at.desc()).all()

        if not reports:
            return "You have no reports."

        result = f"Your Reports:\n\n"
        for report in reports:
            result += f"ID: #{report.id}\n"
            result += f"Title: {report.title}\n"
            result += f"Status: {report.status}\n"
            result += f"Created: {report.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            result += "-" * 30 + "\n"

        return result
    finally:
        db.close()


def get_report(user_id: int, report_id: int):
    """Get details of a specific report."""
    from db.models import Report

    db = _get_db_session()
    try:
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.reporter_id == user_id
        ).first()

        if not report:
            return f"Report #{report_id} not found or you don't have access to it."

        result = f"Report Details:\n\n"
        result += f"ID: #{report.id}\n"
        result += f"Title: {report.title}\n"
        result += f"Content: {report.content}\n"
        result += f"Status: {report.status}\n"
        result += f"Created: {report.created_at.strftime('%Y-%m-%d %H:%M')}\n"

        if report.comment:
            result += f"\nAdmin Comment: {report.comment}\n"

        if report.resolved_by:
            result += f"Resolved at: {report.resolved_at.strftime('%Y-%m-%d %H:%M')}\n"

        return result
    finally:
        db.close()


def create_report(user_id: int, title: str, content: str):
    """Create a new report."""
    from db.models import Report

    db = _get_db_session()
    try:
        report = Report(
            reporter_id=user_id,
            title=title,
            content=content,
            status="open"
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        return f"Report created successfully!\n\nID: #{report.id}\nTitle: {report.title}\nStatus: open\n\nYour report has been submitted and will be reviewed by the admin."
    except Exception as e:
        db.rollback()
        return f"Error creating report: {str(e)}"
    finally:
        db.close()


def update_report(user_id: int, report_id: int, title: str = None, content: str = None):
    """Update an existing report (only open reports can be modified)."""
    from db.models import Report

    db = _get_db_session()
    try:
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.reporter_id == user_id
        ).first()

        if not report:
            return f"Report #{report_id} not found or you don't have access to it."

        if report.status != "open":
            return f"Cannot update report #{report_id}. Only open reports can be modified. Current status: {report.status}"

        updates = []
        if title:
            report.title = title
            updates.append("title")
        if content:
            report.content = content
            updates.append("content")

        db.commit()

        return f"Report #{report_id} updated successfully!\nUpdated fields: {', '.join(updates)}\n\nNew content:\nTitle: {report.title}\nContent: {report.content}"
    except Exception as e:
        db.rollback()
        return f"Error updating report: {str(e)}"
    finally:
        db.close()
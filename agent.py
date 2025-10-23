from typing import List, Dict, Any
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv
import os
import logging
import asyncio

load_dotenv()

# Force Vertex AI usage
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# --- Global Configuration ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "hackathon-473214")
LOCATION = "us-central1"
TOOLBOX_URL = os.getenv("TOOLBOX_URL", "http://localhost:5000/mcp")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

print(f"Using PROJECT_ID={PROJECT_ID}, LOCATION={LOCATION}")
print(f"Connecting to MCP Toolbox at: {TOOLBOX_URL}")

# --- System Prompt ---
prompt = """
You are the Benifix Smart Benefits Assistant. Your primary goal is to provide accurate, 
helpful, and actionable information to employees regarding their benefits.

IMPORTANT BEHAVIOR RULES:
1. **Always** use the available tools when a query requires data retrieval, policy lookup, or cost prediction.
2. Combine information from the database (via SQL tools) with analysis tools to answer complex questions.
3. Be polite, professional, and concise in your responses.
4. NEVER make up or guess any data. If you cannot find the requested information, state that clearly.
5. If a query requires a specific employee ID and the user has not provided one, ask for it.

AVAILABLE CAPABILITIES (via MCP Tools):
- **find-providers**: Search for in-network healthcare providers by specialty
- **get-employee-benefits**: Retrieve comprehensive employee benefits information
- **get-employee-plan-details**: Get specific plan details for cost predictions
- **search-policy-documents**: Search benefits policy documents for coverage details
- **check-employee-deductible**: Check if employee qualifies for low-deductible alerts
- **get-support-ticket-status**: Check status of support tickets
- **get-provider-locations**: Get provider location information for mapping
- **get-usage-profile-assumptions**: Get healthcare usage profiles for cost estimation
- **find-nearest-provider**: Use Google Places API to find closest provider based on user location

TOOL USAGE GUIDELINES:
- For benefit inquiries: Use get-employee-benefits or get-employee-plan-details
- For provider searches: Use find-providers
- For policy questions: Use search-policy-documents
- For cost predictions: Use get-employee-plan-details + get-usage-profile-assumptions
- For deductible alerts: Use check-employee-deductible
- **For finding nearest provider: FIRST call get-provider-locations to get in-network providers, THEN call find-nearest-provider with user's location to find the closest one**

CHALLENGE 5 - FIND NEAREST PROVIDER WORKFLOW:
When a user asks to find the closest/nearest provider:
1. FIRST: Call get-provider-locations with the specialty to get in-network providers from our database
2. SECOND: Call find-nearest-provider with user's current location (latitude/longitude) to use Google Places API
3. Combine the results: Match in-network providers with nearby locations from Places API
4. Recommend the provider that is both in-network AND closest to the user

RESPONSE FORMAT:
- Present information clearly with relevant details
- Use bullet points for multiple items
- Include specific dollar amounts when discussing costs
- Cite the plan name when providing benefit details
- For location-based queries, include addresses and estimated distances
"""

# --- Initialize MCP Toolset ---
mcp_toolset = None
try:
    connection_params = StreamableHTTPConnectionParams(url=TOOLBOX_URL)
    mcp_toolset = McpToolset(
        connection_params=connection_params,
        tool_name_prefix="benifix_"
    )
    print(f"✓ MCP Toolset connected successfully")
    
except Exception as e:
    logger.error(f"Failed to connect MCP Toolset: {e}")
    print(f"✗ MCP Toolset connection failed: {e}")
    print(f"\n⚠ Make sure toolbox is running:")
    print(f"  cd ~/ADK_Hack/benifix_agent")
    print(f"  ./toolbox --tools-file tools.yaml")
    import traceback
    traceback.print_exc()

# --- Root Agent Definition ---
root_agent = Agent(
    name='benifix_benefits_assistant',
    model=Gemini(
        model="gemini-2.0-flash",
        project=PROJECT_ID,
        location=LOCATION,
        vertexai=True
    ),
    instruction=prompt,
    tools=[mcp_toolset] if mcp_toolset else []
)

print("✓ Agent initialized successfully")
if mcp_toolset:
    print(f"✓ Agent connected to MCP Toolbox")
else:
    print("⚠ Agent running without MCP tools")


# --- Async Query Function Using Runner ---
async def run_query_async(query: str, employee_id: str = None, user_id: str = "user", session_id: str = None):
    """Run a query against the agent using the proper Runner pattern"""
    try:
        if employee_id:
            query = f"[Employee ID: {employee_id}] {query}"
        
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}\n")
        
        # Create session service and session
        session_service = InMemorySessionService()
        if session_id is None:
            session = await session_service.create_session(
                app_name="benifix_agent",
                user_id=user_id
            )
            session_id = session.id
        
        # Create runner with the agent and session service
        runner = Runner(
            app_name="benifix_agent",
            agent=root_agent,
            session_service=session_service
        )
        
        # Prepare the user's message in ADK format
        content = types.Content(
            role='user',
            parts=[types.Part(text=query)]
        )
        
        # Run the agent and collect response
        response_text = ""
        tool_calls = []
        
        async for event in runner.run_async(
            session_id=session_id,
            user_id=user_id,
            new_message=content
        ):
            # Check if this is the final response
            if hasattr(event, 'is_final_response') and event.is_final_response():
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                print(part.text, end='', flush=True)
                                response_text += part.text
            
            # Track tool calls
            event_type = type(event).__name__
            if 'ToolCall' in event_type or 'FunctionCall' in event_type:
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'function_call'):
                                tool_name = part.function_call.name
                                print(f"\n🔧 Calling tool: {tool_name}")
                                tool_calls.append(tool_name)
        
        print("\n")
        
        if tool_calls:
            print(f"📊 Tools used: {', '.join(tool_calls)}")
        
        return response_text
        
    except Exception as e:
        logger.error(f"Error running query: {e}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


# --- Synchronous Wrapper ---
def run_query(query: str, employee_id: str = None):
    """Synchronous wrapper for run_query_async"""
    return asyncio.run(run_query_async(query, employee_id))


# --- Example Test Queries ---
async def run_examples_async():
    """Run example queries to test the MCP toolbox integration"""
    
    print("\n" + "="*60)
    print("BENIFIX AGENT - MCP TOOLBOX INTEGRATION TEST")
    print("="*60)
    
    print("\n### Example 1: Provider Search ###")
    await run_query_async("Find me a dentist")
    
    print("\n### Example 2: Employee Benefits ###")
    await run_query_async("What are my benefits?", employee_id="123")
    
    print("\n### Example 3: Benefits + Provider Search ###")
    await run_query_async(
        "What's my deductible, and can you find me a dentist?",
        employee_id="123"
    )
    
    print("\n### Example 4: Deductible Alert ###")
    await run_query_async(
        "Check if I'm eligible for a low-deductible alert",
        employee_id="456"
    )
    
    print("\n### Example 5: Support Ticket Status ###")
    await run_query_async("What's the status of support ticket 1001?")


def run_examples():
    """Synchronous wrapper for run_examples_async"""
    asyncio.run(run_examples_async())


if __name__ == "__main__":
    import sys
    
    if not mcp_toolset:
        print("\n⚠ WARNING: MCP Toolbox not connected!")
        print("Start toolbox first in another terminal:")
        print("  cd ~/ADK_Hack/benifix_agent")
        print("  ./toolbox --tools-file tools.yaml")
        print("\nThen run this agent again.")
        sys.exit(1)
    
    print("\n✓ MCP Toolbox Ready")
    
    if "--examples" in sys.argv:
        run_examples()
    elif len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        run_query(query)
    else:
        print("\nAgent ready for queries.")
        print("\nUsage:")
        print("  python agent.py --examples              # Run test queries")
        print("  python agent.py 'your question here'    # Run a single query")
        print("  adk web --agent agent:root_agent        # Start web UI")

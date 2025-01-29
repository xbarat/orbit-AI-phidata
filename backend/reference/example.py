from phi.agent import Agent
from a1_query.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
openai = OpenAIChat(api_key=os.getenv('OPENAI_API_KEY'))

def create_web_agent():
    return Agent(
        name="Web Agent",
        role="Search the web for information",
        model=openai,
        tools=[DuckDuckGo()],
        instructions=["Always include sources"],
        show_tool_calls=True,
        markdown=True,
    )

def create_finance_agent():
    return Agent(
        name="Finance Agent",
        role="Get financial data",
        model=openai,
        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
        instructions=["Use tables to display data"],
        show_tool_calls=True,
        markdown=True,
    )

def create_team_agent(web_agent, finance_agent):
    return Agent(
        team=[web_agent, finance_agent],
        instructions=["Always include sources", "Use tables to display data"],
        show_tool_calls=True,
        markdown=True,
    )

if __name__ == "__main__":
    # Create test queries
    test_queries = [
        "What are the latest developments in AI?",
        "Get me the current stock price and analyst recommendations for AAPL",
        "Summarize analyst recommendations and share the latest news for NVDA",
        "What are the top performing tech stocks this week and why?",
    ]
    
    # Initialize agents
    web_agent = create_web_agent()
    finance_agent = create_finance_agent()
    team_agent = create_team_agent(web_agent, finance_agent)
    
    # Test individual agents
    print("\n=== Testing Web Agent ===")
    web_agent.print_response(test_queries[0], stream=True)
    
    print("\n=== Testing Finance Agent ===")
    finance_agent.print_response(test_queries[1], stream=True)
    
    print("\n=== Testing Team Agent ===")
    team_agent.print_response(test_queries[2], stream=True)
    team_agent.print_response(test_queries[3], stream=True)

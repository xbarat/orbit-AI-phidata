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

# Create a query parser agent

def create_query_parser():
    return Agent(
        name="Query Agent",
        role="Parse the query into a data requirement",
        model=openai,
        tools=[DuckDuckGo()],
        instructions=["Always include sources"],
        show_tool_calls=True,
        markdown=True,
    )

# Crate a data fetcher agent

def create_data_fetcher():
    return Agent(
        name="Data Fetcher",
        role="Fetch data from the web",
        model=openai,
        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
        instructions=["Use tables to display data"],
        show_tool_calls=True,
        markdown=True,
    )

# Create a data transformer agent

def create_data_transformer():
    return Agent(
        name="Data Transformer",
        role="Transform the data into a structured format",
        model=openai,
        tools=[],
        instructions=["Transform the data into a structured format"],
        show_tool_calls=True,
        markdown=True,
    )

# Create a team agent

def create_team_agent(query_parser, data_fetcher, data_transformer):
    return Agent(
        team=[query_parser, data_fetcher, data_transformer],
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
    query_parser = create_query_parser()
    data_fetcher = create_data_fetcher()
    data_transformer = create_data_transformer()
    team_agent = create_team_agent(query_parser, data_fetcher, data_transformer)
    
    # Test individual agents
    print("\n=== Testing Query Agent ===")
    query_parser.print_response(test_queries[0], stream=True)
    
    print("\n=== Testing Data Fetcher ===")
    data_fetcher.print_response(test_queries[1], stream=True)
    
    print("\n=== Testing Team Agent ===")
    team_agent.print_response(test_queries[2], stream=True)
    team_agent.print_response(test_queries[3], stream=True)

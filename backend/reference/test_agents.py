import pytest
from example import create_web_agent, create_finance_agent, create_team_agent

@pytest.fixture
def web_agent():
    return create_web_agent()

@pytest.fixture
def finance_agent():
    return create_finance_agent()

@pytest.fixture
def team_agent(web_agent, finance_agent):
    return create_team_agent(web_agent, finance_agent)

def test_web_agent(web_agent):
    response = web_agent.run("What is the latest news about SpaceX?")
    assert response is not None
    assert isinstance(response, str)

def test_finance_agent(finance_agent):
    response = finance_agent.run("What is the current stock price of AAPL?")
    assert response is not None
    assert isinstance(response, str)

def test_team_agent(team_agent):
    response = team_agent.run("What are the latest developments and stock performance for NVIDIA?")
    assert response is not None
    assert isinstance(response, str) 
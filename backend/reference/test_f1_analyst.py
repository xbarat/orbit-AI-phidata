import pytest
from f1_analyst import create_f1_analyst, create_f1_team_analyst
import pandas as pd

@pytest.fixture
def f1_agent():
    return create_f1_analyst()

@pytest.fixture
def team_analyst(f1_agent):
    return create_f1_team_analyst(f1_agent)

def test_qualifying_analysis(f1_agent):
    query = "Get qualifying results for Max Verstappen in 2023 Monaco GP"
    response = f1_agent.run(query)
    assert response is not None
    # Check if response contains DataFrame
    assert "DataFrame" in str(response)

def test_race_pace_analysis(f1_agent):
    query = "Analyze Charles Leclerc's lap times in 2023 British GP"
    response = f1_agent.run(query)
    assert response is not None
    # Verify lap time data is present
    assert "LapTime" in str(response)

def test_complex_analysis(team_analyst):
    query = "Compare the race pace of Red Bull and Mercedes in the 2023 Abu Dhabi GP"
    response = team_analyst.run(query)
    assert response is not None
    # Verify team comparison data
    assert any(team in str(response) for team in ["Red Bull", "Mercedes"])

def test_dataframe_creation(f1_agent):
    query = "Create a dataframe of the podium finishers in the 2023 Monaco GP"
    response = f1_agent.run(query)
    # Verify DataFrame format
    assert isinstance(eval(response), pd.DataFrame) 
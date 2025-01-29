from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

class QueryType(BaseModel):
    """Classification of the query type"""
    primary_type: Literal["driver", "constructor", "season", "race", "comparison"] = Field(
        description="Primary type of query being asked"
    )
    sub_type: Literal["performance", "standings", "statistics", "head_to_head", "historical", "specific_event"] = Field(
        description="Specific aspect being queried"
    )
    granularity: Literal["season", "race", "qualifying", "lap", "pitstop"] = Field(
        description="Level of detail needed in the data"
    )

class QueryParameters(BaseModel):
    """Enhanced parameters extracted from the query"""
    primary_entity: Literal["driver", "constructor", "circuit", "season"] = Field(
        description="Primary focus of the query"
    )
    entity_ids: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Mapped entity IDs: drivers, constructors, circuits"
    )
    metrics: List[Literal["results", "qualifying", "laps", "pitstops", "standings", "status"]] = Field(
        default_factory=list,
        description="Required data types from endpoints.md"
    )
    time_scope: Dict[str, Any] = Field(
        default_factory=dict,
        description="Temporal parameters: seasons, rounds, date ranges"
    )
    comparison: bool = Field(
        default=False,
        description="Whether comparison between entities is needed"
    )

class EndpointInfo(BaseModel):
    """Detailed information about an endpoint"""
    url: str = Field(description="Complete Ergast API URL")
    purpose: str = Field(description="What this endpoint's data will be used for")
    requires_filtering: bool = Field(default=False, description="Whether results need filtering")
    filter_criteria: Optional[Dict] = Field(default=None, description="Criteria for filtering results")

class F1QueryResponse(BaseModel):
    """Enhanced response with endpoints and processing instructions"""
    endpoints: List[EndpointInfo] = Field(default_factory=list, description="List of endpoints with details")
    explanation: str = Field(description="Explanation of the data retrieval strategy")
    processing_steps: List[str] = Field(default_factory=list, description="Steps needed to process the data") 
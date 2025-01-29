import logging
from typing import List
from a1_query.query_to_endpoint import process_query
from a2_transform import EndpointRouter
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from a1_query.url_validator import ErgastEndpointValidator
from a1_query.query_index import query_index

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class F1QueryProcessor:
    """Minimal pipeline coordinator"""
    
    def __init__(self):
        self.router = EndpointRouter()
        self.validator = ErgastEndpointValidator()
    
    def execute_query(self, query: str) -> List[pd.DataFrame]:
        """Core execution flow"""
        try:
            # Get validated endpoints
            endpoints = [
                ep for ep in process_query(query)
                if self.validator.validate(ep)
            ]
            
            if not endpoints:
                logger.error("No valid endpoints generated")
                return []
            
            # Process each endpoint
            results = []
            for endpoint in endpoints:
                if transformer := self.router.get_transformer(endpoint):
                    results.append(transformer.transform(endpoint))
                else:
                    logger.warning(f"No transformer for {endpoint}")
            
            return results
            
        except Exception as e:
            logger.exception("Processing failed")
            return []

def test_query(index: int):
    """Test the F1 query processor with a specific query index"""
    processor = F1QueryProcessor()
    query = query_index.get_query(index)
    if query:
        print(f"\nTesting Query [{index}]: {query}")
        results = processor.execute_query(query)
        print("\nResults:")
        for idx, result in enumerate(results, 1):
            print(f"Result {idx}:")
            print(result.head() if isinstance(result, pd.DataFrame) else result)
    else:
        print(f"No query found for index {index}")

# Test the minimal version
if __name__ == "__main__":
    test_query(23)  # Using the same test index as query_to_endpoint.py 
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import logging
from typing import List
from a1_query.query_to_endpoint import process_query
from a2_transform import EndpointRouter
from a1_query.query_index import query_index

logger = logging.getLogger(__name__)

class F1QueryProcessor:
    """Lightweight pipeline coordinator"""
    
    def __init__(self):
        self.router = EndpointRouter()
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Simplified execution flow"""
        try:
            # Directly use existing process_query from query_to_endpoint.py
            endpoints = process_query(query)
            
            if not endpoints:
                logger.warning("No endpoints generated")
                return pd.DataFrame()
            
            # Existing data collection/transformation logic
            dfs = []
            for endpoint in endpoints:
                transformer = self.router.get_transformer(endpoint)
                if transformer:
                    df = transformer.fetch_and_transform(endpoint)
                    dfs.append(df)
            
            return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return pd.DataFrame()

def test_queries(indices: List[int]):
    """Test the pipeline with queries from the index"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    processor = F1QueryProcessor()
    queries = query_index.get_queries(indices)
    
    for query in queries:
        print(f"\nProcessing query: {query}")
        df = processor.execute_query(query)
        if not df.empty:
            print("\nFirst few rows:")
            print(df.head())
            print("\nColumns:", df.columns.tolist())
            print("Shape:", df.shape)

if __name__ == "__main__":
    # Test with specific query indices
    test_queries([29]) 
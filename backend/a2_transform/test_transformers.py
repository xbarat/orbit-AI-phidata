import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from a2_transform.router import EndpointRouter
import pandas as pd

def test_transformer(endpoint: str) -> bool:
    """Test individual transformer with an endpoint URL"""
    router = EndpointRouter()
    transformer = router.get_transformer(endpoint)
    
    if not transformer:
        print(f"❌ No transformer found for: {endpoint}")
        return False
    
    try:
        df = transformer.transform(endpoint)
        if not isinstance(df, pd.DataFrame):
            print(f"❌ Invalid output type for {endpoint} - Expected DataFrame, got {type(df)}")
            return False
        if df.empty:
            print(f"⚠️ Empty DataFrame from {endpoint}")
            return False
        print(f"✅ Success: {endpoint}")
        print(f"   Rows: {len(df)}, Columns: {df.columns.tolist()}")
        return True
    except Exception as e:
        print(f"❌ Transformation failed for {endpoint}: {str(e)}")
        return False

if __name__ == "__main__":
    # Test endpoints from the query "Show me Lewis Hamilton's 2023 race results"
    test_endpoints = [
        "http://ergast.com/api/f1/2023/drivers/lewis_hamilton/results.json",
        "http://ergast.com/api/f1/2023/drivers/lewis_hamilton/laps.json",
        "http://ergast.com/api/f1/2023/drivers/lewis_hamilton/status.json"
    ]
    
    print("\nTesting Transformers for Sample Endpoints:")
    results = [test_transformer(ep) for ep in test_endpoints]
    
    if all(results):
        print("\n🎉 All transformers worked!")
    else:
        print(f"\n🔴 Issues found: {results.count(False)}/{len(results)} failed") 
import unittest
import pandas as pd
from backend.qhi.data_processor import ProcessorFactory, BaseDataProcessor
from backend.qhi.schemas import ENDPOINT_SCHEMAS

class TestEndpointProcessors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_year = 2023  # Using recent year with data
        cls.test_round = 1     # First race of the season
        cls.factory = ProcessorFactory()

    def test_all_endpoints(self):
        """Test transformation for all documented endpoints"""
        endpoints = self.factory.get_available_endpoints()
        param_map = {
            'laps': {'year': self.test_year, 'round': self.test_round},
            'pitstops': {'year': self.test_year, 'round': self.test_round},
            'qualifying': {'year': self.test_year, 'round': self.test_round},
            'results': {'year': self.test_year, 'round': self.test_round},
            'driverStandings': {'year': self.test_year},
            'constructorStandings': {'year': self.test_year},
            'schedules': {'year': self.test_year},
            'circuits': {'year': self.test_year},
            'constructors': {'year': self.test_year},
            'drivers': {'year': self.test_year},
            # No params needed for these
            'seasons': {},
            'status': {}
        }

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                try:
                    # Create processor and fetch minimal data
                    processor = self.factory.create_processor(endpoint)
                    raw_data = processor.fetch_data(
                        **param_map.get(endpoint, {}),
                        limit=1  # Minimize data transfer
                    )
                    
                    # Transform and validate
                    df = processor.transform(raw_data)
                    validated_df = processor.validate_schema(df)
                    
                    # Basic sanity checks
                    self.assertIsInstance(df, pd.DataFrame, 
                        f"{endpoint}: Output is not a DataFrame")
                    
                    if not df.empty:
                        self.assertTrue(
                            all(col in df.columns for col in 
                                ENDPOINT_SCHEMAS[endpoint]['required_fields']),
                            f"{endpoint}: Missing required columns"
                        )
                        
                    print(f"✅ {endpoint} passed | Shape: {df.shape}")
                    
                except Exception as e:
                    self.fail(f"Failed processing {endpoint}: {str(e)}")

if __name__ == '__main__':
    unittest.main(failfast=True) 
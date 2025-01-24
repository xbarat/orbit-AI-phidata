from typing import Dict, List
import httpx
import asyncio
import logging
from pydantic import BaseModel, Field
from datetime import datetime
import backoff  # for exponential backoff

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIResponse(BaseModel):
    """Structured API response"""
    url: str = Field(..., description="The endpoint URL that was called")
    data: Dict = Field(..., description="The response data")
    timestamp: datetime = Field(default_factory=datetime.now)
    status_code: int = Field(default=200)

class DataFetcher:
    """Minimal component for fetching F1 data from Ergast API in parallel"""
    
    def __init__(self, rate_limit_per_second: int = 2):  # Reduced rate limit to be safer
        self.rate_limit = rate_limit_per_second
        self.semaphore = asyncio.Semaphore(rate_limit_per_second)
    
    @backoff.on_exception(
        backoff.expo,
        (httpx.HTTPError, httpx.TimeoutException),
        max_tries=3,
        max_time=30
    )
    async def _fetch_url(self, client: httpx.AsyncClient, url: str) -> APIResponse:
        """Fetch single URL with rate limiting and retries"""
        async with self.semaphore:  # Control concurrent requests
            try:
                # Add delay between requests
                await asyncio.sleep(1.0 / self.rate_limit)
                
                # Ensure URL is properly formatted
                if not url.endswith('.json'):
                    url = f"{url}.json"
                
                # Make request
                response = await client.get(url)
                response.raise_for_status()
                
                # Log success
                logger.info(f"Successfully fetched {url}")
                
                return APIResponse(
                    url=url,
                    data=response.json(),
                    status_code=response.status_code
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error for {url}: {e.response.status_code}")
                raise
            except httpx.TimeoutException:
                logger.error(f"Timeout fetching {url}")
                raise
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                raise
    
    async def fetch_endpoints(self, urls: List[str]) -> List[APIResponse]:
        """Fetch multiple endpoints in parallel with rate limiting
        
        Args:
            urls: List of Ergast API endpoints to fetch
            
        Returns:
            List of APIResponse objects containing the fetched data
        """
        # Configure client with longer timeout and proper headers
        async with httpx.AsyncClient(
            timeout=60.0,  # Increased timeout
            headers={
                "User-Agent": "F1DataAnalytics/1.0",
                "Accept": "application/json"
            },
            follow_redirects=True
        ) as client:
            # Create fetch tasks for all URLs
            tasks = [self._fetch_url(client, url) for url in urls]
            
            # Process in batches to respect rate limits
            batch_size = self.rate_limit
            valid_responses = []
            
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                try:
                    # Gather batch responses
                    batch_responses = await asyncio.gather(*batch, return_exceptions=True)
                    
                    # Filter and log errors
                    for response in batch_responses:
                        if isinstance(response, Exception):
                            logger.error(f"Failed request: {str(response)}")
                        else:
                            valid_responses.append(response)
                    
                    # Add delay between batches
                    if i + batch_size < len(tasks):
                        await asyncio.sleep(1.0)
                        
                except Exception as e:
                    logger.error(f"Batch error: {str(e)}")
            
            return valid_responses

async def fetch_data(urls: List[str]) -> List[Dict]:
    """Helper function to fetch data from multiple endpoints
    
    Args:
        urls: List of Ergast API endpoints to fetch
        
    Returns:
        List of response data dictionaries
    """
    fetcher = DataFetcher()
    responses = await fetcher.fetch_endpoints(urls)
    
    # Log summary
    logger.info(f"Successfully fetched {len(responses)} out of {len(urls)} endpoints")
    
    return [response.data for response in responses]

# Example usage:
if __name__ == "__main__":
    from query_to_endpoint import process_query
    import asyncio
    
    async def main():
        # Get endpoints from query processor
        query = "How does Lewis Hamilton compare to Charles Leclerc in terms of wins, podiums, and points over the last 5 seasons?"
        endpoints = process_query(query)
        
        print("\nFetching data from endpoints...")
        responses = await fetch_data(endpoints)
        
        # Print results
        print("\nFetched Data:")
        for i, data in enumerate(responses):
            print(f"\nResponse {i+1}:")
            mrdata = data.get('MRData', {})
            if mrdata:
                # Extract season from StandingsTable
                standings_table = mrdata.get('StandingsTable', {})
                season = standings_table.get('season', 'Unknown')
                standings_lists = standings_table.get('StandingsLists', [])
                
                print(f"Season: {season}")
                print(f"Total Drivers: {mrdata.get('total', '0')}")
                
                # Display driver standings if available
                if standings_lists:
                    driver_standings = standings_lists[0].get('DriverStandings', [])
                    print("Driver Standings:")
                    for standing in driver_standings:
                        driver = standing.get('Driver', {})
                        driver_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
                        points = standing.get('points', '0')
                        position = standing.get('position', 'N/A')
                        wins = standing.get('wins', '0')
                        print(f"  {position}. {driver_name}: Points={points}, Wins={wins}")
            else:
                print("No MRData found in response")
    
    asyncio.run(main()) 
from typing import List, Dict, Optional
from urllib.parse import urlencode
import datetime
from .models import QueryParameters
from .driver_mapping import DriverIDMapper
from .url_validator import ErgastEndpointValidator

class ErgastURLBuilder:
    BASE_URL = "http://ergast.com/api/f1"
    
    def __init__(self):
        self.current_year = datetime.datetime.now().year
        self.primary_entity = None

    def build_endpoints(self, params: QueryParameters) -> List[str]:
        """Main entry point for endpoint construction"""
        endpoints = []
        
        # Parse temporal parameters
        years = self._parse_time_scope(params.time_scope)
        rounds = params.time_scope.get('rounds', [])
        
        # Get entity lists
        drivers = params.entity_ids.get('drivers', [])
        constructors = params.entity_ids.get('constructors', [])
        circuits = params.entity_ids.get('circuits', [])
        
        # Set primary entity from params
        self.primary_entity = params.primary_entity
        
        # Build endpoints per metric type
        for metric in params.metrics:
            endpoints += self._build_metric_endpoints(
                metric, years, rounds, drivers, constructors, circuits
            )
        
        return self._validate_endpoints(endpoints)

    def _build_metric_endpoints(self, metric, years, rounds, drivers, constructors, circuits):
        """Router for different metric types"""
        builder_map = {
            'results': self._build_results_endpoints,
            'qualifying': self._build_qualifying_endpoints,
            'standings': self._build_standings_endpoints,
            'status': self._build_status_endpoints,
            'laps': self._build_lap_endpoints,
            'pitstops': self._build_pitstop_endpoints
        }
        
        if metric not in builder_map:
            return []
        
        return builder_map[metric](years, rounds, drivers, constructors, circuits)

    def _build_results_endpoints(self, years, rounds, drivers, constructors, circuits):
        """Construct results endpoints"""
        urls = []
        
        # Circuit-based queries
        for circuit in circuits:
            for year in years:
                if rounds:
                    for round_num in rounds:
                        urls.append(f"{self.BASE_URL}/{year}/{round_num}/circuits/{circuit}/results.json")
                else:
                    urls.append(f"{self.BASE_URL}/{year}/circuits/{circuit}/results.json")
        
        # Driver-based queries
        for driver in drivers:
            for year in years:
                urls.append(f"{self.BASE_URL}/{year}/drivers/{driver}/results.json")
        
        # Constructor-based queries
        for constructor in constructors:
            for year in years:
                urls.append(f"{self.BASE_URL}/{year}/constructors/{constructor}/results.json")
        
        return urls

    def _build_standings_endpoints(self, years, rounds, drivers, constructors, circuits):
        """Construct standings endpoints"""
        urls = []
        
        # Get current year if no years specified
        if not years:
            years = [self.current_year]
        
        for year in years:
            # Get general standings and filter by entity in transformer
            if self.primary_entity == 'driver' or drivers:
                urls.append(f"{self.BASE_URL}/{year}/driverStandings.json")
            elif self.primary_entity == 'constructor' or constructors:
                urls.append(f"{self.BASE_URL}/{year}/constructorStandings.json")
        
        return urls

    def _build_qualifying_endpoints(self, years, rounds, drivers, constructors, circuits):
        """Construct qualifying endpoints"""
        urls = []
        
        for year in years:
            # Driver-specific qualifying
            if drivers:
                for driver in drivers:
                    # Debug print
                    print(f"Original driver ID: {driver}")
                    ergast_driver = ErgastEndpointValidator.DRIVER_MAPPINGS.get(driver, driver)
                    print(f"Mapped driver ID: {ergast_driver}")
                    urls.append(f"{self.BASE_URL}/{year}/drivers/{ergast_driver}/qualifying.json")
            # Constructor-specific qualifying
            elif constructors:
                for constructor in constructors:
                    urls.append(f"{self.BASE_URL}/{year}/constructors/{constructor}/qualifying.json")
            # Circuit-specific qualifying
            elif circuits:
                for circuit in circuits:
                    urls.append(f"{self.BASE_URL}/{year}/circuits/{circuit}/qualifying.json")
            # If no specific entities, get all qualifying for the year
            else:
                urls.append(f"{self.BASE_URL}/{year}/qualifying.json")
        
        return urls

    def _build_status_endpoints(self, years, rounds, drivers, constructors, circuits):
        """Construct status endpoints"""
        urls = []
        
        # Get current year if no years specified
        if not years:
            years = [self.current_year]
        
        for year in years:
            # Constructor-specific status
            if constructors:
                for constructor in constructors:
                    urls.append(f"{self.BASE_URL}/{year}/constructors/{constructor}/status.json")
            # Driver-specific status
            elif drivers:
                for driver in drivers:
                    urls.append(f"{self.BASE_URL}/{year}/drivers/{driver}/status.json")
            # General status for the year
            else:
                urls.append(f"{self.BASE_URL}/{year}/status.json")
        
        return urls

    def _build_lap_endpoints(self, years, rounds, drivers, constructors, circuits):
        """Construct lap endpoints according to Ergast API spec"""
        urls = []
        
        # Get current year if no years specified
        if not years:
            years = [self.current_year]
        
        for year in years:
            # For fastest lap analysis, we only need the final lap data
            # or a sample of laps from each race (e.g., every 10th lap)
            if rounds:
                for round_num in rounds:
                    urls.append(f"{self.BASE_URL}/{year}/{round_num}/laps.json")
            else:
                # Instead of all rounds (1-23), get data from representative races
                # For example: First, middle, and last race of each season
                season_rounds = [1, 12, 20]  # Representative sample
                for round_num in season_rounds:
                    urls.append(f"{self.BASE_URL}/{year}/{round_num}/laps.json")
        
        return urls

    def _build_pitstop_endpoints(self, years, rounds, drivers, constructors, circuits):
        """Construct pitstop endpoints"""
        urls = []
        for year in years:
            if rounds:
                for round_num in rounds:
                    urls.append(f"{self.BASE_URL}/{year}/{round_num}/pitstops.json")
        return urls

    def _parse_time_scope(self, time_scope: Dict) -> List[int]:
        """Convert time scope to concrete years"""
        try:
            if not time_scope:  # Handle empty time_scope
                return [self.current_year]
            
            if 'years' in time_scope:
                return [int(year) for year in time_scope['years']]
            
            if 'range' in time_scope:
                range_data = time_scope['range']
                if isinstance(range_data, list) and len(range_data) == 2:
                    start, end = range_data
                    return list(range(int(start), int(end) + 1))
                else:
                    print(f"Invalid range format: {range_data}")
                    return [self.current_year]
                
            if 'last' in time_scope:
                years = int(time_scope['last'])
                return list(range(self.current_year - years + 1, self.current_year + 1))
            
            # Default to current year if no valid time scope found
            return [self.current_year]
        
        except Exception as e:
            print(f"Error parsing time scope: {str(e)}")
            return [self.current_year]  # Fallback to current year

    def _validate_endpoints(self, endpoints: List[str]) -> List[str]:
        """Apply validation rules"""
        validator = ErgastEndpointValidator()
        return [ep for ep in endpoints if validator.validate(ep)] 
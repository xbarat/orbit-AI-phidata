import requests
import pandas as pd
from backend.qhi.schemas import ENDPOINT_SCHEMAS

class BaseDataProcessor:
    """Base class for F1 data processing with common utilities"""
    
    BASE_URL = "http://ergast.com/api/f1/"
    
    def __init__(self, endpoint_type):
        self.endpoint_type = endpoint_type
        self._cache = {}
    
    def fetch_data(self, year=None, round=None, **params):
        """Generic API request handler with error handling"""
        url = self._build_url(year, round)
        try:
            if url in self._cache:
                return self._cache[url]
                
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            self._cache[url] = data
            return data
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def _build_url(self, year, round):
        """Construct endpoint-specific URL (to be implemented by subclasses)"""
        raise NotImplementedError

    def transform(self, raw_data):
        """Transform raw JSON to structured DataFrame (to be implemented by subclasses)"""
        raise NotImplementedError

    @staticmethod
    def safe_get(data, *keys):
        """Safely navigate nested dictionaries"""
        for key in keys:
            try:
                data = data[key]
            except (KeyError, TypeError):
                return None
        return data

    def validate_schema(self, df):
        """Validate DataFrame against endpoint schema"""
        schema = ENDPOINT_SCHEMAS.get(self.endpoint_type)
        if not schema:
            return df
            
        # Check required fields
        missing = [field for field in schema['required_fields'] if field not in df.columns]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
            
        # Apply type conversions
        for col, dtype in schema['type_map'].items():
            if col in df.columns:
                try:
                    # Handle nullable types
                    if dtype == 'Int64':
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                    else:
                        df[col] = df[col].astype(dtype)
                except (ValueError, TypeError):
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
        return df

    def _try_int(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _try_float(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

class DriversProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("drivers")
        
    def _build_url(self, year, _=None):
        return f"{self.BASE_URL}{year}/drivers.json" if year else f"{self.BASE_URL}drivers.json"

    def transform(self, raw_data):
        drivers = self.safe_get(raw_data, 'MRData', 'DriverTable', 'Drivers') or []
        
        rows = []
        for driver in drivers:
            rows.append({
                'driverId': driver.get('driverId'),
                'givenName': driver.get('givenName'),
                'familyName': driver.get('familyName'),
                'permanentNumber': self._try_int(driver.get('permanentNumber')),
                'nationality': driver.get('nationality'),
                'dateOfBirth': driver.get('dateOfBirth'),
                'url': driver.get('url')
            })
            
        return pd.DataFrame(rows)

class CircuitsProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("circuits")
        
    def _build_url(self, year, _=None):
        return f"{self.BASE_URL}{year}/circuits.json" if year else f"{self.BASE_URL}circuits.json"

    def transform(self, raw_data):
        circuits = self.safe_get(raw_data, 'MRData', 'CircuitTable', 'Circuits') or []
        
        rows = []
        for circuit in circuits:
            location = circuit.get('Location', {})
            rows.append({
                'circuitId': circuit.get('circuitId'),
                'circuitName': circuit.get('circuitName'),
                'lat': self._try_float(location.get('lat')),
                'long': self._try_float(location.get('long')),
                'locality': location.get('locality'),
                'country': location.get('country')
            })
            
        return pd.DataFrame(rows)

class SchedulesProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("schedules")
        
    def _build_url(self, year, _=None):
        return f"{self.BASE_URL}{year}.json"

    def transform(self, raw_data):
        races = self.safe_get(raw_data, 'MRData', 'RaceTable', 'Races') or []
        
        rows = []
        for race in races:
            circuit = race.get('Circuit', {})
            rows.append({
                'season': self._try_int(race.get('season')),
                'round': self._try_int(race.get('round')),
                'raceName': race.get('raceName'),
                'date': race.get('date'),
                'time': race.get('time'),
                'circuitId': circuit.get('circuitId'),
                'url': race.get('url')
            })
            
        return pd.DataFrame(rows)

class PitstopsProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("pitstops")
        
    def _build_url(self, year, round):
        return f"{self.BASE_URL}{year}/{round}/pitstops.json"

    def transform(self, raw_data):
        races = self.safe_get(raw_data, 'MRData', 'RaceTable', 'Races') or []
        
        rows = []
        for race in races:
            base_info = {
                'season': self._try_int(race.get('season')),
                'round': self._try_int(race.get('round')),
                'raceName': race.get('raceName')
            }
            
            for pitstop in race.get('PitStops', []):
                rows.append({
                    **base_info,
                    'driverId': pitstop.get('driverId'),
                    'lap': self._try_int(pitstop.get('lap')),
                    'stop': self._try_int(pitstop.get('stop')),
                    'duration': self._try_float(pitstop.get('duration')),
                    'time': pitstop.get('time')
                })
                
        return pd.DataFrame(rows)

class ConstructorsProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("constructors")
        
    def _build_url(self, year, _=None):
        return f"{self.BASE_URL}{year}/constructors.json" if year else f"{self.BASE_URL}constructors.json"

    def transform(self, raw_data):
        constructors = self.safe_get(raw_data, 'MRData', 'ConstructorTable', 'Constructors') or []
        
        rows = []
        for constructor in constructors:
            rows.append({
                'constructorId': constructor.get('constructorId'),
                'name': constructor.get('name'),
                'nationality': constructor.get('nationality'),
                'established': self._try_int(constructor.get('established')),
                'url': constructor.get('url')
            })
            
        return pd.DataFrame(rows)

class SeasonsProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("seasons")
        
    def _build_url(self, year=None, _=None):
        return f"{self.BASE_URL}seasons.json"

    def transform(self, raw_data):
        seasons = self.safe_get(raw_data, 'MRData', 'SeasonTable', 'Seasons') or []
        
        rows = []
        for season in seasons:
            rows.append({
                'season': self._try_int(season.get('season')),
                'url': season.get('url')
            })
            
        return pd.DataFrame(rows)

class QualifyingProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("qualifying")
        
    def _build_url(self, year, round=None):
        return f"{self.BASE_URL}{year}/{round}/qualifying.json" if round else f"{self.BASE_URL}{year}/qualifying.json"

    def transform(self, raw_data):
        races = self.safe_get(raw_data, 'MRData', 'RaceTable', 'Races') or []
        
        rows = []
        for race in races:
            base_info = {
                'season': race.get('season'),
                'round': race.get('round'),
                'raceName': race.get('raceName')
            }
            
            for result in race.get('QualifyingResults', []):
                driver = result.get('Driver', {})
                constructor = result.get('Constructor', {})
                
                rows.append({
                    **base_info,
                    'driverId': driver.get('driverId'),
                    'constructorId': constructor.get('constructorId'),
                    'position': self._try_int(result.get('position')),
                    'q1': result.get('Q1'),
                    'q2': result.get('Q2'),
                    'q3': result.get('Q3')
                })
                
        return pd.DataFrame(rows)

class RaceResultsProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("results")
        
    def _build_url(self, year, round=None):
        return f"{self.BASE_URL}{year}/{round}/results.json" if round else f"{self.BASE_URL}{year}/results.json"

    def transform(self, raw_data):
        races = self.safe_get(raw_data, 'MRData', 'RaceTable', 'Races') or []
        
        rows = []
        for race in races:
            base_info = {
                'season': race.get('season'),
                'round': race.get('round'),
                'raceName': race.get('raceName'),
                'circuitId': self.safe_get(race, 'Circuit', 'circuitId')
            }
            
            for result in race.get('Results', []):
                driver = result.get('Driver', {})
                constructor = result.get('Constructor', {})
                
                rows.append({
                    **base_info,
                    'driverId': driver.get('driverId'),
                    'driverName': f"{driver.get('givenName')} {driver.get('familyName')}",
                    'constructorId': constructor.get('constructorId'),
                    'position': self._try_int(result.get('position')),
                    'points': self._try_float(result.get('points')),
                    'laps': self._try_int(result.get('laps')),
                    'status': result.get('status')
                })
        
        return pd.DataFrame(rows)

class DriverStandingsProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("driverStandings")
        
    def _build_url(self, year, _=None):
        return f"{self.BASE_URL}{year}/driverStandings.json"

    def transform(self, raw_data):
        standings = self.safe_get(raw_data, 'MRData', 'StandingsTable', 'StandingsLists') or []
        
        rows = []
        for standing in standings:
            season = standing.get('season')
            for driver_standing in standing.get('DriverStandings', []):
                driver = driver_standing.get('Driver', {})
                rows.append({
                    'season': self._try_int(season),
                    'position': self._try_int(driver_standing.get('position')),
                    'points': self._try_float(driver_standing.get('points')),
                    'wins': self._try_int(driver_standing.get('wins')),
                    'driverId': driver.get('driverId'),
                    'constructorId': driver_standing.get('Constructors', [{}])[0].get('constructorId')
                })
                
        return pd.DataFrame(rows)

class ConstructorStandingsProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("constructorStandings")
        
    def _build_url(self, year, _=None):
        return f"{self.BASE_URL}{year}/constructorStandings.json"

    def transform(self, raw_data):
        standings = self.safe_get(raw_data, 'MRData', 'StandingsTable', 'StandingsLists') or []
        
        rows = []
        for standing in standings:
            season = standing.get('season')
            for constructor_standing in standing.get('ConstructorStandings', []):
                constructor = constructor_standing.get('Constructor', {})
                rows.append({
                    'season': self._try_int(season),
                    'position': self._try_int(constructor_standing.get('position')),
                    'points': self._try_float(constructor_standing.get('points')),
                    'wins': self._try_int(constructor_standing.get('wins')),
                    'constructorId': constructor.get('constructorId')
                })
                
        return pd.DataFrame(rows)

class StatusProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("status")
        
    def _build_url(self, year=None, _=None):
        return f"{self.BASE_URL}status.json"

    def transform(self, raw_data):
        status_list = self.safe_get(raw_data, 'MRData', 'StatusTable', 'Status') or []
        
        rows = []
        for status in status_list:
            rows.append({
                'status': status.get('status'),
                'count': self._try_int(status.get('count'))
            })
            
        return pd.DataFrame(rows)

class LapsProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__("laps")
        
    def _build_url(self, year, round):
        return f"{self.BASE_URL}{year}/{round}/laps.json"

    def transform(self, raw_data):
        races = self.safe_get(raw_data, 'MRData', 'RaceTable', 'Races') or []
        
        rows = []
        for race in races:
            for lap in race.get('Laps', []):
                for timing in lap.get('Timings', []):
                    rows.append({
                        'season': self._try_int(race.get('season')),
                        'round': self._try_int(race.get('round')),
                        'lap': self._try_int(lap.get('lap')),
                        'driverId': timing.get('driverId'),
                        'position': self._try_int(timing.get('position')),
                        'time': timing.get('time')
                    })
                    
        return pd.DataFrame(rows)

class ProcessorFactory:
    @staticmethod
    def create_processor(endpoint_type):
        processors = {
            'drivers': DriversProcessor,
            'constructors': ConstructorsProcessor,
            'circuits': CircuitsProcessor,
            'seasons': SeasonsProcessor,
            'results': RaceResultsProcessor,
            'qualifying': QualifyingProcessor,
            'schedules': SchedulesProcessor,
            'driverStandings': DriverStandingsProcessor,
            'constructorStandings': ConstructorStandingsProcessor,
            'status': StatusProcessor,
            'laps': LapsProcessor,
            'pitstops': PitstopsProcessor
        }
        
        processor_class = processors.get(endpoint_type)
        if not processor_class:
            raise ValueError(f"Unknown endpoint type: {endpoint_type}. Valid types: {list(processors.keys())}")
            
        return processor_class()

    @staticmethod
    def get_available_endpoints():
        return [
            'drivers', 'constructors', 'circuits', 'seasons',
            'results', 'qualifying', 'schedules', 'driverStandings',
            'constructorStandings', 'status', 'laps', 'pitstops'
        ] 
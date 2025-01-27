ENDPOINT_SCHEMAS = {
    'drivers': {
        'required_fields': ['driverId', 'givenName', 'familyName'],
        'type_map': {
            'permanentNumber': 'Int64',
            'dateOfBirth': 'datetime64[ns]'
        }
    },
    'constructors': {
        'required_fields': ['constructorId', 'name'],
        'type_map': {
            'established': 'Int64'
        }
    },
    'circuits': {
        'required_fields': ['circuitId', 'circuitName'],
        'type_map': {
            'lat': 'float',
            'long': 'float'
        }
    },
    'seasons': {
        'required_fields': ['season'],
        'type_map': {
            'season': 'int'
        }
    },
    'results': {
        'required_fields': ['season', 'round', 'driverId'],
        'type_map': {
            'season': 'int',
            'round': 'int',
            'grid': 'int',
            'laps': 'int',
            'position': 'int',
            'points': 'float'
        }
    },
    'qualifying': {
        'required_fields': ['season', 'round', 'driverId'],
        'type_map': {
            'season': 'int',
            'round': 'int',
            'position': 'int'
        }
    },
    'schedules': {
        'required_fields': ['season', 'round', 'raceName'],
        'type_map': {
            'season': 'int',
            'round': 'int',
            'date': 'datetime64[ns]'
        }
    },
    'driverStandings': {
        'required_fields': ['season', 'position', 'driverId'],
        'type_map': {
            'season': 'int',
            'position': 'int',
            'points': 'float',
            'wins': 'int'
        }
    },
    'constructorStandings': {
        'required_fields': ['season', 'position', 'constructorId'],
        'type_map': {
            'season': 'int',
            'position': 'int',
            'points': 'float',
            'wins': 'int'
        }
    },
    'status': {
        'required_fields': ['status', 'count'],
        'type_map': {
            'count': 'int'
        }
    },
    'laps': {
        'required_fields': ['season', 'round', 'lap', 'driverId'],
        'type_map': {
            'season': 'int',
            'round': 'int',
            'lap': 'int'
        }
    },
    'pitstops': {
        'required_fields': ['season', 'round', 'driverId', 'stop'],
        'type_map': {
            'season': 'int',
            'round': 'int',
            'lap': 'Int64',
            'stop': 'Int64',
            'duration': 'float'
        }
    }
} 
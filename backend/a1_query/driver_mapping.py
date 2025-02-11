class DriverIDMapper:
    """Maps common driver names/variations to their Ergast API driver IDs"""
    
    DRIVER_MAPPINGS = {
        'max_verstappen': 'max_verstappen',
        'hamilton': 'hamilton',
        'leclerc': 'leclerc',
        'perez': 'perez',
        'carlos_sainz': 'sainz',
        'carlos_sainz_jr': 'sainz',
        'sainz': 'sainz',
        'russell': 'russell',
        'norris': 'norris',
        'piastri': 'piastri',
        'alonso': 'alonso',
        'stroll': 'stroll',
        'gasly': 'gasly',
        'ocon': 'ocon',
        'albon': 'albon',
        'tsunoda': 'tsunoda',
        'bottas': 'bottas',
        'hulkenberg': 'hulkenberg',
        'ricciardo': 'ricciardo',
        'zhou': 'zhou',
        'kevin_magnussen': 'kevin_magnussen',
        'sargeant': 'sargeant',
        'oscar_piastri': 'piastri',
        'yuki_tsunoda': 'tsunoda'
    }

    @classmethod
    def get_ergast_id(cls, driver_id: str) -> str:
        """Convert any driver ID variation to its Ergast API format"""
        return cls.DRIVER_MAPPINGS.get(driver_id.lower(), driver_id) 
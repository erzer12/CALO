class DataLoader:
    """
    Responsible for ingesting raw data from various sources.
    For MVP, this will likely load local JSON/CSV files or hit free public APIs.
    """
    
    def __init__(self):
        # Setup data connections (e.g. file paths, API keys)
        pass

    def load_latest_data(self):
        """
        Fetches the most recent snapshot of city data.
        Returns a dictionary or object containing raw data points.
        """
        # TODO: Implement file reading or API request
        # return { "weather": ..., "311_calls": ... }
        pass

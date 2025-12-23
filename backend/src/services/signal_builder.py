class SignalBuilder:
    """
    Responsible for pre-processing raw data into meaningful 'signals'.
    A signal is a heuristic or statistic that defines a specific aspect of the city.
    
    Example: 
    Raw Data: [Temp 98F, 99F, 100F] -> Signal: "Heatwave Detected"
    """

    def compute_signals(self, raw_data):
        """
        Analyzes raw data and returns a list of high-level signals.
        """
        signals = {}
        
        # 1. Analyze Sanitation Stress (from Complaints)
        complaints = raw_data.get('complaints')
        if not complaints.empty:
            sanitation_complaints = complaints[complaints['category'] == 'sanitation']
            # Simple heuristic: Count complaints in the dataset (MVP style)
            count = len(sanitation_complaints)
            if count >= 3:
                signals['sanitation_stress'] = 'High'
            elif count >= 1:
                signals['sanitation_stress'] = 'Medium'
            else:
                signals['sanitation_stress'] = 'Low'
            
            signals['sanitation_complaint_count'] = int(count)
        
        # 2. Analyze Health Trends
        trends = raw_data.get('trends', {})
        health_warnings = []
        if trends.get('fever udaipur') == 'rising':
            health_warnings.append('Fever cases rising')
        if trends.get('mosquito problem udaipur') == 'rising':
            health_warnings.append('Mosquito activity increasing')
            
        signals['health_early_warning'] = "Detected: " + ", ".join(health_warnings) if health_warnings else "None"

        # 3. Environmental Trigger (Weather)
        weather = raw_data.get('weather', {})
        # Get latest forecast day
        if 'forecast' in weather and len(weather['forecast']) > 0:
            latest = weather['forecast'][0]
            signals['weather_condition'] = latest.get('condition', 'Unknown')
            signals['daily_rainfall'] = f"{latest.get('rainfall_mm', 0)} mm"
            
            if latest.get('rainfall_mm', 0) > 0:
                signals['environmental_trigger'] = 'Active (Rainfall)'
            else:
                signals['environmental_trigger'] = 'Inactive'
        
        # 4. News Context
        news = raw_data.get('news', [])
        signals['recent_news_headlines'] = [item['title'] for item in news[:3]]
        
        return signals

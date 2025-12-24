import pandas as pd
import math

class LogicEngine:
    """
    The Logic Layer of CALO.
    Responsible for:
    1. Normalizing raw signals into a 0.0 - 1.0 scale.
    2. Correlating signals to identify specific 'Risk Scenarios'.
    3. assigning Confidence Scores to avoid the 'Correlation Trap'.
    """

    def normalize_signals(self, raw_data):
        """
        Convert diverse raw data into standardized 0-1 signals.
        """
        signals = {}
        
        # --- 1. Weather Normalization ---
        weather = raw_data.get('weather', {})
        forecast = weather.get('forecast', [{}])[0]
        
        # Rainfall Stress: >50mm is 1.0 (High)
        rainfall = forecast.get('rainfall_mm', 0)
        signals['weather_rainfall_stress'] = min(rainfall / 50.0, 1.0)
        
        # Heat Stress: >45C is 1.0
        temp = forecast.get('temperature_celsius', 25)
        # Assuming 25C is neutral (0.0), 45C is max (1.0)
        if temp:
             signals['weather_heat_stress'] = max(0.0, min((temp - 25) / 20.0, 1.0))
        else:
            signals['weather_heat_stress'] = 0.0
            
        signals['weather_condition_raw'] = forecast.get('condition', 'Unknown')


        # --- 2. Complaints Normalization (Municipal) ---
        complaints_df = raw_data.get('complaints', pd.DataFrame())
        signals['complaints_sanitation_stress'] = 0.0
        signals['complaints_drainage_stress'] = 0.0
        
        if not complaints_df.empty and 'category' in complaints_df.columns:
            # Sanitation
            san_count = len(complaints_df[complaints_df['category'] == 'sanitation'])
            # Threshold: 5 complaints = 1.0
            signals['complaints_sanitation_stress'] = min(san_count / 5.0, 1.0)
            
            # Drainage (simulate/infer from category or description)
            # For this MVP, let's assume 'sanitation' covers drainage broadly, 
            # or look for keywords if description exists.
            # We'll just mirror sanitation for now or check if there are specific keywords
            drain_count = 0 
            # (Simple keyword match if 'description' existed, but we rely on category for now)
            signals['complaints_drainage_stress'] = signals['complaints_sanitation_stress']


        # --- 3. Social Trends Normalization ---
        trends = raw_data.get('trends', {})
        
        # Fever/Health Anxiety
        # "Rising" = 0.8, "High" = 1.0, otherwise 0.2
        fever_status = trends.get('fever udaipur', 'stable').lower()
        if 'spike' in fever_status or 'high' in fever_status:
            signals['social_health_anxiety'] = 1.0
        elif 'rising' in fever_status:
            signals['social_health_anxiety'] = 0.7
        else:
            signals['social_health_anxiety'] = 0.1
            
        # Infrastructure/Traffic Anxiety
        # Check specific traffic tokens if they exist in trends
        signals['social_traffic_anxiety'] = 0.2 # Default low


        return signals

    def evaluate_risk(self, signals):
        """
        Combines normalized signals to detect specific 'Risk Scenarios'.
        Returns a list of active risks and a global confidence score.
        """
        active_risks = []
        
        # --- Scenario A: Vector-Borne Disease Risk (Dengue/Malaria) ---
        # Logic: High Rain (or Humidity) + Sanitation Complaints + Health Anxiety
        # We assume rainfall stress implies humidity/water pooling potential
        disease_score = (
            (0.3 * signals.get('weather_rainfall_stress', 0)) +
            (0.3 * signals.get('complaints_sanitation_stress', 0)) + 
            (0.4 * signals.get('social_health_anxiety', 0))
        )
        
        if disease_score > 0.4: # Threshold for attention
            active_risks.append({
                "id": "BIO_RISK",
                "name": "Vector-Borne Disease Cluster",
                "severity": disease_score, # 0.0 - 1.0
                "contributing_factors": ["Rainfall/Humidity", "Sanitation Complaints", "Health Search Trends"]
            })

        # --- Scenario B: Urban Flash Flood ---
        # Logic: Very High Rain + Drainage Stress
        flood_score = (
            (0.6 * signals.get('weather_rainfall_stress', 0)) +
            (0.4 * signals.get('complaints_drainage_stress', 0))
        )
        
        if flood_score > 0.5:
            active_risks.append({
                "id": "FLOOD_RISK",
                "name": "Urban Flash Flood",
                "severity": flood_score,
                "contributing_factors": ["Heavy Rainfall Forecast", "Drainage Complaints"]
            })

        # --- Scenario C: Heatwave ---
        heat_score = signals.get('weather_heat_stress', 0)
        if heat_score > 0.6:
            active_risks.append({
                "id": "HEAT_RISK",
                "name": "Severe Heatwave",
                "severity": heat_score,
                "contributing_factors": ["High Temperatures"]
            })

        # --- Confidence Calculation ---
        # Simple heuristic: More diverse data sources = higher confidence.
        # Ideally, we verify data freshness here too.
        sources_present = 0
        if signals.get('weather_condition_raw') != 'Unknown': sources_present += 1
        if signals.get('complaints_sanitation_stress') > 0: sources_present += 1 # At least some data
        if signals.get('social_health_anxiety') > 0: sources_present += 1
        
        # Max sources = 3 for this MVP calculation
        confidence_score = min(sources_present / 3.0, 1.0)
        
        # If we rely heavily on one strong signal (like Rain=1.0), confidence is fairly high for that specific event,
        # but for complex inferences (Disease), we need multiple.
        # Let's keep it simple:
        
        return {
            "signals": signals,
            "active_risks": active_risks,
            "confidence_score": confidence_score
        }

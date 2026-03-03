import requests
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting decorator to prevent API throttling."""
    def __init__(self, calls: int = 5, period: int = 60):
        self.calls = calls
        self.period = period
        self.clock = time.time
        self.last_called = [0.0] * calls
        
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = self.clock()
            if self.last_called[-1] >= now - self.period:
                sleep_time = self.period - (now - self.last_called[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
            self.last_called.pop(0)
            self.last_called.append(self.clock())
            return func(*args, **kwargs)
        return wrapper


class DataCollector:
    """Collect live odds and sports data from multiple sources.""" 
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Bet-Titan/1.0'
        })
        
        # API endpoints
        self.ESPN_BASE = 'https://site.api.espn.com/apis/site/v2'
        self.ODDS_API_BASE = 'https://api.the-odds-api.com/v4'
        
    @RateLimiter(calls=5, period=60)
    def fetch_live_odds(self, sport: str, region: str = 'us') -> Dict:
        """
        Fetch live odds from multiple sportsbooks using The Odds API.
        
        Args:
            sport: Sport type (football, basketball, baseball, soccer, etc.)
            region: Region for odds (us, uk, au, etc.)
            
        Returns:
            Dictionary containing odds from multiple sportsbooks
        """
        try:
            api_key = self.config.get('odds_api_key')
            if not api_key:
                logger.warning("Odds API key not configured")
                return {}
            
            url = f'{self.ODDS_API_BASE}/sports/{sport}/odds'
            params = {
                'apiKey': api_key,
                'region': region,
                'markets': 'h2h,spreads,totals',
                'oddsFormat': 'american'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            odds_data = response.json()
            logger.info(f"Fetched live odds for {sport} from {len(odds_data.get('events', []))} events")
            return odds_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching live odds: {e}")
            return {}
    
    @RateLimiter(calls=3, period=60)
    def fetch_sports_data(self, sport: str, league: str = '') -> Dict:
        """
        Fetch sports data (scores, schedules) from ESPN API.
        
        Args:
            sport: Sport type (football, basketball, baseball, etc.)
            league: Specific league (NFL, NBA, MLB, etc.)
            
        Returns:
            Dictionary containing sports data
        """
        try:
            # Map sports to ESPN league codes
            league_map = {
                'nfl': 'nfl',
                'nba': 'nba',
                'nhl': 'nhl',
                'mlb': 'mlb',
                'mls': 'soccer',
                'premier_league': 'soccer'
            }
            
            league_code = league_map.get(league.lower(), sport.lower())
            url = f'{self.ESPN_BASE}/sites/espn/leagues/{league_code}/events'
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched sports data for {league}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching sports data for {league}: {e}")
            return {}
    
    @RateLimiter(calls=5, period=60)
    def fetch_team_stats(self, sport: str, team_id: str) -> Dict:
        """
        Fetch team statistics from ESPN.
        
        Args:
            sport: Sport type
            team_id: ESPN team ID
            
        Returns:
            Dictionary containing team statistics
        """
        try:
            url = f'{self.ESPN_BASE}/sites/espn/teams/{team_id}'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            team_data = response.json()
            logger.info(f"Fetched team stats for team {team_id}")
            return team_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching team stats: {e}")
            return {}
    
    @RateLimiter(calls=3, period=60)
    def fetch_injury_reports(self, sport: str, league: str) -> Dict:
        """
        Fetch injury reports (Note: may require additional API or web scraping).
        
        Args:
            sport: Sport type
            league: League name
            
        Returns:
            Dictionary containing injury data
        """
        try:
            # This would typically require scraping or a dedicated injury API
            # Placeholder implementation
            logger.info(f"Fetching injury reports for {league}")
            return {'injuries': [], 'timestamp': datetime.now().isoformat()}
            
        except Exception as e:
            logger.error(f"Error fetching injury reports: {e}")
            return {}
    
    @RateLimiter(calls=5, period=60)
    def fetch_game_schedule(self, sport: str, league: str, days_ahead: int = 7) -> List[Dict]:
        """
        Fetch upcoming game schedules.
        
        Args:
            sport: Sport type
            league: League name
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming games
        """
        try:
            league_code = league.lower()
            url = f'{self.ESPN_BASE}/sites/espn/leagues/{league_code}/events'
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            logger.info(f"Fetched schedule for {league}: {len(events)} games")
            return events
            
        except requests.RequestException as e:
            logger.error(f"Error fetching game schedule: {e}")
            return []
    
    def fetch_real_time_updates(self, sport: str, update_interval: int = 60) -> None:
        """
        Continuously fetch real-time updates at specified intervals.
        
        Args:
            sport: Sport type to monitor
            update_interval: Seconds between updates
        """
        logger.info(f"Starting real-time updates for {sport} every {update_interval}s")
        
        try:
            while True:
                odds = self.fetch_live_odds(sport)
                schedule = self.fetch_game_schedule(sport, sport.upper())
                
                if odds or schedule:
                    logger.info(f"Real-time update: {len(odds.get('events', []))} odds, {len(schedule)} games")
                    yield {
                        'timestamp': datetime.now().isoformat(),
                        'odds': odds,
                        'schedule': schedule
                    }
                
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            logger.info("Real-time updates stopped by user")
        except Exception as e:
            logger.error(f"Error in real-time updates: {e}")
    
    def get_sportsbook_comparison(self, event_id: str) -> pd.DataFrame:
        """
        Compare odds across multiple sportsbooks for a specific event.
        
        Args:
            event_id: Event ID to compare
            
        Returns:
            DataFrame with sportsbook comparisons
        """
        try:
            # Implementation would aggregate data from fetch_live_odds
            comparison_data = {
                'sportsbook': [],
                'moneyline': [],
                'spread': [],
                'total': []
            }
            
            df = pd.DataFrame(comparison_data)
            logger.info(f"Generated sportsbook comparison for event {event_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error generating sportsbook comparison: {e}")
            return pd.DataFrame()


# Example usage
if __name__ == '__main__':
    config = {
        'odds_api_key': 'YOUR_API_KEY_HERE'
    }
    
    collector = DataCollector(config)
    
    # Fetch live odds
    odds = collector.fetch_live_odds('americanfootball_nfl')
    print(f"Live odds: {len(odds.get('events', []))} events")
    
    # Fetch sports data
    sports_data = collector.fetch_sports_data('nfl', 'NFL')
    print(f"Sports data: {sports_data}")
    
    # Fetch game schedule
    schedule = collector.fetch_game_schedule('nfl', 'nfl')
    print(f"Schedule: {len(schedule)} games")

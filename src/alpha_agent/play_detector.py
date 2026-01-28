"""
Play detector - identify specific trade setups (Golden Staircase, etc.)
"""

import pandas as pd
from src.utils.logging import get_logger

logger = get_logger("alpha_agent.play_detector")


class PlayDetector:
    """Identify specific trade setups based on technical patterns"""
    
    def __init__(self):
        self.logger = logger
    
    def detect_golden_staircase(self, technicals):
        """
        Golden Staircase: Price > 60d SMA > 200d SMA
        Confirms both short-term and long-term trends are up
        
        Args:
            technicals: dict with price, sma_200, sma_60
        
        Returns:
            bool, confidence score (0-100)
        """
        price = technicals.get('price')
        sma_60 = technicals.get('sma_60')
        sma_200 = technicals.get('sma_200')
        
        if pd.isna(price) or pd.isna(sma_60) or pd.isna(sma_200):
            return False, 0.0
        
        # Check the staircase condition
        is_golden_staircase = (price > sma_60) and (sma_60 > sma_200)
        
        if is_golden_staircase:
            # Calculate confidence based on distance from SMAs
            dist_from_60 = (price - sma_60) / sma_60 * 100
            dist_from_200 = (sma_60 - sma_200) / sma_200 * 100
            confidence = min(100, 50 + (dist_from_60 + dist_from_200) / 2)
            
            self.logger.debug(f"✓ Golden Staircase detected (confidence: {confidence:.1f}%)")
            return True, confidence
        
        return False, 0.0
    
    def detect_mean_reversion_bounce(self, technicals, bounce_threshold=0.02):
        """
        Mean Reversion Bounce: Price near 200d SMA but above it
        Institutions often defend the 200d line
        
        Args:
            technicals: dict with price, sma_200
            bounce_threshold: percent above 200d (e.g., 0.02 = 2%)
        
        Returns:
            bool, confidence score (0-100)
        """
        price = technicals.get('price')
        sma_200 = technicals.get('sma_200')
        
        if pd.isna(price) or pd.isna(sma_200):
            return False, 0.0
        
        # Price above 200d but within 2% of it
        percent_above_200 = (price - sma_200) / sma_200
        
        is_bounce = (percent_above_200 > 0) and (percent_above_200 <= bounce_threshold)
        
        if is_bounce:
            confidence = 100 - (percent_above_200 / bounce_threshold * 50)
            self.logger.debug(f"✓ Mean Reversion Bounce detected (confidence: {confidence:.1f}%)")
            return True, confidence
        
        return False, 0.0
    
    def detect_60d_breakout(self, data, volume_threshold=1.2):
        """
        60d Breakout: Price crosses above 60d SMA on high volume
        Signals fresh momentum after consolidation
        
        Args:
            data: pd.DataFrame with full price history and volume
            volume_threshold: ratio of current volume to avg (e.g., 1.2 = 20% above avg)
        
        Returns:
            bool, confidence score (0-100)
        """
        if len(data) < 2:
            return False, 0.0
        
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        price = latest.get('Adj Close')
        sma_60 = latest.get('SMA_60')
        prev_price = previous.get('Adj Close')
        prev_sma_60 = previous.get('SMA_60')
        volume = latest.get('Volume', 0)
        
        if pd.isna(price) or pd.isna(sma_60):
            return False, 0.0
        
        # Check if price crossed above 60d SMA
        crossed_above = (prev_price <= prev_sma_60) and (price > sma_60)
        
        # Check if volume is elevated
        avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
        high_volume = volume > (avg_volume * volume_threshold)
        
        is_breakout = crossed_above and high_volume
        
        if is_breakout:
            self.logger.debug(f"✓ 60d Breakout detected (volume: {volume:.0f})")
            return True, 85.0
        
        return False, 0.0
    
    def classify_play(self, ticker, data, technicals):
        """
        Identify which play (if any) applies to this stock
        
        Args:
            ticker: str, stock ticker
            data: pd.DataFrame with full history
            technicals: dict with current technicals
        
        Returns:
            dict with play name, confidence, and details
        """
        result = {
            "ticker": ticker,
            "play": None,
            "confidence": 0.0,
        }
        
        plays = []
        
        # Check Golden Staircase
        is_gs, conf_gs = self.detect_golden_staircase(technicals)
        if is_gs:
            plays.append(("Golden Staircase", conf_gs))
        
        # Check Mean Reversion Bounce
        is_mrb, conf_mrb = self.detect_mean_reversion_bounce(technicals)
        if is_mrb:
            plays.append(("Mean Reversion Bounce", conf_mrb))
        
        # Check 60d Breakout
        is_bo, conf_bo = self.detect_60d_breakout(data)
        if is_bo:
            plays.append(("60d Breakout", conf_bo))
        
        # Select the play with highest confidence
        if plays:
            best_play = max(plays, key=lambda x: x[1])
            result["play"] = best_play[0]
            result["confidence"] = best_play[1]
        
        return result


if __name__ == "__main__":
    detector = PlayDetector()
    
    test_technicals = {
        "price": 105.0,
        "sma_60": 103.0,
        "sma_200": 100.0,
    }
    
    is_gs, conf = detector.detect_golden_staircase(test_technicals)
    print(f"✓ Golden Staircase: {is_gs} (confidence: {conf:.1f}%)")

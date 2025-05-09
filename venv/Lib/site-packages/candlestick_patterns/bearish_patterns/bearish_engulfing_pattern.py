from ..pattern_detector import PatternDetector


class BearishEngulfingPattern(PatternDetector):
    def search_for_pattern_in_aggs(self) -> bool:
        if all(self.aggs[i].close > self.aggs[i].open for i in range(-8, -2)):
            current_candle = self.aggs[-1]
            # Check for Bearish Engulfing pattern
            if (
                current_candle.close < current_candle.open
                and self.aggs[-2].close > self.aggs[-1].open
                and self.aggs[-2].close > current_candle.open
                and self.aggs[-2].open < current_candle.close
            ):
                return True
        return False

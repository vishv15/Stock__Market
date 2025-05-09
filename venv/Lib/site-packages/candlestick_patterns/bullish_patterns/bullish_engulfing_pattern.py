from ..pattern_detector import PatternDetector


class BullishEngulfingPattern(PatternDetector):
    def search_for_pattern_in_aggs(self) -> bool:
        if (
            self.aggs[-2].close < self.aggs[-2].open
            and self.aggs[-1].close > self.aggs[-1].open
            and self.aggs[-1].close > self.aggs[-2].open
            and self.aggs[-1].open < self.aggs[-2].close
        ):
            return True
        return False

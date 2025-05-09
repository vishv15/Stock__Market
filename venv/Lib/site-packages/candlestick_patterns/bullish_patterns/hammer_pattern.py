from ..pattern_detector import PatternDetector


class HammerPattern(PatternDetector):
    def search_for_pattern_in_aggs(self) -> bool:
        if (
            self.aggs[-1].close > self.aggs[-1].open
            and self.aggs[-1].low < self.aggs[-1].open
            and self.aggs[-1].low - self.aggs[-1].open
            >= (self.aggs[-1].close - self.aggs[-1].open) / 2
        ):
            return True

        return False

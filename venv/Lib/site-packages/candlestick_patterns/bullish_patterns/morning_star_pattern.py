from ..pattern_detector import PatternDetector


class MorningStarPattern(PatternDetector):
    def search_for_pattern_in_aggs(self) -> bool:
        if (
            self.aggs[-3].close > self.aggs[-3].open
            and self.aggs[-2].close < self.aggs[-2].open
            and self.aggs[-1].close > self.aggs[-1].open
            and self.aggs[-1].close > ((self.aggs[-3].open + self.aggs[-3].close) / 2)
            and self.aggs[-2].close < self.aggs[-3].open
        ):
            return True

        return False

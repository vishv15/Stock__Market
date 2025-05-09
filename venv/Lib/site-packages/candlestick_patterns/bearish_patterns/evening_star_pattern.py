from ..pattern_detector import PatternDetector


class EveningStarPattern(PatternDetector):
    def search_for_pattern_in_aggs(self) -> bool:
        if (
            self.aggs[-3].high > self.aggs[-4].high
            and self.aggs[-3].low > self.aggs[-4].low
            and self.aggs[-2].high > self.aggs[-3].high
            and self.aggs[-2].low > self.aggs[-3].low
            and self.aggs[-1].high > self.aggs[-2].high
            and self.aggs[-1].low > self.aggs[-2].low
        ):
            # Check for Evening Star pattern
            if (
                self.aggs[-3].close < self.aggs[-3].open
                and self.aggs[-2].close > self.aggs[-2].open
                and self.aggs[-1].close < self.aggs[-1].open
                and self.aggs[-1].open > self.aggs[-2].close
                and self.aggs[-1].close > self.aggs[-3].open
            ):
                return True
        return False

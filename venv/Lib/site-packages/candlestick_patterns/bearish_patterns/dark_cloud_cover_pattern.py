from ..pattern_detector import PatternDetector


class DarkCloudCoverPattern(PatternDetector):
    def search_for_pattern_in_aggs(self) -> bool:
        if (
            self.aggs[-2].high > self.aggs[-3].high
            and self.aggs[-2].low > self.aggs[-3].low
            and self.aggs[-1].high > self.aggs[-2].high
            and self.aggs[-1].low > self.aggs[-2].low
        ):
            # Check for Dark Cloud Cover pattern
            if (
                self.aggs[-2].close > self.aggs[-2].open
                and self.aggs[-1].open > self.aggs[-2].close
                and self.aggs[-1].close
                < ((self.aggs[-2].open + self.aggs[-2].close) / 2)
            ):
                return True
        return False

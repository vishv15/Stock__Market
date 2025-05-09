from typing import List

from polygon.rest.models.aggs import Agg

from src.candlestick_patterns.bearish_patterns import (
    BearishEngulfingPattern,
    DarkCloudCoverPattern,
    EveningStarPattern,
)

from ..bullish_patterns import (
    BullishEngulfingPattern,
    HammerPattern,
    MorningStarPattern,
)
from ..utils.constants import PatternName


class Candlesticks:
    def __init__(self, aggs: List[Agg]):
        self.aggs = aggs

    PATTERN_MAP = {
        PatternName.BULLISH_ENGULFING: BullishEngulfingPattern,
        PatternName.HAMMER: HammerPattern,
        PatternName.MORNING_STAR: MorningStarPattern,
        PatternName.BEARISH_ENGULFING: BearishEngulfingPattern,
        PatternName.DARK_CLOUD_COVER: DarkCloudCoverPattern,
        PatternName.EVENING_STAR: EveningStarPattern,
    }

    def search_for_patterns(
        self, pattern_names: List[PatternName]
    ) -> List[PatternName]:
        found_patterns: List[PatternName] = []
        for pattern_name in pattern_names:
            PatternClass = self.PATTERN_MAP[pattern_name]
            pattern_found = PatternClass(self.aggs).search_for_pattern_in_aggs()
            if pattern_found:
                found_patterns.append(pattern_name)
        return found_patterns

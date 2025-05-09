from abc import ABC, abstractmethod
from typing import List

from polygon.rest.models.aggs import Agg


class PatternDetector(ABC):
    def __init__(self, aggs: List[Agg]):
        self._assert_sorted_dates_ascending(aggs)
        self.aggs = aggs

    def _assert_sorted_dates_ascending(self, aggs: List[Agg]):
        assert aggs[0].timestamp < aggs[1].timestamp

    @abstractmethod
    def search_for_pattern_in_aggs(self) -> bool:
        raise NotImplementedError
